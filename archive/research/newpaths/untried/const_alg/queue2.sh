#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# queue2.sh: the pin solver with the COUNTER objective (trailmin5_ctr.py via pinctr.sh), deltas 8 and 6, new pins
# only, two runs side by side (2 processes), kissat --time=1080 each, so each run ends inside 20 minutes.
#   delta 8: length XOR 8 (55/63), W13 top 8 bits zero, delta free (+-8), counter bound 88 (best known: L8c, L8b 88; H8 89)
#   delta 6: length XOR 6 (57/63), W13 free, delta +6 (as L6c), counter bound 90 (best known: L6c 91)
D="${HASHCYBERAXE_WORKSPACE}/research/newpaths/untried/const_alg"
echo "$(date +%H:%M:%S) queue2 pid $$ pgid $(ps -o pgid= $$ | tr -d ' ')" >> "$D/pids.txt"
bash "$D/pinctr.sh" 8 free 8 88 24 51 1080 &
bash "$D/pinctr.sh" 6 00000006 0 90 24 61 1080 &
wait
grep -E '^RES' "$D/pinctr.log" | cut -c1-400
