#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# controls: one z3 process at a time
cd "${HASHCYBERAXE_WORKSPACE}/research/fifties/combos/solvers-GROK-R3" || exit 1
z3 --version
for f in ctl_pinned ctl_bad; do
  s=$(date +%s.%N)
  z3 -T:300 -st $f.smt2 > $f.out 2>&1
  e=$(date +%s.%N)
  echo "$f wall $(echo "$e - $s" | bc) s"; head -3 $f.out
done
