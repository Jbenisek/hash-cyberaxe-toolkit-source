#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# ctr_cone4.sh: COUNTER=1, pin H8, Y4 and E1.d1 in the basis, only Y4 held fixed per outer step (the inner word may
# be E1.d1 itself, varied inside the heavy beta cube, or any other basis word).  Bound B on the words recomputed
# per inner step before the test E1.b1 (the next E1 test once E1.d1 is prescribed).
cd "${HASHCYBERAXE_WORKSPACE}/research/newpaths/scout_recent"
export PYTHONDONTWRITEBYTECODE=1 COUNTER=1 PIN_EXTRA=w14
printf '%s\n' "$@" | xargs -P 2 -I{} bash -c 'f=cone4_E1b1_B{}.txt; python3 -B basis_sat_ctr.py Y4,E1.d1 --outer Y4 --cone-max E1.b1:{} --cone E1.b1,E1.a2,E3.h1,E3.g1,E3.e2 --order --levels 110 --time 240 > $f 2>&1; echo "B={}: $(head -1 $f | cut -c1-300)"; grep "cone of" $f | cut -c1-140'
