//! Yee fields and electron current, unsplit convolutional PML.
//! SI inputs; internally tau=c*t, h=Z0*H and j=J/(eps0*c).
//! Physical model: Marshall & Close (2015), doi:10.1002/2015JA021238.
//! We drive the current with an analytic incident wave and evolve scattered
//! fields. The radiation integral of the induced current replaces surface NTF.
use mpi::{collective::SystemOperation, topology::SimpleCommunicator, traits::*};
use rayon::prelude::*;
use serde::{Deserialize, Serialize};
use std::{
    env, fs,
    io::{BufWriter, Read, Seek, SeekFrom, Write},
    time::Instant,
};

const C: f64 = 299_792_458.0;
const EPS0: f64 = 8.854_187_818_8e-12;
const ME: f64 = 9.109_383_713_9e-31;
const QE: f64 = 1.602_176_634e-19;
const PI: f64 = std::f64::consts::PI;
type Vector = [f64; 3];
type Complex = [f64; 2];
type Fields = [Vec<f64>; 3];

struct Grid {
    n: usize,
    dx: f64,
    dt: f64,
    x_start: usize,
    x_count: usize,
}

#[derive(Deserialize)]
struct Config {
    n: usize,
    dx_m: f64,
    pml_cells: usize,
    frequency_hz: f64,
    collision_rate_s1: f64,
    magnetic_field_t: Vector,
    polarization: String,
    support_radius_m: f64,
    periods: f64,
    density_file: String,
    output_file: String,
    threads: usize,
    #[serde(default)]
    field_frames: usize,
    #[serde(default)]
    field_file: Option<String>,
}

#[derive(Serialize)]
struct ResultData {
    frequency_hz: f64,
    collision_rate_s1: f64,
    magnetic_field_t: Vector,
    polarization: String,
    pml_cells: usize,
    support_radius_m: f64,
    periods: f64,
    angle_rad: Vec<f64>,
    rcs_m2: Vec<f64>,
    backscatter_rhcp_lhcp_m2: [f64; 2],
    // Fourier current radiation amplitudes, transverse to each direction.
    radiation_amplitude: Vec<[Complex; 3]>,
    incident_fourier: [Complex; 3],
    n: usize,
    dx_m: f64,
    dt_s: f64,
    steps: usize,
    active_edges: usize,
    elapsed_s: f64,
    threads: usize,
    mpi_ranks: usize,
    field_times_s: Vec<f64>,
}

struct Edge {
    component: usize,
    index: usize,
    position: Vector,
    wp: f64,
    rhs: f64,
    next: f64,
    fourier: Complex,
}

#[derive(Clone, Copy)]
struct Pml {
    a: f64,
    b: f64,
}

fn dot(a: Vector, b: Vector) -> f64 {
    a.iter().zip(b).map(|(x, y)| x * y).sum()
}

/// Each rank owns a contiguous x slab plus one ghost plane on either side.
/// Sendrecv avoids ordering deadlocks. End-rank ghost planes are vacuum/PEC;
/// the ring exchange used here is communication only, not periodic physics.
fn exchange_halos(fields: &mut Fields, grid: &Grid, world: &SimpleCommunicator) {
    if world.size() == 1 {
        return;
    }
    let rank = world.rank();
    let left = world.process_at_rank((rank + world.size() - 1) % world.size());
    let right = world.process_at_rank((rank + 1) % world.size());
    let plane = grid.n * grid.n;
    for field in fields {
        let (lo, rest) = field.split_at_mut(plane);
        let (owned, hi) = rest.split_at_mut(grid.x_count * plane);
        mpi::point_to_point::send_receive_into(&owned[..plane], &left, hi, &right);
        mpi::point_to_point::send_receive_into(&owned[owned.len() - plane..], &right, lo, &left);
        if rank == 0 {
            lo.fill(0.0);
        }
        if rank == world.size() - 1 {
            hi.fill(0.0);
        }
    }
}
/// Lorentz operator on energy-normalized edge current p=j/wp.
/// Adjacent components are gathered with mutually adjoint four-edge averages.
/// The discrete operator is skew-adjoint, so the CN update preserves energy.
fn gyro_at(field: &Fields, index: usize, component: usize, n: usize, gyro: Vector) -> f64 {
    let strides = [n * n, n, 1];
    let average = |other: usize| {
        let a = strides[component];
        let b = strides[other];
        (field[other][index]
            + field[other][index + a]
            + field[other][index - b]
            + field[other][index + a - b])
            / 4.0
    };
    let a = (component + 1) % 3;
    let b = (component + 2) % 3;
    gyro[a] * average(b) - gyro[b] * average(a)
}

