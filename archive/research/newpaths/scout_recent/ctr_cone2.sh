#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# ctr_cone2.sh: COUNTER=1, pin H8, Y4 and E1.d1 in the basis.  Spec lines "OUTER:B" : words in OUTER are held
# fixed per outer step (comma list), at most B words recomputed per inner step before the first test E3.h1.
cd "${HASHCYBERAXE_WORKSPACE}/research/newpaths/scout_recent"
export PYTHONDONTWRITEBYTECODE=1 COUNTER=1 PIN_EXTRA=w14
printf '%s\n' "$@" | xargs -P 2 -I{} bash -c 'o=${1%%:*}; b=${1##*:}; f=cone2_${o//,/_}_B$b.txt; python3 -B basis_sat_ctr.py Y4,E1.d1 --outer $o --cone-max E3.h1:$b --cone E3.h1,E3.g1,E3.e2,E1.b1,E1.a2 --order --levels 110 --time 240 > $f 2>&1; echo "$1: $(head -1 $f | cut -c1-300)"; grep "cone of" $f | cut -c1-160' _ {}
