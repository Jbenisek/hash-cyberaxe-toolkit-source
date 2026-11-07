#!/usr/bin/env bash
# Stage pkg9 (the slimmed cluster package at margin 2, claim 92.58) into the Yukon checkout and run the organizer's
# own intake on it: the mechanical check, the declared experiments and the judge evidence. On the owner's explicit
# go of 2026-10-07. Runs no yukon command and submits nothing. The candidate folder is backed up first.
set -uo pipefail
W='historical-sources/~~Projects/~HashSmash/workspace'; P="$W/research/pkg9/pkg"
PKG="$P/blake3-r2"; NOTE_SRC="$P/submission-note-r2.md"
DST="$HOME/hashsmash/yukon/hashsmash"; CAND='lanes/exploratory/candidates/blake3-r2'
NOTE="$HOME/hashsmash/notes/submission-note-r2-pkg9.md"
cd "$DST" || exit 1
BK="$HOME/hashsmash/backup_candidates/blake3-r2_$(date '+%Y%m%d_%H%M%S')"
mkdir -p "$BK" && cp -a "$DST/$CAND/." "$BK/" && echo "previous candidate kept in $BK"
rm -rf "${DST:?}/$CAND"
(cd "$PKG" && find . -type f -not -path '*/__pycache__/*' -not -name '*.pyc' -print0) | while IFS= read -r -d '' f; do
  install -D -m 0644 "$PKG/$f" "$DST/$CAND/$f"; done
sed -i 's/"submission_state": "draft"/"submission_state": "ready"/' "$DST/$CAND/claim.json"
install -D -m 0644 "$NOTE_SRC" "$NOTE"
echo "staged: $(find "$CAND" -type f | wc -l) files; $(grep -o -E '"submission_state": "[a-z]+"|"time_log2": [0-9.]+' "$CAND/claim.json" | tr '\n' ' ')"
echo "note: $(wc -c < "$NOTE") bytes; CRLF files: $(grep -rlI $'\r' "$CAND" "$NOTE" | wc -l)"
echo "== mechanical check"
python3 scripts/local_tracks.py check blake3-r2-exploratory 2>&1 | grep -E '"status"|submission_state|qualified' | tr -d ' \n'; echo
echo "== organizer intake (experiments and judge evidence)"
t0=$(date +%s)
timeout 1700 python3 scripts/hashsmash_pipeline.py intake --track blake3-r2-exploratory 2>&1 | tail -3
echo "intake finished in $(( $(date +%s) - t0 )) s"
EV=lanes/exploratory/.yukon/work/tracks/blake3-r2-exploratory/judge-evidence.json
[ -f "$EV" ] && echo "judge evidence: $(stat -c%s "$EV") bytes (the 93.5 that the judge failed on: 329,710)"
echo "== hashes"
(cd "$CAND" && sha256sum claim.json proof.md experiments/halfsearch.py experiments/manifest.json certificates/manifest.json)
sha256sum "$NOTE" | sed "s|$HOME|~|"
