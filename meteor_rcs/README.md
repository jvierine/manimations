# Meteor head echo: comet dust to radar cross section

`../meteor_head_rcs.py` is a native `manim_slides.Slide` presentation. Its opening
follows a roughly 100-micrometre grain from 55P/Tempel--Tuttle, through long-term
orbital evolution and an illustrative Earth encounter, to sputtering, heating,
Langmuir evaporation, hyperthermal ionization, and the plasma cloud seen by MAARSY.
An animated two-frame photon diagram spells out Poynting--Robertson drag:
thermal emission is isotropic in the grain frame, but carries forward momentum
in the Sun frame. Its deliberately exaggerated aberration illustrates the
tangential recoil, not a relativistic meteoroid speed.
The radiation-pressure sequence distinguishes the radial force from P--R drag,
defines the force ratio `beta_rad`, and derives the release-energy criterion
`beta_rad >= r_release/(2*a_parent)` for negligible ejection speed. The familiar
one-half threshold applies to a circular parent orbit. Optical efficiency is
size and composition dependent; ever-smaller grains are not automatically
easier to eject. No new dust-orbit calculation is presented.

Nine animated slides introduce solid-grain collisions before the surviving
grain's final Earth encounter. They distinguish cratering and fragmentation
from catastrophic disruption, derive impact energy per target mass, relative
velocity, geometric swept-volume rates, a phase-space destruction-rate integral,
and survival under cumulative collision exposure. The illustrative 100/10
micrometre target/projectile pair at 10 km/s gives 50 kJ/kg of available
projectile energy per target mass; no universal grain-strength threshold or
55P collision lifetime is claimed. These solid impacts are distinct from the
atomic collision lengths used in the later plasma section.

The sequence introduces Grün et al. (1985), the scaled-lifetime dynamical
population model of Nesvorný et al. (2011), the collision-cascade/comet-splitting
model of Rigley and Wyatt (2022), and the three-dimensional collisional grooming
method of Stark and Kuchner (2009) as applied to Jupiter-family comet dust by
Pokorný et al. (2024). The latter's inferred strength is conditional
on its source population and outcome prescription; it is not a direct 55P
lifetime measurement. All five papers have clickable citations. Animations
of collision outcomes, encounter geometry and ensemble survival are explanatory
schematics, not a new collisional simulation or a digitized model curve.
The evaporation cartoon shrinks the solid grain as successive neutral-atom
shells leave. The radar illustration uses all 433 actual antenna positions
from the meteor repository, bundled in `maarsy_array.h5`, and labels the cloud's
effective radar-scattering diameter as `D_eff`. That schematic size is not a
physical boundary or a density-support cutoff.

The thermal derivation builds from projected grain area and atmospheric mass
flux to heating power, then adds radiation and latent-heat loss at separate
presenter-controlled steps. Equations use mathematical symbols throughout;
their definitions and units accompany the relevant term. Langmuir evaporation
and the coupled trajectory equations have separate graphical explanations.
The free molecular discussion defines `Kn = lambda_nn/D` and the molecular
speed ratio, distinguishing the ambient air--air mean free path from the DO
collision lengths. Momentum and energy balances separately derive
`F_drag = Gamma*rho_A*A*v^2` and `P_heat = Lambda*rho_A*A*v^3/2`.
The drag convention is `Gamma = C_D/2`; an unshielded hypersonic sphere has
approximately `Gamma = 1`, or `C_D = 2`, when reemission speeds are small
relative to the incoming stream. Surface reflection, thermal accommodation,
and vapour shielding can change these coefficients. This explanation does not
change the archived solver or its results. The introductory radar parameters
give frequency and wavelength; the wave period is omitted there.

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
Scientific citations on the radiation-pressure and free molecular slides, and
all bibliography entries, are clickable in the HTML deck after each animation
finishes. Links open the papers in a new tab. The exporter aligns accessible
link areas with the rendered citations, including letterboxing when resized.
Equations use MathTex and prose uses the
shared TeX-backed `Text` renderer. The web export includes the repository's
final-slide navigation guard. No separate PPTX is required.
The slides use a white background, dark text, and dark blue, green, and rust
accents to match the native Rustplotlib figures.

## Native Rustplotlib figures

