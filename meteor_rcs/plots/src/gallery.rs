//! Same density, sampled colormap and log-height convention as Rustplotlib's
//! dimant_oppenheim gallery example at dd3238b. No change to DO quadrature.
use crate::support::dimant::Density;
use anyhow::Result;
use std::{f64::consts::PI, path::Path};

pub fn build(_out: &Path) -> Result<serde_json::Value> {
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
    let checks: Vec<_> = [[0., 1.], [1., 1.], [-1., 1.], [0.01, 0.01], [15., 8.]]
        .into_iter()
        .map(|[z, r]| [z, r, model.at(z, r)])
        .collect();
    Ok(
        serde_json::json!({"checks":checks,"z":xs,"r":ys,"log_density":heights.iter().map(|v|if v.is_finite(){Some(*v)}else{None}).collect::<Vec<_>>(),"theta":theta,"radius":radial}),
    )
}
