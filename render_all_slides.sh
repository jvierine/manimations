#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

SHOW_PROVENANCE=0 conda run -n base manim-slides render \
  --disable_caching -r 1920,1080 --fps 30 planck_to_ktb.py PlanckToKTB
SHOW_PROVENANCE=0 conda run -n base manim-slides render \
  --disable_caching -r 1920,1080 --fps 30 telecom_modulations.py TelecomModulations
SHOW_PROVENANCE=0 conda run -n base manim-slides render \
  --disable_caching -r 1920,1080 --fps 30 friis_voyager.py FriisVoyager
