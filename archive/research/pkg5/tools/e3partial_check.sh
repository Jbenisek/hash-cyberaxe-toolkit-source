#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# The check of the partial E3 probability program (research/night/main/e3partial.c) against brute force at 8-bit
# words, run again so that its result is on file: evidence/e3partial_bf8.txt. The program is built here afresh
# from the night's source, exactly as research/night/main/e3partial.sh builds it (-DWBITS=8 -DSELFTEST), into a
# folder of its own, and run with the same two arguments (30 cases, seed 11). CPU only. Research helper.
#
#   wsl -d Ubuntu -- bash './research/pkg5/tools/e3partial_check.sh'
set -uo pipefail
PKG="${HASHCYBERAXE_WORKSPACE}/research/pkg5"
SRC="${HASHCYBERAXE_WORKSPACE}/research/night/main"
TMP="$HOME/hashsmash/pkg5-recount"
mkdir -p "$PKG/evidence" "$TMP"
cd "$SRC" || exit 2
gcc -O2 -fopenmp -DWBITS=8 -DSELFTEST -o "$TMP/e3partial_bf8" e3partial.c -lm 2> "$TMP/e3partial_build.log" || { echo "build failed"; head -5 "$TMP/e3partial_build.log"; exit 3; }
{
  echo "SOURCE e3partial.c sha256 $(sha256sum e3partial.c | cut -c1-64); built with -DWBITS=8 -DSELFTEST; arguments 30 11"
  OMP_NUM_THREADS=4 "$TMP/e3partial_bf8" 30 11
  echo "exit status $?"
} > "$PKG/evidence/e3partial_bf8.txt" 2>&1
tail -4 "$PKG/evidence/e3partial_bf8.txt" | cut -c1-240
