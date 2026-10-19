//! Native plot builder for the Manim Slides deck. Python supplies HDF5 arrays
//! over stdin; Rustplotlib owns all layout, axes, typography, and rendering.
use anyhow::Result;
use rustplotlib::*;
use serde::Deserialize;
use std::{io, path::PathBuf};

#[derive(Deserialize)]
struct Data {
    altitude: Vec<f64>,
    loss: Vec<f64>,
    temperature: Vec<f64>,
    speeds: Vec<f64>,
    beta: Vec<f64>,
    z: Vec<f64>,
    r: Vec<f64>,
    density: Vec<Option<f64>>,
    radius: Vec<f64>,
    rcs: Vec<f64>,
}

fn figure(width: f64, height: f64) -> Figure {
    let mut f = Figure::new(IntendedUse::Custom { width_mm: width, font_pt: 12.0 });
    f.height_mm = height;
    f.raster_dpi = 240.0;
    f.latex.cache = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join(".latex-cache");
    f
}

fn curve(x: &[f64], y: &[f64], color: &str) -> Layer {
    let mut line = Line::new(x.iter().zip(y).map(|(&a, &b)| [a, b]).collect(), color);
    line.width_pt = 1.7;
    Layer::Line(line)
}

fn edges(centers: &[f64]) -> Vec<f64> {
    let mut out = vec![centers[0] - (centers[1] - centers[0]) / 2.0];
    out.extend(centers.windows(2).map(|p| (p[0] + p[1]) / 2.0));
    let n = centers.len();
    out.push(centers[n-1] + (centers[n-1] - centers[n-2]) / 2.0);
    out
}

fn main() -> Result<()> {
    let d: Data = serde_json::from_reader(io::stdin())?;
    let out = PathBuf::from(std::env::args().nth(1).expect("output directory"));
    std::fs::create_dir_all(&out)?;
    let save = |f: Figure, name: &str| -> Result<()> {
        for ext in ["svg", "png"] { f.save(out.join(format!("{name}.{ext}")))?; }
        Ok(())
    };

    let mut f = figure(195.0, 88.0);
    for (rect, values, label, color) in [
        (Rect::new(23., 8., 66., 59.), &d.loss, r"$-\dot m\ [10^{-9}\,\mathrm{kg\,s^{-1}}]$", "#9b4825"),
        (Rect::new(119., 8., 66., 59.), &d.temperature, r"$T_M\ [\mathrm K]$", "#267369"),
    ] {
        let divisor = if label.contains("dot") { 1e-9 } else { 1.0 };
        let max = values.iter().copied().fold(0., f64::max);
        let x: Vec<_> = values.iter().map(|v| if *v > 0.03*max { *v/divisor } else { f64::NAN }).collect();
        let mut axes = Axes::new([0., max/divisor*1.05], [95., 115.], label, "Altitude [km]");
        axes.yticks = vec![95., 100., 105., 110., 115.];
        axes.xticks = if divisor < 1.0 { vec![0., 3., 6.] } else { vec![0., 1000., 2000.] };
        let mut p = Panel::new(rect, axes);
        p.push(curve(&x, &d.altitude, color));
        f.panels.push(p);
    }
    save(f, "ablation")?;

    let mut f = figure(170., 88.);
    let mut a = Axes::new([8., 80.], [0., 1.], "Instantaneous speed [km/s]", r"$\beta_{\mathrm{Si}}$");
    a.xticks = vec![10., 20., 40., 60., 80.];
    a.yticks = vec![0., 0.25, 0.5, 0.75, 1.];
    let mut p = Panel::new(Rect::new(21., 7., 139., 60.), a);
    p.push(curve(&d.speeds, &d.beta, "#9b4825"));
    f.panels.push(p);
    save(f, "ionization")?;

    let mut f = figure(175., 111.);
    let sc = f.scale(Scale::new([0.001, 30.], Normalization::Log, ColorMap::sequential())?);
    let mut a = Axes::new([-2., 6.], [-3., 3.], r"$z/\lambda_T$ (positive behind)", r"$r_\perp/\lambda_T$ (signed slice)");
    a.xticks = vec![-2., 0., 2., 4., 6.];
    a.yticks = vec![-3., 0., 3.];
    let mut p = Panel::new(Rect::new(24., 6., 104., 78.), a);
    p.pcolormesh(edges(&d.z), edges(&d.r), d.density.iter().map(|v| v.unwrap_or(f64::NAN)).collect(), sc)?;
    f.panels.push(p);
    f.colorbars.push(Colorbar::new(Rect::new(137., 6., 3., 78.), sc, r"$n_e/n_\star$", vec![0.001, 0.1, 10.]));
    save(f, "density")?;

    let mut f = figure(180., 89.);
    let mut a = Axes::new([0., 10.], [-38., -21.], "Plasma support radius [m]", "Native RCS [dBsm]");
    a.xticks = vec![0., 2., 4., 6., 8., 10.];
    a.yticks = vec![-36., -32., -28., -24.];
    let mut p = Panel::new(Rect::new(24., 7., 146., 60.), a);
    let db: Vec<_> = d.rcs.iter().map(|v| 10.*v.log10()).collect();
    p.push(curve(&d.radius, &db, "#9b4825"));
    f.panels.push(p);
    save(f, "cutoff")?;
    println!("Rustplotlib wrote four native SVG/PNG figures.");
    Ok(())
}
