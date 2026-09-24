# Repository instructions

Use the base conda environment for Python commands (`conda run -n base python ...`).
Use HDF5 rather than CSV for scientific data products.

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
- Inspect the final decoded frame of EVERY exported slide video in EVERY affected
  deck. Reject blank endings and confirm the expected completed content is present;
  checking only the last slide of a deck is insufficient.
- After deployment, verify live browser playback through natural completion on
  the first and an intermediate slide, plus final-slide completion and another
  forward keypress. HTTP 200 and successful rendering alone are not acceptance.
- Do not claim the issue is fixed until the deployed pages pass these checks.

Public pages are under `https://juha.no/space/`; media belongs under
`/mnt/shovel/share/space/` on `juha-no`. Viewers use the browser directly.
Do not edit the user's Keynote deck.

This regression affected all slides across all three decks and cost the user
roughly an hour of creative work. Treat correct pause behavior as a fundamental
requirement of every future slide change.
