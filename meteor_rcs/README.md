# Meteor head echo: comet dust to radar cross section

`../meteor_head_rcs.py` is a native `manim_slides.Slide` presentation. Its opening
follows a roughly 100-micrometre grain from 55P/Tempel--Tuttle, through long-term
orbital evolution and an illustrative Earth encounter, to sputtering, heating,
Langmuir evaporation, hyperthermal ionization, and the plasma cloud seen by MAARSY.

The derivation then connects the thermal ablation equations to Si primary
electron production, production line density, Dimant--Oppenheim normalization
and morphology, cold collisional/magnetized plasma current, Yee FDTD, the
induced-current radiation integral, and polarized monostatic RCS. It concludes
with convergence, beam selection, and the inverse problem of constraining the
physical meteoroid parameters from a calibrated echo and trajectory.

The DO sequence explains each factor in production line density, the atmosphere
and grain rest frames, velocity-dependent collision lengths, dimensionless
coordinates, the reference amplitude, and the axisymmetric reconstruction in
three dimensions. Both axial and transverse distances scale with the same
thermal collision length. The reference amplitude is not a peak density or a
unit-integral normalization.

## Build from the repository root

```bash
conda run -n base python -m meteor_rcs.prepare_assets
conda run -n base manim-slides render -r 1920,1080 --fps 30 \
  meteor_head_rcs.py MeteorHeadRCS
conda run -n base python export_web.py web MeteorHeadRCS
conda run -n base python -m meteor_rcs.inspect_slides
```

Open `web/meteor-head-rcs/index.html` through an HTTP server. Arrow keys advance;
each video holds its completed frame. Source filenames and provenance footers
are never rendered; they are retained in code comments and data metadata.
Equations use MathTex and prose uses the
shared TeX-backed `Text` renderer. The web export includes the repository's
final-slide navigation guard. No separate PPTX is required.
The slides use a white background, dark text, and dark blue, green, and rust
accents to match the native Rustplotlib figures.

## Native Rustplotlib figures

All quantitative plots are constructed and rendered by
[`jvierine/rustplotlib`](https://github.com/jvierine/rustplotlib), pinned to
`6c41f00ffcafc76d7850c885f63afd29ad097556` in `plots/Cargo.toml`.
`plots/src/main.rs` owns axes, labels, layout, colors, and SVG/PNG exports.
Manim imports the PNGs; the matching SVGs remain available for vector reuse.
Python prepares numerical arrays and passes them over stdin to the small Rust
program. HDF5 remains the saved scientific data format. Matplotlib is not used.
The first build needs Cargo, network access to fetch dependencies, and LaTeX
with dvisvgm; subsequent builds use the Cargo and glyph caches.

## Data and interpretation

The small bundled `inputs.h5` contains exact subsets of saved calculations;
**building this presentation never launches ablation or FDTD jobs**:

- `orbit_55p`: the actual Jupiter-plus-Poynting--Robertson secular track from
  [the 55P demo](https://juha.no/55p/). Its orbit-averaged model smooths close
  encounters. Its mass/area is 0.1 kg/m², equivalent to a 100-micrometre sphere
  at 1500 kg/m³. The final three-lap Earth encounter is a separate illustrative
  Kepler orbit whose phase is chosen to intersect Earth; it is not a computed
  impact from the secular integration. PR evolution occurs over many orbits,
  not suddenly during the final three laps.
- `trajectory`: native Rust thermal ablation of a **different illustrative
  material case**: 100 micrometres, initial 49.684 km/s, 45-degree entry, bulk
  density 3300 kg/m³, archived MSIS 2.1 atmosphere. This is not a recovered
  history of the narrative Leonid grain. The thermal model uses 50-u effective
  vapor mass; the ionization/DO chain represents all lost mass as Si (28.085 u).
- `cutoff`: completed native FDTD sensitivity results for 500 micrometres,
  initial 23.16 km/s, fixed height 92.5 km, 2.80-cm grid. They do **not** establish
  a universal converged plasma cutoff. The stopped 512-collision-length case
  contributes no result.

The original dataset paths, model attributes and SHA-256 source fingerprints
are retained. `prepare_assets.py` recalculates DO morphology with the standalone
`do_density.py` and creates `data.h5` and the figures. `data.h5` records arrays,
input/source hashes and source text. Both files use HDF5 rather than CSV.

`do_density.py` is copied from the author's standalone function in
[`jvierine/fdtd`](https://github.com/jvierine/fdtd/blob/main/examples/dimant_oppenheim.py),
retaining the attribution and the comparison with MetAblate's implementation.
This presentation makes no modifications to either ablation or Maxwell solver.

Early sputtering is shown in the physical narrative; it is **not included in
the archived thermal ablation calculation**. Evaporated atoms retain the
meteoroid's bulk velocity plus a thermal spread in the atmosphere frame. An
energetic collision *can* ionize; the primary probability is not unity.

The cloud illustration and the field/current animation are explicitly
schematic. The DO morphology, archived thermal trajectory and native cutoff
curve are quantitative. The ideal DO origin is singular; finite-grid density
caps and support tapers are numerical/model choices. A production line density
is not a surviving trail line density. RCS is not total scattering cross
section, and an RHCP channel is not the sum over receive polarizations.

## Primary references

- [55P/Tempel--Tuttle, NASA Science](https://science.nasa.gov/solar-system/comets/55p-tempel-tuttle/).
- [Fitzpatrick, solar radiation and interplanetary dust](https://farside.ph.utexas.edu/teaching/celestial/Celestial/node95.html),
  used by the author's [55P secular orbit demo](https://github.com/jvierine/55p-tempel-tuttle-animation).
- [Vondrak et al. (2008), chemical ablation](https://doi.org/10.5194/acp-8-7015-2008),
  with its [corrigendum](https://acp.copernicus.org/articles/8/7015/2008/acp-8-7015-2008-corrigendum.pdf).
- [Hill et al. (2005), thermal grain model](https://doi.org/10.1051/0004-6361:20053053).
- [Jones (1997), primary ionization](https://doi.org/10.1093/mnras/288.4.995), Eq. 33 and Table 1.
- [Dimant and Oppenheim (2017), Part 1](https://doi.org/10.1002/2017JA023960)
  and [Part 2](https://doi.org/10.1002/2017JA023963), especially Eqs. 45--48.
- [Marshall and Close (2015), plasma FDTD](https://doi.org/10.1002/2015JA021238).
- [Marshall, Brown and Close (2017), plasma distributions and RCS](https://doi.org/10.1016/j.pss.2016.12.011).
- [Huyghebaert et al. (2026), MAARSY initial heights and neutral density](https://doi.org/10.5194/amt-19-4277-2026).

The Maxwell solver follows the cold-plasma scattering framework of Marshall and
Close, using an independent Rust implementation with analytic incident fields
and an induced-current far-field integral.
