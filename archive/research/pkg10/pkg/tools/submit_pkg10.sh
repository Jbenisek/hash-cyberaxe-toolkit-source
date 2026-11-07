#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# THE SUBMIT of pkg9 (slimmed cluster package, margin 2, claim 92.58), on the owner's go of 2026-10-07 ("submit it").
# Refuses unless every staged file has the hash that was verified, then submits. Changes nothing in the package.
set -uo pipefail
export PATH="$HOME/.local/bin:$HOME/.bun/bin:$PATH"
export NO_COLOR=1
strip() { sed 's/\x1b\[[0-9;]*m//g'; }
cd "$HOME/hashsmash/yukon/hashsmash" || exit 1
NOTE="$HOME/hashsmash/notes/submission-note-r2-pkg10.md"
CAND='lanes/exploratory/candidates/blake3-r2'
P="${HASHCYBERAXE_WORKSPACE}/research/pkg10/pkg"
[ -f "$P/VERIFIED.sha256" ] || { echo "STOP: no VERIFIED.sha256; run stage_pkg10.sh first"; exit 1; }
sha256sum --quiet -c "$P/VERIFIED.sha256" || { echo "STOP: a staged file differs from the verified one"; exit 1; }

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
