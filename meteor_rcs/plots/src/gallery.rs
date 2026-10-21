//! Same density, sampled colormap and log-height convention as Rustplotlib's
//! dimant_oppenheim gallery example at dd3238b. No change to DO quadrature.
use crate::{figure, support::dimant::Density};
use anyhow::Result;
use rustplotlib::*;
use std::{
    f64::consts::{PI, TAU},
    path::Path,
};

pub fn build(out: &Path) -> Result<serde_json::Value> {
    let model = Density::new(64);
    let xs: Vec<_> = (0..=160).map(|i| -5. + 25. * i as f64 / 160.).collect();
    let ys: Vec<_> = (0..=128).map(|i| -10. + 20. * i as f64 / 128.).collect();
    let heights: Vec<_> = ys
        .iter()
        .flat_map(|&r| {
            let model = &model;
            xs.iter().map(move |&z| {
                if z.hypot(r) > 20. {
                    f64::NAN
                } else {
                    (8. * PI * model.at(z, r)).log10()
                }
            })
        })
        .collect();
    let colors = || {
        ColorMap::listed(
            include_bytes!("support/dimant_colormap.rgb")
                .chunks_exact(3)
                .map(|p| [p[0] as f64 / 255., p[1] as f64 / 255., p[2] as f64 / 255.])
                .collect(),
        )
    };
    std::fs::create_dir_all(out.join("do_turntable"))?;
    std::fs::create_dir_all(out.join("do_physical"))?;
    // An actual spatial isodensity surface, F_DO=0.05, is separate from the
    // gallery height map. Radius is solved, never inferred from plot height.
    let theta: Vec<_> = (0..=72).map(|i| PI * i as f64 / 72.).collect();
    let radial: Vec<_> = theta
        .iter()
        .map(|&t| {
            let (mut lo, mut hi) = (1e-5, 100.);
            for _ in 0..55 {
                let r = (lo + hi) / 2.;
                if model.at(r * t.cos(), r * t.sin()) > 0.05 {
                    lo = r
                } else {
                    hi = r
                }
            }
            (lo + hi) / 2.
        })
        .collect();
    for frame in 0..48 {
        let angle = -0.65 + TAU * frame as f64 / 47.;
        let mut f = figure(160., 100.);
        f.raster_dpi = 150.;
        let sc = f.scale(Scale::new([-3., 4.], Normalization::Linear, colors()?)?);
        let mut s = Surface::new(xs.clone(), ys.clone(), heights.clone(), [-3., 4.], sc)?;
        s.yaw = angle;
        s.fit_to_view = false;
        let mut p = Panel::new(
            Rect::new(5., 8., 150., 78.),
            Axes::new([0., 1.], [0., 1.], "", ""),
        );
        p.axes = None;
        // Axes use the identical camera as the surface; captions stay outside
        // the moving geometry and are checked on every exported frame.
        let origin = [-5., -10., -3.];
        for (tip, color) in [([20., -10., -3.], "#245774"), ([-5., 10., -3.], "#267369")] {
            let projected: Vec<_> = [origin, tip]
                .map(|v| {
                    let v = s.project(v);
                    [v[0], 1. - v[1]]
                })
                .to_vec();
            p.push(Layer::Line(Line::new(projected, color)));
        }
        p.push(Layer::Surface(s));
        let labels = vec![Label::new(
            r"Blue: $z/\lambda_T$; green: $r_\perp/\lambda_T$; height: log density",
            80.,
            94.,
        )];
        f.check_annotations(&p, &labels)?;
        f.labels = labels;
        f.panels.push(p);
        f.save(out.join(format!("do_turntable/{frame:03}.png")))?;

        let mut f = figure(160., 100.);
        f.raster_dpi = 150.;
        let sc = f.scale(Scale::new(
            [0., 1.],
            Normalization::Linear,
            ColorMap::new(vec![[0.78, 0.89, 0.86], [0.10, 0.40, 0.36]])?,
        )?);
        // Orthographic camera around the trajectory axis, preserving distances.
        let project = |p: [f64; 3]| {
            let x = angle.cos() * p[0] - angle.sin() * p[1];
            let depth = angle.sin() * p[0] + angle.cos() * p[1];
            (
                [0.5 + x / 20., 0.5 + (p[2] * 0.85 - depth * 0.35) / 20.],
                depth + p[2] * 0.35,
            )
        };
        let mut faces = vec![];
        for j in 0..72 {
            for i in 0..64 {
                let mut poly = vec![];
                let mut depth = 0.;
                for (j, i) in [(j, i), (j + 1, i), (j + 1, i + 1), (j, i + 1)] {
                    let t = theta[j];
                    let phi = TAU * i as f64 / 64.;
                    let r = radial[j];
                    let (xy, d) = project([
                        r * t.cos(),
                        r * t.sin() * phi.cos(),
                        r * t.sin() * phi.sin(),
                    ]);
                    poly.push(xy);
                    depth += d;
                }
                faces.push((depth, poly, 0.35 + 0.6 * (TAU * i as f64 / 64.).cos().abs()));
            }
        }
        faces.sort_by(|a, b| a.0.total_cmp(&b.0));
        let mut p = Panel::new(
            Rect::new(5., 8., 150., 78.),
            Axes::new([0., 1.], [0., 1.], "", ""),
        );
        p.axes = None;
        p.push(Layer::PolygonMesh(PolygonMesh::new(
            faces.iter().map(|v| v.1.clone()).collect(),
            faces.iter().map(|v| v.2).collect(),
            sc,
        )?));
        let axis: Vec<_> = [[-6., 0., 0.], [10., 0., 0.]]
            .map(|v| project(v).0)
            .to_vec();
        p.push(Layer::Line(Line::new(axis, "#245774")));
        let grain = project([0., 0., 0.]).0;
        let mut marker = Line::new(
            (0..=32)
                .map(|i| {
                    let t = TAU * i as f64 / 32.;
                    [grain[0] + 0.006 * t.cos(), grain[1] + 0.006 * t.sin()]
                })
                .collect(),
            "#9b4825",
        );
        marker.fill = Some("#9b4825".into());
        marker.fill_opacity = 1.;
        p.push(Layer::Line(marker));
        let labels = vec![Label::new(
            r"Physical space: $n_e/n_*=0.05$; gold: grain; blue: trajectory",
            80.,
            94.,
        )];
        f.check_annotations(&p, &labels)?;
        f.labels = labels;
        f.panels.push(p);
        f.save(out.join(format!("do_physical/{frame:03}.png")))?;
    }
    let checks: Vec<_> = [[0., 1.], [1., 1.], [-1., 1.], [0.01, 0.01], [15., 8.]]
        .into_iter()
        .map(|[z, r]| [z, r, model.at(z, r)])
        .collect();
    Ok(
        serde_json::json!({"checks":checks,"z":xs,"r":ys,"log_density":heights.iter().map(|v|if v.is_finite(){Some(*v)}else{None}).collect::<Vec<_>>(),"theta":theta,"radius":radial}),
    )
}
