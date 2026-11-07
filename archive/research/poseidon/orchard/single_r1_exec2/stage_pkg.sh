#!/bin/bash
# Put the staged candidate (pkg_stage_cap6/) into its own copy of the clone and run the organizer's mechanical checks. Nothing is submitted;
# no yukon command is run; no AI review is run. (Adapted from twofam_r1/stage_pkg.sh; slot layout: ~/hashsmash/yukon/pos_r1_exec2/pareto/candidates/poseidon.)
# Called by `cycle.sh --stage` (CAP is taken from the environment, default 6). The slot is created from the pos_r1_pkg copy if missing.
set -euo pipefail
CAP=${CAP:-6}
SRC="$(cd "$(dirname "$0")" && pwd)/pkg_stage_exec"
NOTESRC="$(cd "$(dirname "$0")" && pwd)/submission-note_exec.md"
ROOT=/root/hashsmash/yukon/pos_r1_exec2
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
echo "--- pareto_candidate.py --family poseidon --rounds 1"
python3 ../scripts/pareto_candidate.py --family poseidon --rounds 1
(cd candidates/poseidon && find . -type f -not -path '*/__pycache__/*' | sort | xargs sha256sum) > STAGED.sha256
sha256sum submission-note.md >> STAGED.sha256
echo "--- STAGED.sha256 written"; wc -l STAGED.sha256
