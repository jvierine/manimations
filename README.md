# Manim Slides teaching decks

This repository contains source code and configuration only. Images, movies,
scientific datasets, browser scene arrays, and compiled WebAssembly are excluded
from Git, including its history. The published decks and their build inputs live
on juha.no.

Restore the checksum-verified build inputs after cloning:

```bash
conda run -n base python fetch_assets.py
```

`asset_manifest.json` pins the external archive and every input by SHA-256.
The render scripts fetch missing inputs automatically. Generated media stays
local or is published to juha.no; never add it to Git or Git LFS.

## Meteor head echo: comet dust to RCS

[`meteor_head_rcs.py`](meteor_head_rcs.py) follows a 100-micrometre grain from
55P/Tempel--Tuttle to atmospheric entry, sputtering, Langmuir evaporation,
ionization, and detection by MAARSY. It derives the complete
ablation → line density → Dimant--Oppenheim → FDTD → polarized RCS calculation,
then calculates received power and SNR. See [build commands, data and assumptions](meteor_rcs/README.md).
All quantitative figures use native [Rustplotlib](https://github.com/jvierine/rustplotlib)
exports; the external scientific arrays retain their provenance in HDF5.

```bash
conda run -n base python -m meteor_rcs.prepare_assets
conda run -n base manim-slides render -r 1920,1080 --fps 30 meteor_head_rcs.py MeteorHeadRCS
conda run -n base python export_web.py web MeteorHeadRCS
```

Live browser deck: <https://juha.no/space/meteor-head-rcs/>.
Script provenance stays in code comments and HDF5 metadata; it is never rendered.

## Planck law to radio noise

This Manim presentation derives the single-mode radio noise formula from
Planck spectral radiance. The bridge uses the throughput of one spatial mode,
\(A\Omega=\lambda^2\), and explicitly selects one of the two polarizations
included in \(B_\nu\).

The opening scene uses the pyGDSM `HaslamSkyModel` at 408 MHz. Regenerate the
kelvin map and its native-resolution HEALPix HDF5 data product with:

```bash
conda run -n base python make_haslam_map.py
```

The generator writes `assets/haslam_408mhz.png` and
`assets/haslam_408mhz.h5`. The HDF5 dataset is named
`brightness_temperature_k`; its attributes record the unit, HEALPix ordering,
Galactic coordinate system, frequency, resolution, model, and generating
script.

## Render

Manim is installed in the base conda environment.

```bash
# Fast preview
conda run -n base manim -pql planck_to_ktb.py PlanckToKTB

# Final 1920 x 1080 render
conda run -n base manim -pqh planck_to_ktb.py PlanckToKTB
```

Keep source-script provenance in code comments and data metadata, never in
rendered slides or figures.

## Web presentations

All three presentations inherit from `manim_slides.Slide`, so their scene
boundaries become interactive browser slide breaks. Render all slide media at
1920 x 1080 and 30 fps with:

```bash
./render_all_slides.sh
```

Export a self-contained web presentation with:

```bash
conda run -n base manim-slides convert --folder slides --offline \
  FriisVoyager web/friis-voyager/index.html
```

The exported page uses RevealJS and standard MP4 video. Viewers need only a
web browser; they do not need Python, Manim, or `manim-slides`.

For production exports, use the wrapper that checks every slide's final frame,
creates review images, adds the navigation guard, and names videos by content
to prevent stale browser caching:

```bash
conda run -n base python export_web.py /tmp/lecture-web PlanckToKTB FriisVoyager
```

Publish only each deck's `index.html` and `index_assets/`; the `qa-*` images
are local review artifacts. See `AGENTS.md` for mandatory pause checks.

## Physics conventions

- \(B_\nu\) is spectral radiance per unit frequency and includes both
  polarizations.
- One matched receiver mode has \(A\Omega=\lambda^2\) and selects one
  polarization.
- The Rayleigh-Jeans limit requires \(h\nu\ll k_BT\).
- \(P=k_BTB\) gives available thermal-noise power for one matched mode over
  bandwidth \(B\). Receiver loss, mismatch, and receiver-added noise require
  additional factors or noise temperatures.

The exact thermal power spectral density of one mode, excluding zero-point
energy, is

\[
\frac{dP}{d\nu}=\frac{h\nu}{\exp[h\nu/(k_BT)]-1}.
\]

# Digital modulation and antenna radiation

`telecom_modulations.py` is an eleven-section animated lecture. It begins with an
antenna radiating an electromagnetic wave, introduces BPSK one bit at a time,
defines bit and symbol rates with units, then shows QPSK, ASK, FSK, and QAM.

```bash
# Fast preview
conda run -n base manim -pql telecom_modulations.py TelecomModulations

# Final 1920 x 1080 render
conda run -n base manim -pqh telecom_modulations.py TelecomModulations
```

Keep source-script provenance in code comments and data metadata, never in the video.