fn pml_coefficients(n: usize, count: usize, dx: f64, dt: f64, shift: f64, k: f64) -> Vec<Pml> {
    (0..n)
        .map(|i| {
            let x = i as f64 + shift;
            let depth =
                ((count as f64 - x).max(x - (n - count) as f64) / count as f64).clamp(0.0, 1.0);
            if depth == 0.0 {
                return Pml { a: 0.0, b: 1.0 };
            }
            // Cubic conductivity; target amplitude reflection 1e-8. kappa=1.
            let sigma = -4.0 * (1e-8_f64).ln() / (2.0 * count as f64 * dx) * depth.powi(3);
            let alpha = 0.05 * k * (1.0 - depth);
            let b = (-(sigma + alpha) * dt).exp();
            Pml {
                a: sigma * (b - 1.0) / (sigma + alpha),
                b,
            }
        })
        .collect()
}

fn stretched(derivative: f64, memory: &mut f64, coefficient: Pml) -> f64 {
    if coefficient.a == 0.0 {
        return derivative;
    }
    *memory = coefficient.b * *memory + coefficient.a * derivative;
    derivative + *memory
}

/// Forward curl for H at half steps; backward curl for E at integer steps.
/// Structure-of-arrays storage; independent contiguous x slabs run in parallel.
fn advance(
    fields: &mut Fields,
    memory: &mut [[Vec<f64>; 2]; 3],
    source: &Fields,
    pml: &[Pml],
    grid: &Grid,
    forward: bool,
) {
    let Grid {
        n,
        dx,
        dt,
        x_start,
        x_count,
    } = *grid;
    let strides = [n * n, n, 1];
    let sign = if forward { -1.0 } else { 1.0 };
    for component in 0..3 {
        let axis_a = (component + 1) % 3;
        let axis_b = (component + 2) % 3;
        let [ma, mb] = &mut memory[component];
        fields[component]
            .par_chunks_mut(n * n)
            .zip(ma.par_chunks_mut(n * n))
            .zip(mb.par_chunks_mut(n * n))
            .enumerate()
            .for_each(|(i, ((output, pa), pb))| {
                if i == 0 || i > x_count {
                    return;
                }
                let global_i = x_start + i - 1;
                if global_i == 0 || global_i == n - 1 {
                    return;
                }
                for j in 1..n - 1 {
                    for z in 1..n - 1 {
                        let local = j * n + z;
                        let index = i * n * n + local;
                        let coordinates = [global_i, j, z];
                        let derivative = |field: usize, axis: usize| {
                            let stride = strides[axis];
                            if forward {
                                (source[field][index + stride] - source[field][index]) / dx
                            } else {
                                (source[field][index] - source[field][index - stride]) / dx
                            }
                        };
                        let da = stretched(
                            derivative(axis_b, axis_a),
                            &mut pa[local],
                            pml[coordinates[axis_a]],
                        );
                        let db = stretched(
                            derivative(axis_a, axis_b),
                            &mut pb[local],
                            pml[coordinates[axis_b]],
                        );
                        output[local] += sign * dt * (da - db);
                    }
                }
            });
    }
}

fn incident(tau: f64, x: f64, k: f64, sigma: f64, launch: f64, polarization: &str) -> Vector {
    let u = tau - x - launch;
    let envelope = (-0.5 * (u / sigma).powi(2)).exp();
    let (sine, cosine) = (k * u).sin_cos();
    match polarization {
        "linear" => [0.0, 0.0, envelope * cosine],
        "lhcp" => [
            0.0,
            envelope * sine / 2.0_f64.sqrt(),
            envelope * cosine / 2.0_f64.sqrt(),
        ],
        "rhcp" => [
            0.0,
            -envelope * sine / 2.0_f64.sqrt(),
            envelope * cosine / 2.0_f64.sqrt(),
        ],
        _ => unreachable!(),
    }
}

fn norm2(z: Complex) -> f64 {
    z[0] * z[0] + z[1] * z[1]
}

