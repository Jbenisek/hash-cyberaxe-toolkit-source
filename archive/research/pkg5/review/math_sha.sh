#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# Reviewer, lens mathematics and cost: which files the checks ran on.
P="${HASHCYBERAXE_WORKSPACE}/research/pkg5"
cd "$P" && sha256sum blake3-r2/proof.md blake3-r2/claim.json blake3-r2/experiments/halfsearch.py tools/pkg5_data.py | cut -c1-64,65-110
grep -o 'PROGRAM sha256 [0-9a-f]*' evidence/selftest_1200000_61.json | cut -c1-80
cat "$HOME/hashsmash/pkg5-review-math/.done" 2>/dev/null; ls "$P/review" | grep -c '^math_' | sed 's/^/my files: /'
