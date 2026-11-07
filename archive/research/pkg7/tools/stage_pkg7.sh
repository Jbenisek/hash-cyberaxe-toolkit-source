#!/usr/bin/env bash
# Stage pkg7 into the Yukon checkout (WSL ~/hashsmash/yukon/hashsmash). WRITTEN IN THE STEP FIX, NEVER RUN BY IT.
# Run only after the owner's go for THIS package (pkg7, blake3-r2, time_log2 95.7), by the main session:
#
#   wsl -d Ubuntu -- bash "./research/pkg7/tools/stage_pkg7.sh"
#
# It refuses unless blake3-r2/ and the note have the hashes of FROZEN_fix.sha256 and FROZEN_fix_note.sha256 (the
# validated files of the step FIX). It copies the candidate folder that is in the checkout now (the files of the
# filed entry c66f230d) to ~/hashsmash/backup_candidates/ first, replaces it with research/pkg7/blake3-r2, sets
# "submission_state" to "ready" in the staged copy only (research/pkg7 stays draft), copies the note to
# ~/hashsmash/notes/submission-note-r2-pkg7.md, runs the repository's mechanical check there and compares every
# staged file with the frozen one. It runs no yukon command and submits nothing.
set -euo pipefail
W='historical-sources/~~Projects/~HashSmash/workspace'; P="$W/research/pkg7"
PKG="$P/blake3-r2"; NOTE_SRC="$P/submission-note-r2.md"
DST="$HOME/hashsmash/yukon/hashsmash"; CAND='lanes/exploratory/candidates/blake3-r2'
NOTE="$HOME/hashsmash/notes/submission-note-r2-pkg7.md"
(cd "$PKG" && sha256sum --quiet -c "$P/FROZEN_fix.sha256") || { echo "STOP: blake3-r2 differs from the frozen, validated package"; exit 1; }
[ "$(sha256sum "$NOTE_SRC" | cut -c1-64)" = "$(cut -c1-64 "$P/FROZEN_fix_note.sha256")" ] || { echo "STOP: the note differs from the frozen note"; exit 1; }
[ -d "$DST/.git" ] || { echo "STOP: no checkout at $DST"; exit 1; }
BK="$HOME/hashsmash/backup_candidates/blake3-r2_$(date '+%Y%m%d_%H%M%S')"
if [ -d "$DST/$CAND" ]; then mkdir -p "$BK" && cp -a "$DST/$CAND/." "$BK/" && echo "previous candidate folder kept in $BK"; fi
rm -rf "${DST:?}/$CAND"
(cd "$PKG" && find . -type f -not -path '*/__pycache__/*' -not -name '*.pyc' -print0) | while IFS= read -r -d '' f; do
  install -D -m 0644 "$PKG/$f" "$DST/$CAND/$f"
done
sed -i 's/"submission_state": "draft"/"submission_state": "ready"/' "$DST/$CAND/claim.json"
install -D -m 0644 "$NOTE_SRC" "$NOTE"
cd "$DST"
echo "files in the checkout: $(find "$CAND" -type f | wc -l)"
grep -n -E '"submission_state":|"time_log2":' "$CAND/claim.json" | cut -c1-60 | tr '\n' ' '; echo
echo "mechanical check in the checkout: $(python3 scripts/local_tracks.py check blake3-r2-exploratory | grep -E '"status"|submission_state|certificates_verified' | tr -d ' \n')"
echo "note: $(wc -c < "$NOTE") bytes (minimum 5120); CRLF files: $(grep -rlI $'\r' "$CAND" "$NOTE" | wc -l)"
bad=0
for f in $(cd "$PKG" && find . -type f -not -name claim.json -not -path '*/__pycache__/*' -not -name '*.pyc' | sort); do
  [ "$(sha256sum "$PKG/$f" | cut -c1-64)" = "$(sha256sum "$DST/$CAND/$f" | cut -c1-64)" ] || { echo "DIFFERENT $f"; bad=1; }
done
[ "$(sed 's/"submission_state": "draft"/"submission_state": "ready"/' "$PKG/claim.json" | sha256sum | cut -c1-64)" = "$(sha256sum "$DST/$CAND/claim.json" | cut -c1-64)" ] || { echo "DIFFERENT claim.json"; bad=1; }
[ $bad = 0 ] && echo "STAGED: all files identical to the frozen package, state ready in the staged copy only" || echo "NOT STAGED CLEANLY"
git status --short "$CAND" | head -12