fn run(
    config: Config,
    world: &SimpleCommunicator,
) -> Result<ResultData, Box<dyn std::error::Error>> {
    let n = config.n;
    let dx = config.dx_m;
    if n < 8
        || config.pml_cells < 3
        || 2 * config.pml_cells + 4 >= n
        || !dx.is_finite()
        || dx <= 0.0
        || !config.frequency_hz.is_finite()
        || config.frequency_hz <= 0.0
        || !config.collision_rate_s1.is_finite()
        || config.collision_rate_s1 < 0.0
        || !config.periods.is_finite()
        || config.periods <= 0.0
        || !config.support_radius_m.is_finite()
        || config.support_radius_m <= 0.0
        || config.magnetic_field_t.iter().any(|x| !x.is_finite())
        || !["lhcp", "rhcp", "linear"].contains(&config.polarization.as_str())
    {
        return Err("Invalid grid, physical inputs or polarization".into());
    }
    let global_size = n.checked_pow(3).ok_or("Grid size overflow")?;
    let rank = world.rank() as usize;
    let ranks = world.size() as usize;
    if ranks > n {
        return Err("More MPI ranks than x planes".into());
    }
    let x_start = n * rank / ranks;
    let x_count = n * (rank + 1) / ranks - x_start;
    let size = (x_count + 2) * n * n;
    let mut input = fs::File::open(&config.density_file)?;
    if input.metadata()?.len()
        != global_size
            .checked_mul(24)
            .ok_or("Grid byte count overflow")? as u64
    {
        return Err("Density file must contain 3*n^3 little-endian f64 Yee-edge densities".into());
    }
    let mut edges = Vec::new();
    // Independent slab reads avoid replicating the complete density on ranks.
    let mut bytes = vec![0_u8; x_count * n * n * 8];
    for component in 0..3 {
        input.seek(SeekFrom::Start(
            ((component * global_size + x_start * n * n) * 8) as u64,
        ))?;
        input.read_exact(&mut bytes)?;
        for (flat, bytes) in bytes.chunks_exact(8).enumerate() {
            let density = f64::from_le_bytes(bytes.try_into()?);
            if !density.is_finite() || density < 0.0 {
                return Err("Invalid electron density".into());
            }
            if density == 0.0 {
                continue;
            }
            let indices = [x_start + flat / (n * n), (flat / n) % n, flat % n];
            if indices
                .iter()
                .any(|&q| q <= config.pml_cells || q >= n - config.pml_cells - 2)
            {
                return Err("Plasma overlaps PML or outer boundary".into());
            }
            let position = std::array::from_fn(|q| {
                (indices[q] as f64 + if q == component { 0.5 } else { 0.0 } - n as f64 / 2.0) * dx
            });
            edges.push(Edge {
                component,
                index: flat + n * n,
                position,
                wp: (density * QE * QE / (EPS0 * ME * C * C)).sqrt(),
                rhs: 0.0,
                next: 0.0,
                fourier: [0.0; 2],
            });
        }
    }
    drop(bytes);
    let mut active_edges = 0_u64;
    world.all_reduce_into(
        &(edges.len() as u64),
        &mut active_edges,
        SystemOperation::sum(),
    );
    let gyro = config.magnetic_field_t.map(|b| QE * b / (ME * C));
    let local_wp2 = edges
        .iter()
        .map(|edge| edge.wp * edge.wp)
        .fold(0.0, f64::max);
    let mut max_wp2 = 0.0_f64;
    world.all_reduce_into(&local_wp2, &mut max_wp2, SystemOperation::max());
    let dt = (0.5 * dx).min(0.7 / (max_wp2 + dot(gyro, gyro)).sqrt());
    let k = 2.0 * PI * config.frequency_hz / C;
    let wavelength = 2.0 * PI / k;
    let sigma = wavelength;
    let launch = 6.0 * sigma + config.support_radius_m;
    let steps = ((launch + 6.0 * sigma + config.support_radius_m + config.periods * wavelength)
        / dt)
        .ceil() as usize;
    let integer_pml = pml_coefficients(n, config.pml_cells, dx, dt, 0.0, k);
    let half_pml = pml_coefficients(n, config.pml_cells, dx, dt, 0.5, k);
    let mut electric: Fields = std::array::from_fn(|_| vec![0.0; size]);
    let mut magnetic: Fields = std::array::from_fn(|_| vec![0.0; size]);
    let mut epml = std::array::from_fn(|_| std::array::from_fn(|_| vec![0.0; size]));
    let mut hpml = std::array::from_fn(|_| std::array::from_fn(|_| vec![0.0; size]));
    let mut incident_fourier = [[0.0; 2]; 3];
    let mut incident_plane = vec![[0.0; 3]; n];
    let mut plasma: Fields = std::array::from_fn(|_| vec![0.0; size]);
    let damping = 0.5 * dt * config.collision_rate_s1 / C;
    let magnetized = dot(gyro, gyro) > 0.0;
    let clock = Instant::now();
    let mut last_report = Instant::now();
    let grid = Grid {
        n,
        dx,
        dt,
        x_start,
        x_count,
    };
    // Record total Ez and physical Jz on the y=0 plane, at their staggered times.
    // The analytic incident wave is added by the plotting script.
    let first = ((launch - 0.5 * n as f64 * dx - 4.0 * sigma).max(0.0) / dt) as usize;
    let last = (((launch + 0.5 * n as f64 * dx + 4.0 * sigma + 2.0 * wavelength) / dt) as usize)
        .min(steps - 1);
    let mut frame_steps: Vec<usize> = (0..config.field_frames)
        .map(|i| first + (last - first) * i / config.field_frames.saturating_sub(1).max(1))
        .collect();
    frame_steps.dedup();
    let mut field_times_s = Vec::new();
    let mut field_writer = if rank == 0 && !frame_steps.is_empty() {
        Some(BufWriter::new(fs::File::create(
            config.field_file.as_ref().ok_or("Missing field_file")?,
        )?))
    } else {
        None
    };
    let mut frame_index = 0;
    if rank == 0 {
        eprintln!(
            "Rust Yee/CPML: {n}^3 cells, {active_edges} current edges, {steps} steps, {ranks} MPI ranks x {} threads",
            rayon::current_num_threads()
        );
    }
    for step in 0..steps {
        let tau = step as f64 * dt;
        advance(&mut magnetic, &mut hpml, &electric, &half_pml, &grid, true);
        exchange_halos(&mut magnetic, &grid, world);
        let (sin_e, cos_e) = (k * tau).sin_cos();
        let reference = incident(tau, 0.0, k, sigma, launch, &config.polarization);
        for q in 0..3 {
            incident_fourier[q][0] += dt * reference[q] * cos_e;
            incident_fourier[q][1] += dt * reference[q] * sin_e;
        }
        let (sin_j, cos_j) = (k * (tau + 0.5 * dt)).sin_cos();
        // A plane wave depends only on x. Evaluate it once per x plane,
        // rather than repeating exp/sin/cos at every plasma-current site.
        for (i, wave) in incident_plane.iter_mut().enumerate() {
            let x = (i as f64 - n as f64 / 2.0) * dx;
            *wave = incident(tau, x, k, sigma, launch, &config.polarization);
        }
        edges.par_iter_mut().for_each(|edge| {
            let q = edge.component;
            let external = incident_plane[x_start + edge.index / (n * n) - 1][q];
            let total = external + electric[q][edge.index];
            edge.rhs = (1.0 - damping) * plasma[q][edge.index] + dt * edge.wp * total;
            if magnetized {
                edge.rhs += 0.5 * dt * gyro_at(&plasma, edge.index, q, n, gyro);
            }
        });
        // Matrix-free trapezoidal Lorentz solve. dt*|Omega| <= 0.7 makes
        // this contraction fast (typically five iterations for Earth's B).
        let mut converged = !magnetized;
        for _ in 0..32 {
            let (error, scale) = edges
                .par_iter_mut()
                .map(|edge| {
                    edge.next = (edge.rhs
                        + if magnetized {
                            0.5 * dt * gyro_at(&plasma, edge.index, edge.component, n, gyro)
                        } else {
                            0.0
                        })
                        / (1.0 + damping);
                    (
                        (edge.next - plasma[edge.component][edge.index]).abs(),
                        edge.next.abs(),
                    )
                })
                .reduce(|| (0.0_f64, 0.0_f64), |a, b| (a.0.max(b.0), a.1.max(b.1)));
            for edge in &edges {
                plasma[edge.component][edge.index] = edge.next;
            }
            if magnetized {
                exchange_halos(&mut plasma, &grid, world);
            }
            let mut global_norm = [0.0_f64; 2];
            world.all_reduce_into(&[error, scale], &mut global_norm, SystemOperation::max());
            if !magnetized || global_norm[0] <= 1e-12 * global_norm[1].max(1e-30) {
                converged = true;
                break;
            }
        }
        if !converged {
            return Err("Lorentz iteration did not converge".into());
        }
        edges.par_iter_mut().for_each(|edge| {
            let j = edge.wp * edge.next;
            edge.fourier[0] += dt * j * cos_j;
            edge.fourier[1] += dt * j * sin_j;
        });
        advance(
            &mut electric,
            &mut epml,
            &magnetic,
            &integer_pml,
            &grid,
            false,
        );
        for edge in &edges {
            electric[edge.component][edge.index] -= dt * edge.wp * edge.next;
        }
        exchange_halos(&mut electric, &grid, world);
        if frame_index < frame_steps.len() && step == frame_steps[frame_index] {
            let mut slice = vec![0.0_f32; n * n];
            for i in 0..x_count {
                for z in 0..n {
                    slice[(x_start + i) * n + z] =
                        (electric[2][(i + 1) * n * n + (n / 2) * n + z] + incident(tau+dt,(x_start as f64+i as f64-n as f64/2.)*dx,k,sigma,launch,&config.polarization)[2]) as f32;
                }
            }
            let root = world.process_at_rank(0);
            if rank == 0 {
                let mut complete = vec![0.0_f32; n * n];
                root.reduce_into_root(&slice[..], &mut complete[..], SystemOperation::sum());
                let writer = field_writer.as_mut().unwrap();
                for value in complete {
                    writer.write_all(&value.to_le_bytes())?;
                }
            } else {
                root.reduce_into(&slice[..], SystemOperation::sum());
            }
            // J is sampled at n+1/2; normalized j=J/(eps0*c).
            let mut current_slice=vec![0.0_f32;n*n];
            for edge in &edges {
                if edge.component==2 && (edge.index/n)%n==n/2 {
                    let ix=edge.index/(n*n)-1+x_start;
                    let iz=edge.index%n;
                    current_slice[ix*n+iz]=(edge.wp*edge.next*EPS0*C) as f32;
                }
            }
            let root=world.process_at_rank(0);
            if rank==0 {
                let mut complete=vec![0.0_f32;n*n];
                root.reduce_into_root(&current_slice[..],&mut complete[..],SystemOperation::sum());
                for value in complete { field_writer.as_mut().unwrap().write_all(&value.to_le_bytes())?; }
            } else { root.reduce_into(&current_slice[..],SystemOperation::sum()); }
            field_times_s.push((step + 1) as f64 * dt / C);
            frame_index += 1;
        }
        if step % 100 == 0 {
            let unstable = edges
                .iter()
                .any(|edge| !edge.next.is_finite() || (edge.wp * edge.next).abs() > 1e15)
                as i32;
            let mut global_unstable = 0_i32;
            world.all_reduce_into(&unstable, &mut global_unstable, SystemOperation::max());
            if global_unstable != 0 {
                return Err("Nonfinite or unstable plasma current".into());
            }
            if rank == 0 && last_report.elapsed().as_secs() >= 10 {
                eprintln!(
                    "{:.0}% ({:.1} s)",
                    100.0 * step as f64 / steps as f64,
                    clock.elapsed().as_secs_f64()
                );
                last_report = Instant::now();
            }
        }
    }
    if let Some(writer) = field_writer.as_mut() {
        writer.flush()?;
    }
    let intensity: f64 = incident_fourier.iter().map(|&v| norm2(v)).sum();
    if !intensity.is_finite() || intensity <= 0.0 {
        return Err("Invalid incident Fourier normalization".into());
    }
    // Exact far-zone radiation integral of the self-consistent induced current.
    // Includes multiple scattering through the time evolution; not a Born sum.
    // sigma = k^2/(4*pi*|E_inc_hat|^2) |P_transverse integral(j_hat dV)|^2.
    let factor = k * k / (4.0 * PI * intensity);
    let angle_rad: Vec<f64> = (0..37).map(|i| PI * i as f64 / 36.0).collect();
    let mut radiation_amplitude: Vec<[Complex; 3]> = angle_rad
        .iter()
        .map(|&angle| {
            let direction = [angle.cos(), 0.0, angle.sin()];
            let mut amplitude = [[0.0; 2]; 3];
            for edge in &edges {
                let (sine, cosine) = (-k * dot(direction, edge.position)).sin_cos();
                let q = edge.component;
                let [re, im] = edge.fourier;
                amplitude[q][0] += dx.powi(3) * (re * cosine - im * sine);
                amplitude[q][1] += dx.powi(3) * (re * sine + im * cosine);
            }
            let longitudinal: Complex = std::array::from_fn(|part| {
                direction
                    .iter()
                    .zip(amplitude)
                    .map(|(d, a)| d * a[part])
                    .sum()
            });
            for (d, a) in direction.iter().zip(&mut amplitude) {
                a[0] -= d * longitudinal[0];
                a[1] -= d * longitudinal[1];
            }
            amplitude
        })
        .collect();
    let local_amplitude: Vec<f64> = radiation_amplitude
        .iter()
        .flat_map(|a| a.iter().flat_map(|z| z.iter()))
        .copied()
        .collect();
    let mut global_amplitude = vec![0.0_f64; local_amplitude.len()];
    world.all_reduce_into(
        &local_amplitude[..],
        &mut global_amplitude[..],
        SystemOperation::sum(),
    );
    for (a, values) in radiation_amplitude
        .iter_mut()
        .zip(global_amplitude.chunks_exact(6))
    {
        for (z, pair) in a.iter_mut().zip(values.chunks_exact(2)) {
            z.copy_from_slice(pair);
        }
    }
    let mut elapsed_s = 0.0_f64;
    world.all_reduce_into(
        &clock.elapsed().as_secs_f64(),
        &mut elapsed_s,
        SystemOperation::max(),
    );
    let rcs_m2 = radiation_amplitude
        .iter()
        .map(|a| factor * a.iter().map(|&v| norm2(v)).sum::<f64>())
        .collect();
    let back = radiation_amplitude.last().unwrap();
    // Backward RHCP analyser (0,i,1)/sqrt(2); LHCP (0,-i,1)/sqrt(2).
    let rhcp = [
        (back[2][0] + back[1][1]) / 2.0_f64.sqrt(),
        (back[2][1] - back[1][0]) / 2.0_f64.sqrt(),
    ];
    let lhcp = [
        (back[2][0] - back[1][1]) / 2.0_f64.sqrt(),
        (back[2][1] + back[1][0]) / 2.0_f64.sqrt(),
    ];
    Ok(ResultData {
        frequency_hz: config.frequency_hz,
        collision_rate_s1: config.collision_rate_s1,
        magnetic_field_t: config.magnetic_field_t,
        polarization: config.polarization,
        pml_cells: config.pml_cells,
        support_radius_m: config.support_radius_m,
        periods: config.periods,
        angle_rad,
        rcs_m2,
        backscatter_rhcp_lhcp_m2: [factor * norm2(rhcp), factor * norm2(lhcp)],
        radiation_amplitude,
        incident_fourier,
        n,
        dx_m: dx,
        dt_s: dt / C,
        steps,
        active_edges: active_edges as usize,
        elapsed_s,
        threads: rayon::current_num_threads(),
        mpi_ranks: ranks,
        field_times_s,
    })
}