All quantitative plots are constructed and rendered by
[`jvierine/rustplotlib`](https://github.com/jvierine/rustplotlib), pinned to
`2da4af7f2a2274b875608bf435e4fa3b368ab98d` in `plots/Cargo.toml`.
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
- [Burns, Lamy and Soter (1979), solar radiation forces](https://doi.org/10.1016/0019-1035(79)90050-2).
- [Bariselli et al. (2020), rarefied meteor entry](https://doi.org/10.1093/mnras/stz3559).
- [Loth et al. (2021), sphere drag and its free molecular limit](https://doi.org/10.2514/1.J060153).
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

## Expanded density and electromagnetic derivations

The deck introduces the Dimant--Oppenheim kinetic model before its function.
The normalization sequence starts with the outgoing half-Maxwellian surface
flux, eliminates `a^2 n0` using the atom production rate, and follows Part 2
Eq. 45 through `Gion = beta*sigma_c/(4*pi)` and `q = beta*Ndot/v` to `nstar`.
The ion-to-air mass factor is traced through the recoil speed and the
velocity-space integral in Part 2 Eqs. 3 and 10--11. The kinetic transport
picture makes clear why ions born along earlier trajectories contribute to a
local density. The numerical prefactor belongs to that published kinetic
solution; it is not a geometric cloud-volume estimate.

The rotating log-height surface reproduces the Rustplotlib gallery's density
function, sampling domain and colormap. Plot height is explicitly log density.
A separate rotating physical isodensity surface (`ne/nstar = 0.05`) is obtained
by solving the same function for radius at each polar angle and revolving it
about the trajectory axis. It is an illustrative density level, not a plasma
edge or FDTD cutoff. `Figure::check_annotations` checks captions against the
projected geometry in all 48 frames of each animation. Camera-independent
caption space avoids labels moving through the plotted surface.

The 2D density map retains dimensionless axes and adds metre axes. Their
calibration uses archived MSIS neutral density at **100 km altitude**, a
50 km/s meteoroid and a 2000 K grain. The corresponding thermal collision
length is about 0.1045 m; the fast atom's atmospheric path is about 6.790 m.
Altitude alone cannot determine the DO thermal collision length.

The Yee-grid animation explains field staggering in space and time. CPML is
spelled out as convolutional perfectly matched layer, with an outgoing-pulse
schematic and its derivative-memory update. The electron response is derived
from the Lorentz force and linear collisional momentum loss, then converted
to current using `J = -ne*e*ue`. A separate restoring-field animation explains
the plasma-frequency scale. The dielectric follows from `exp(-i*omega*t)`,
`J = sigma*E`, `J = dP/dt`, and `D = epsilon0*E + P`. The constant collision
frequency in the archived example is identified as an assumption.

Additional references:

- [Bronshten (1983), Physics of Meteoric Phenomena](https://doi.org/10.1007/978-94-009-7222-3).
- [Sugar et al. (2018), section 5.3](https://doi.org/10.1002/2018JA025265), adoption of the empirical collision law.
- [Yee (1966)](https://doi.org/10.1109/TAP.1966.1138693), staggered Maxwell discretization.
- [Roden and Gedney (2000)](https://doi.org/10.1002/1098-2760(20001205)27:5%3C334::AID-MOP14%3E3.0.CO;2-A), convolution PML.

## Lecture structure

Four sections follow the grain's journey: orbital evolution, atmospheric
entry and ablation, ionization and plasma morphology, then radar scattering
and received power. Three presenter-controlled interludes separate them.
The MAARSY illustration opens the plasma section. The ablation section ends
with four altitude-profile panels using six saved 45-degree MetAblate cases
from sabmod, bundled in ablation_profiles.h5. These 1e-8 kg cometary cases
are labelled separately from the 100-micrometre stony Rust-chain example.
No Matplotlib images or new ablation integrations are used.

The Maxwell sequence states why field feedback matters, then derives the
leapfrog updates from Faraday and Ampere-Maxwell laws. It defines the discrete
curl, time index, fields and constants before discussing time-step limits.
The factor 0.7 is identified as a solver margin. The radar equation is built
from incident flux, return flux, and effective aperture, with a clickable
MIT Lincoln Laboratory radar-course reference.

The Poynting--Robertson section now also derives its tangential force: zero
net emitted photon momentum in the grain frame transforms to outgoing
momentum P_emit*v_t/c^2 per second in the Sun frame. For an ideal absorbing
grain in radiative equilibrium, P_emit is approximately P_abs to the order
retained. Incoming radial sunlight supplies no tangential momentum, leaving
the negative recoil. This states the assumptions behind the displayed drag
formula rather than presenting it as a universal optical-scattering law.
