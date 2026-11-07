#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# ctr_cone3.sh: (a) COUNTER=1, pin H8, Y4 and E3.h1 prescribed and fixed per outer step: cheapest inner loop
# before the first test E1.d1 (bounds 20, 40, 60).  (b) COUNTER=2 (T1 = high counter word also free; only 19
# bits are reachable, so solving for T1 is a 2^-13 filter): can Y4, E1.d1 and E3.h1 all be prescribed?
cd "${HASHCYBERAXE_WORKSPACE}/research/newpaths/scout_recent"
export PYTHONDONTWRITEBYTECODE=1 PIN_EXTRA=w14
run() { COUNTER=$1 python3 -B basis_sat_ctr.py $2 $3 --levels 110 --time 240 > $4 2>&1; echo "$4: $(head -1 $4 | cut -c1-300)"; grep 'cone of' $4 | cut -c1-120; }
export -f run
printf '%s\n' "1 Y4,E3.h1 --outer_Y4,E3.h1_--cone-max_E1.d1:40_--cone_E1.d1,E1.b1,E1.a2,E3.g1,E3.e2_--order cone3_E3h1_B40.txt" \
              "2 Y4,E1.d1,E3.h1 --order cone3_triple_c2.txt" \
              "1 Y4,E3.h1 --outer_Y4,E3.h1_--cone-max_E1.d1:70_--cone_E1.d1,E1.b1,E1.a2,E3.g1,E3.e2_--order cone3_E3h1_B70.txt" \
  | xargs -P 2 -I{} bash -c 'set -- {}; run $1 $2 "${3//_/ }" $4'
