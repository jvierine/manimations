#!/usr/bin/env bash
set -euo pipefail
bad=0
while IFS= read -r -d '' path; do
  case "$path" in
    *.png|*.jpg|*.jpeg|*.gif|*.webp|*.svg|*.pdf|*.mp4|*.mov|*.webm|*.mkv|*.mp3|*.wav|*.h5|*.hdf5|*.rgb|*.wasm|*.zip|meteor_rcs/webgl/pkg/*|meteor_rcs/webgl/scenes.json|meteor_rcs/webgl/current.json)
      echo "Non-code asset tracked: $path" >&2
      bad=1
      ;;
  esac
done < <(git ls-files -z)
if (( bad )); then exit 1; fi
echo 'Tracked files contain source code and configuration only.'
