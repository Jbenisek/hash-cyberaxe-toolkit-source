#!/usr/bin/env bash
# THE SUBMIT of pkg9 (slimmed cluster package, margin 2, claim 92.58), on the owner's go of 2026-10-07 ("submit it").
# Refuses unless every staged file has the hash that was verified, then submits. Changes nothing in the package.
set -uo pipefail
export PATH="$HOME/.local/bin:$HOME/.bun/bin:$PATH"
export NO_COLOR=1
strip() { sed 's/\x1b\[[0-9;]*m//g'; }
cd "$HOME/hashsmash/yukon/hashsmash" || exit 1
NOTE="$HOME/hashsmash/notes/submission-note-r2-pkg9.md"
CAND='lanes/exploratory/candidates/blake3-r2'
bad=0
while read -r h f; do
  [ "$(sha256sum "$f" | cut -c1-64)" = "$h" ] || { echo "STOP: $f differs from the verified file"; bad=1; }
done <<EOF
88d08a4e2afb4f594f362cc9dbd8756c99d5319a45c5f5e16d7a95d6bc6068e8 $CAND/claim.json
4bb9b99d421e5ccb387c836b7ed5144e4f607f087f7e62cb3370f54ea34d748a $CAND/proof.md
9920bef24c77cbf3624ba7f74776f2e76480541fcc4a8864c12fe809c575e74b $CAND/experiments/halfsearch.py
3ba8bc765bcb2bbe3835ad78dac25f46f58875f90d647e7285c99d1edc5acff8 $CAND/experiments/manifest.json
a3c78779269ab224b0a36cc0cc075aaebdfb496a3a695bce1e743cf7bd45c4c8 $CAND/certificates/manifest.json
de4e2715d172f8739f1edf7c49ead47461aedf0bbe76624407bba904e403d0e3 $NOTE
EOF
[ $bad = 0 ] || exit 1
[ "$(find "$CAND" -type f | wc -l)" = 5 ] || { echo "STOP: the staged candidate does not hold exactly 5 files"; exit 1; }
echo "staged files identical to the verified ones"
echo "=== submissions in flight"
yukon submissions 2>&1 | strip | grep -E 'validating|queued|running' | head -5 || true
echo "=== yukon submit"
yukon submit --track blake3-r2-exploratory --note-file "$NOTE" \
  --model "Claude Opus 5.5" --harness "Claude Code" \
  --coauthors @winglock @Th0rgal @5kyguy @tekkac 2>&1 | strip | grep -v -E '^\+|^\||Update available|yukon update' | tail -12
echo "exit: ${PIPESTATUS[0]}"
date '+%Y-%m-%d %H:%M:%S %z'