fn main() {
    let (universe, provided) = mpi::initialize_with_threading(mpi::Threading::Funneled)
        .expect("MPI initialization failed");
    let world = universe.world();
    if provided < mpi::Threading::Funneled {
        world.abort(1);
    }
    let execute = || -> Result<(), Box<dyn std::error::Error>> {
        let filename = env::args().nth(1).ok_or("Usage: meteor-fdtd config.json")?;
        let config: Config = serde_json::from_slice(&fs::read(filename)?)?;
        let output_file = config.output_file.clone();
        rayon::ThreadPoolBuilder::new()
            .num_threads(config.threads)
            .build_global()?;
        let result = run(config, &world)?;
        if result.rcs_m2.iter().any(|x| !x.is_finite()) {
            return Err("Nonfinite RCS".into());
        }
        if world.rank() == 0 {
            fs::write(output_file, serde_json::to_vec_pretty(&result)?)?;
        }
        Ok(())
    };
    if let Err(error) = execute() {
        eprintln!("MPI rank {}: {error}", world.rank());
        world.abort(1);
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn lorentz_operator_is_skew_adjoint() {
        let n = 8;
        let mut p: Fields = std::array::from_fn(|_| vec![0.0; n * n * n]);
        for (q, field) in p.iter_mut().enumerate() {
            for i in 2..n - 2 {
                for j in 2..n - 2 {
                    for k in 2..n - 2 {
                        let index = i * n * n + j * n + k;
                        field[index] = ((index + q) as f64).sin();
                    }
                }
            }
        }
        let gyro = [0.3, -0.1, 0.5];
        let mut work = 0.0;
        for (q, field) in p.iter().enumerate() {
            for i in 1..n - 1 {
                for j in 1..n - 1 {
                    for k in 1..n - 1 {
                        let index = i * n * n + j * n + k;
                        work += field[index] * gyro_at(&p, index, q, n, gyro);
                    }
                }
            }
        }
        assert!(work.abs() < 1e-13);
    }
}
