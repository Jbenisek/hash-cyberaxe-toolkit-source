#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/sha256grid/check2-1" || exit 1
L="${HASHCYBERAXE_WORKSPACE}/research/sha256grid/map-r38"
python3 price_check.py | tee price_check.txt
echo "--- levers_r38.py re-run (stdout only) vs its saved output:"
python3 $L/levers_r38.py > levers_rerun.txt 2>&1
diff <(tr -d '\r' < levers_rerun.txt) <(tr -d '\r' < $L/levers_r38.out.txt) && echo "levers_r38.py output IDENTICAL to levers_r38.out.txt"
sed -n '1,2p;6,7p' levers_rerun.txt
echo "--- chain A status:"; date; for f in g8_s1 k2_s1; do [ -f $f.done ] && echo "$f: $(cat $f.done)"; [ -f $f.out ] && grep -E '^s |process-time' $f.out; done
pgrep -a kissat
