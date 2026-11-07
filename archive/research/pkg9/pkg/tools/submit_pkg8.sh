#!/usr/bin/env bash
# THE SUBMIT of the 93.5 package (pkg8), on the owner's go of 2026-10-07 ("go on 95.7 submit fix 4").
# It submits; it changes nothing in the package. Run stage_pkg7.sh first.
set -uo pipefail
export PATH="$HOME/.local/bin:$HOME/.bun/bin:$PATH"
export NO_COLOR=1
strip() { sed 's/\x1b\[[0-9;]*m//g'; }
cd "$HOME/hashsmash/yukon/hashsmash" || exit 1
NOTE="$HOME/hashsmash/notes/submission-note-r2-pkg8.md"
CAND='lanes/exploratory/candidates/blake3-r2'
grep -q '"submission_state": "ready"' "$CAND/claim.json" || { echo "STOP: the staged package is not ready"; exit 1; }
grep -q '"time_log2": 93.5' "$CAND/claim.json" || { echo "STOP: the staged claim is not 93.5"; exit 1; }
[ "$(wc -c < "$NOTE")" -ge 5120 ] || { echo "STOP: note too short"; exit 1; }
echo "=== submissions in flight"
yukon submissions 2>&1 | strip | cut -c1-140 | head -8
echo "=== yukon submit"
yukon submit --track blake3-r2-exploratory --note-file "$NOTE" \
  --model "Claude Opus 5.5" --harness "Claude Code" \
  --coauthors @winglock @Th0rgal @5kyguy @tekkac 2>&1 | strip | tail -25
echo "exit: ${PIPESTATUS[0]}"
date '+%Y-%m-%d %H:%M:%S %z'
