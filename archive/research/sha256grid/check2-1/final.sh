#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# check2-1 post-run checks (one process at a time)
cd "${HASHCYBERAXE_WORKSPACE}/research/sha256grid/check2-1" || exit 1
S="${HASHCYBERAXE_WORKSPACE}/research/sha256grid/scout2-1"
date
echo "== independent verification: scout solutions, then mine"
mine=$(ls s_base.sols.json c_base.sols.json c_g8.sols.json c_g32.sols.json 2>/dev/null)
python3 indep_verify.py $S/step1_base.sols.json $S/step1_k1r16.sols.json $S/step1_g32.sols.json $S/step1_g8.sols.json $mine
echo "== my runs (units at 10^10/2728 per CPU-s)"
for f in sbase_s2 cbase_s1 cbase_s2 cbase_s3 g8_s1 k2_s1 g32_s2; do
  [ -f $f.out ] || continue
  t=$(grep 'process-time' $f.out | tail -1 | awk '{print $(NF-1)}')
  u=$(python3 -c "import math; print('%.3f' % (math.log2($t) + math.log2(1e10/2728)))")
  echo "$f: $(grep -m1 '^s ' $f.out) | $(grep '^c conflicts:' $f.out | awk '{print "conflicts", $3}') | $t CPU-s = 2^$u units | $(cat $f.done 2>/dev/null)"
done
date
