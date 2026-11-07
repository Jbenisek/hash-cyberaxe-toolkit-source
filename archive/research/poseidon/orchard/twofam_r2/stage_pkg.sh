#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# Put the staged candidate (pkg_stage/) into the fresh WSL copy of the clone and run the organizer's mechanical checks.
# Nothing is submitted; no yukon command is run; no AI review is run.
set -euo pipefail
SRC="${HASHCYBERAXE_WORKSPACE}/research/poseidon/orchard/twofam_r2/pkg_stage"
ROOT=/root/hashsmash/yukon/pos_r2_twofam
if [ ! -d "$ROOT" ]; then cp -a /root/hashsmash/yukon/pos_r1_pkg "$ROOT"; rm -rf "$ROOT/pareto/.yukon/work" "$ROOT/pareto/STAGED.sha256" "$ROOT/pareto/submission-note.md" "$ROOT/pareto/__pycache__"; fi
CAND="$ROOT/pareto/candidates/poseidon"
rm -rf "$CAND"
mkdir -p "$CAND"
(cd "$SRC" && find . -type f -not -path '*/__pycache__/*' -print0) | while IFS= read -r -d '' f; do
  install -D -m 0644 "$SRC/$f" "$CAND/$f"
done
echo "--- candidate files"
find "$CAND" -type f -printf '%m %7s %p\n' | sort -k3
if grep -l $'\r' "$CAND"/proof.md "$CAND"/claim.json "$CAND"/certificates/manifest.json >/dev/null 2>&1; then echo "CRLF found in text files"; exit 1; fi
cp "$(dirname "$SRC")/submission-note.md" "$ROOT/pareto/submission-note.md"
cd "$ROOT/pareto"
echo "--- pareto_candidate.py --family poseidon --rounds 2"
python3 ../scripts/pareto_candidate.py --family poseidon --rounds 2
(cd candidates/poseidon && find . -type f -not -path '*/__pycache__/*' | sort | xargs sha256sum) > STAGED.sha256
sha256sum submission-note.md >> STAGED.sha256
echo "--- STAGED.sha256 written"; wc -l STAGED.sha256
