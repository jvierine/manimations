# Repository instructions

Use the base conda environment for Python commands (`conda run -n base python ...`).
Use HDF5 rather than CSV for scientific data products.

## Keep Git code-only

Never commit media, scientific data, generated scene arrays, compiled browser
packages, or rendered outputs. Keep them local or on juha.no and restore needed
inputs through fetch_assets.py with asset_manifest.json. Do not use Git LFS for
these assets. Run bash check_code_only.sh before committing.

## Keep provenance out of rendered material

Keep script names, file paths, generator credits, and build/source provenance
in code comments or scientific-data metadata only. Never display these
annotations in presentations or publications, including slide footers, figure
captions, and nearby text. Do not add a display toggle. This applies to new
decks and revisions of existing decks. Ordinary scientific citations and a
references slide are appropriate; source-code credits are not.

## Keep labels clear of graphics

Place labels with visible clearance from curves, lines, arrows, symbols, other
labels, and moving objects by default. Check the entire animation, including
intermediate positions and the completed slide. Prefer space outside the
graphic or a clear leader line; do not place a curve through text.

## Explain equations visually

Define every symbol and its units on first use, including temperatures,
coefficients, and physical constants. Use MathTex for symbols such as
T_M, chi, and Gamma; do not substitute their literal names in rendered prose.
Build physical balances term by term, link each term to a graphical process,
and provide presenter-controlled pauses between the explanations.

## Manim slides: preserve the completed slide at every pause

These presentations are delivered as HTML pages with video segments. Every
slide in every deck MUST stop on its fully rendered content and remain visible
until the presenter advances. A fade to a blank background before the pause
defeats the purpose of the slide presentation.

- Put `next_slide()` BEFORE the outgoing slide's fade-out or cleanup. The
  fade-out belongs to the beginning of the next segment, after the user advances.
- Preserve the deferred-cleanup pattern in `start_slide()`, `clear_slide()`, and
  `_flush_pending_clear()` in all three presentation sources. `clear_slide()`
  queues cleanup; `start_slide()` first establishes the boundary and then runs it.
- The final slide must retain its completed content. Never clear it at the end
  of `construct()`. Check actual scene execution order, not method order in the file.
- Keep forward navigation from blanking or advancing beyond the last real slide.
  Preserve `final_slide_guard.js` in web exports, but do not mistake this navigation
  guard for a fix to fade-outs encoded into individual slide videos.
- After changing boundaries, rebuild and re-export EVERY affected deck. Validate
  the newly referenced media rather than trusting an old render or cache.
- Never splice isolated scene renders into an older deck manifest. The next
  segment contains the preceding slide's fade-out, so replacing only the slide
  leaves flashes of obsolete formulas/text at navigation boundaries. Rebuild
  the whole affected deck in execution order; export_web.py rejects manifests
  mixing render folders. Preserve pause-before-cleanup while doing this.
- Inspect the final decoded frame of EVERY exported slide video in EVERY affected
  deck. Reject blank endings and confirm the expected completed content is present;
  checking only the last slide of a deck is insufficient.
- After deployment, verify live browser playback through natural completion on
  the first and an intermediate slide, plus final-slide completion and another
  forward keypress. HTTP 200 and successful rendering alone are not acceptance.
- Do not claim the issue is fixed until the deployed pages pass these checks.

Public pages are under `https://juha.no/space/`; media belongs under
`/mnt/shovel/share/space/` on `juha-no`. Viewers use the browser directly.
After presentation changes, render, export, and deploy the updated browser
deck there by default, unless the user explicitly asks to hold rendering or
deployment. A source-only edit or local preview is not the completed delivery.
Do not edit the user's Keynote deck.

## Shared presentation fonts

All teaching decks, including new slides, must use the TeX-backed `Text`
renderer from `planck_to_ktb`, imported after `from manim import *`.
Do not fall back to Manim/Pango `Text`. Use `MathTex` for mathematics and
check that prose has no unsupported Unicode mathematical characters.

This regression affected all slides across all three decks and cost the user
roughly an hour of creative work. Treat correct pause behavior as a fundamental
requirement of every future slide change.

Explain why each mathematical block is needed before deriving it. For new
physical models, state the question, introduce symbols, trace the equation's
physical origin and assumptions, and provide clickable scientific references.
Use clear section transitions in long lectures. Keep colourbars and secondary
axes compact: collision clearance is not a reason for large empty gutters.
For Rustplotlib camera animations, check fixed annotations against projected
geometry in every frame with `Figure::check_annotations`.
