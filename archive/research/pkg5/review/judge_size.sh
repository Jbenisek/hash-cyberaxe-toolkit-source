#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# hostile-judge lens: size of the judge evidence of the last local intake in the validation mirror (read-only, stat only)
F="$HOME/hashsmash/hash-smash/lanes/exploratory/.yukon/work/tracks/blake3-r2-exploratory/judge-evidence.json"
if [ -f "$F" ]; then
  echo "judge-evidence.json bytes $(stat -c %s "$F") modified $(stat -c %y "$F" | cut -c1-16) limit $((512*1024))"
else
  echo "judge-evidence.json not found in the mirror"
fi
P="${HASHCYBERAXE_WORKSPACE}/research"
echo "proof bytes pkg4 $(stat -c %s "$P/pkg4/blake3-r2/proof.md") pkg5 $(stat -c %s "$P/pkg5/blake3-r2/proof.md") limit $((512*1024))"
echo "program bytes pkg4 $(stat -c %s "$P/pkg4/blake3-r2/experiments/halfsearch.py") pkg5 $(stat -c %s "$P/pkg5/blake3-r2/experiments/halfsearch.py") limit $((64*1024))"
