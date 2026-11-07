#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# Regenerate the expected-hash files that tools/stage_pkg7.sh verifies, after the fix3 corrections.
# Run: wsl -d Ubuntu -- bash "./research/pkg7/work/fix3/freeze_fix3.sh"
set -euo pipefail
P="${HASHCYBERAXE_WORKSPACE}/research/pkg7"
cd "$P/blake3-r2"
find . -type f -not -path '*/__pycache__/*' -not -name '*.pyc' | sort | xargs sha256sum > "$P/FROZEN_fix.sha256"
cd "$P"
sha256sum -b submission-note-r2.md > "$P/FROZEN_fix_note.sha256"
echo "=== FROZEN_fix.sha256 ==="
cat "$P/FROZEN_fix.sha256"
echo "=== FROZEN_fix_note.sha256 ==="
cat "$P/FROZEN_fix_note.sha256"
echo "=== verify package against the frozen file ==="
(cd "$P/blake3-r2" && sha256sum --quiet -c "$P/FROZEN_fix.sha256") && echo "package: all files match"
echo "=== verify note hash (first 64 chars, as stage_pkg7.sh does) ==="
[ "$(sha256sum "$P/submission-note-r2.md" | cut -c1-64)" = "$(cut -c1-64 "$P/FROZEN_fix_note.sha256")" ] && echo "note: matches"
