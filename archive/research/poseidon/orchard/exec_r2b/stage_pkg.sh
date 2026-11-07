#!/bin/bash
# Put the candidate (pkg_stage/) into its own slot of the clone and run the organizer's mechanical intake. Nothing is submitted;
# no yukon command is run; no AI review is run. Slot: /root/hashsmash/yukon/pos_r2_exec2 (created from pos_r1_pkg if missing).
set -euo pipefail
SRC="$(cd "$(dirname "$0")" && pwd)/pkg_stage"
NOTESRC="$(cd "$(dirname "$0")" && pwd)/submission-note.md"
ROOT=/root/hashsmash/yukon/pos_r2_exec2
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
cp "$NOTESRC" "$ROOT/pareto/submission-note.md"
cd "$ROOT/pareto"
echo "--- pareto_candidate.py --family poseidon --rounds 2"
python3 ../scripts/pareto_candidate.py --family poseidon --rounds 2
(cd candidates/poseidon && find . -type f -not -path '*/__pycache__/*' | sort | xargs sha256sum) > STAGED.sha256
sha256sum submission-note.md >> STAGED.sha256
echo "--- STAGED.sha256 written"; wc -l STAGED.sha256
