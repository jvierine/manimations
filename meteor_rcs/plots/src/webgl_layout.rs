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
    #[serde(default)]
    yaw_start: Option<f64>,
    #[serde(default)]
    yaw_span: Option<f64>,
    #[serde(default)]
    pitch: Option<f64>,
    #[serde(default)]
    view_width: Option<f64>,
    #[serde(default)]
    gutter_left: Option<f64>,
    #[serde(default)]
    frames: Option<usize>,
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
    // pixels in the fixed right-hand gutter, with additional validator padding.
    for (name, scene) in scenes {
        let height = name == "height";
        let view_width = scene.view_width.unwrap_or(153.6);
        let gutter_left = scene.gutter_left.unwrap_or(156.);
        let frames = scene.frames.unwrap_or(360);
        let gutter = Label::new(
            format!(r"\rule{{{}mm}}{{88mm}}", 192. - gutter_left),
            (gutter_left + 192.) / 2.,
            45.,
        );
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
        points.extend(if name == "ionization" {
            vec![[0., 0., 0.]]
        } else if height {
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
        for frame in 0..=frames {
            let t = frame as f64 / frames as f64;
            let q = t * (scene.camera_targets.len() - 1) as f64;
            let i = (q.floor() as usize).min(scene.camera_targets.len() - 2);
            let u = q - i as f64;
            let target: [f64; 3] = std::array::from_fn(|k| {
                scene.camera_targets[i][k] * (1. - u) + scene.camera_targets[i + 1][k] * u
            });
            let yaw = scene.yaw_start.unwrap_or(if height { -0.85 } else { 0.85 })
                + scene.yaw_span.unwrap_or(std::f64::consts::TAU)
                    * if name == "ionization" {
                        (t / 0.8).min(1.)
                    } else {
                        t
                    };
            let pitch: f64 = scene.pitch.unwrap_or(if height { 0.42 } else { 0.28 });
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
                    (0.5 + 0.5 * dot(right) * 2.4142137 / (view_width / 90. * z)) * view_width,
                    (0.5 - 0.5 * dot(up) * 2.4142137 / z) * 90.,
                ];
                for k in 0..2 {
                    lo[k] = lo[k].min(xy[k]);
                    hi[k] = hi[k].max(xy[k]);
                }
            }
            ensure!(
                lo[0] > 0. && hi[0] < view_width && lo[1] > 0. && hi[1] < 90.,
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
            "{name}: {} camera frames clear annotations and canvas bounds; injected collision rejected",
            frames + 1
        );
    }
    Ok(())
}
