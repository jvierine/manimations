//! Check each recorded camera frame with Rustplotlib's annotation validator.
//! The entire annotation gutter is reserved conservatively; it encloses every
//! fixed canvas/TeX label. Projected mesh and axis bounds enclose all triangles.
use anyhow::{Result, ensure};
use rustplotlib::*;
use serde::Deserialize;
use std::{collections::BTreeMap, path::Path};

#[derive(Deserialize)]
#[serde(rename_all = "camelCase")]
struct Scene {
    xyz: Vec<f64>,
    bounds: [f64; 6],
    scale: [f64; 3],
    camera_distance: f64,
    camera_targets: Vec<[f64; 3]>,
}

pub fn check(path: &Path) -> Result<()> {
    let scenes: BTreeMap<String, Scene> = serde_json::from_reader(std::fs::File::open(path)?)?;
    let mut fig = Figure::new(IntendedUse::Custom {
        width_mm: 192.,
        font_pt: 12.,
    });
    fig.height_mm = 90.;
    fig.latex.cache = Path::new(env!("CARGO_MANIFEST_DIR")).join(".latex-cache");
    let sc = fig.scale(Scale::new(
        [0., 1.],
        Normalization::Linear,
        ColorMap::sequential(),
    )?);
    // Millimetres map to ten output pixels. A measured TeX rule reserves all
    // pixels x=1560..1920, y=105..895, with additional validator padding.
    let gutter = Label::new(r"\rule{36mm}{79mm}", 174., 50.);
    for (name, scene) in scenes {
        let height = name == "height";
        let radius = (0..3)
            .map(|k| ((scene.bounds[2 * k + 1] - scene.bounds[2 * k]) * scene.scale[k]).powi(2))
            .sum::<f64>()
            .sqrt()
            / 2.;
        let mut points: Vec<[f64; 3]> = scene
            .xyz
            .chunks_exact(3)
            .map(|p| [p[0], p[1], p[2]])
            .collect();
        points.extend(if height {
            vec![
                [-5., -10., -3.],
                [20., -10., -3.],
                [-5., 10., -3.],
                [-5., -10., 2.7],
            ]
        } else {
            vec![[-2., 0., 0.], [8., 0., 0.], [0., 4.5, 0.], [0., 0., 4.5]]
        });
        let mut rejected_control = false;
        for frame in 0..=360 {
            let t = frame as f64 / 360.;
            let q = t * (scene.camera_targets.len() - 1) as f64;
            let i = (q.floor() as usize).min(scene.camera_targets.len() - 2);
            let u = q - i as f64;
            let target: [f64; 3] = std::array::from_fn(|k| {
                scene.camera_targets[i][k] * (1. - u) + scene.camera_targets[i + 1][k] * u
            });
            let yaw = (if height { -0.85 } else { 0.85 }) + std::f64::consts::TAU * t;
            let pitch: f64 = if height { 0.42 } else { 0.28 };
            let front = [
                yaw.cos() * pitch.cos(),
                yaw.sin() * pitch.cos(),
                pitch.sin(),
            ];
            let right = [-yaw.sin(), yaw.cos(), 0.];
            let up = [
                -yaw.cos() * pitch.sin(),
                -yaw.sin() * pitch.sin(),
                pitch.cos(),
            ];
            let mut lo = [f64::INFINITY; 2];
            let mut hi = [f64::NEG_INFINITY; 2];
            for p in &points {
                let v: [f64; 3] =
                    std::array::from_fn(|k| (p[k] - target[k]) * scene.scale[k] / radius);
                let dot = |a: [f64; 3]| (0..3).map(|k| v[k] * a[k]).sum::<f64>();
                let z = scene.camera_distance - dot(front);
                ensure!(z > 0., "{name} frame {frame}: geometry behind camera");
                let xy = [
                    (0.5 + 0.5 * dot(right) * 2.4142137 / (1536. / 900. * z)) * 153.6,
                    (0.5 - 0.5 * dot(up) * 2.4142137 / z) * 90.,
                ];
                for k in 0..2 {
                    lo[k] = lo[k].min(xy[k]);
                    hi[k] = hi[k].max(xy[k]);
                }
            }
            ensure!(
                lo[0] > 0. && hi[0] < 153.6 && lo[1] > 0. && hi[1] < 90.,
                "{name} frame {frame}: clipped geometry"
            );
            let mut panel = Panel::new(
                Rect::new(0., 0., 192., 90.),
                Axes::new([0., 192.], [90., 0.], "", ""),
            );
            panel.push(Layer::PolygonMesh(PolygonMesh::new(
                vec![vec![
                    [lo[0], lo[1]],
                    [hi[0], lo[1]],
                    [hi[0], hi[1]],
                    [lo[0], hi[1]],
                ]],
                vec![0.5],
                sc,
            )?));
            fig.check_annotations(&panel, std::slice::from_ref(&gutter))?;
            if frame == 0 {
                let colliding =
                    Label::new("$r_\\perp$", (lo[0] + hi[0]) / 2., (lo[1] + hi[1]) / 2.);
                rejected_control = fig.check_annotations(&panel, &[colliding]).is_err();
            }
        }
        ensure!(
            rejected_control,
            "{name}: collision positive control was not rejected"
        );
        println!(
            "{name}: 361 camera frames clear annotations and canvas bounds; injected collision rejected"
        );
    }
    Ok(())
}
