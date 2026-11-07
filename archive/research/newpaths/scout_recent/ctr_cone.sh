#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# ctr_cone.sh B..: with the chunk counter word free (COUNTER=1) and pin H8, Y4 and E1.d1 both prescribed and held
# fixed (outer); is there an inner basis word such that at most B words are recomputed per inner step before the
# first test E3.h1?  At most 2 solver processes.
cd "${HASHCYBERAXE_WORKSPACE}/research/newpaths/scout_recent"
export PYTHONDONTWRITEBYTECODE=1 COUNTER=1 PIN_EXTRA=w14
printf '%s\n' "$@" | xargs -P 2 -I{} bash -c "python3 -B basis_sat_ctr.py Y4,E1.d1 --outer Y4,E1.d1 --cone-max E3.h1:{} --cone E3.h1,E3.g1,E3.e2,E1.b1,E1.a2 --order --levels 110 --time 240 > cone_E1d1_B{}.txt 2>&1; echo B={}: \$(head -1 cone_E1d1_B{}.txt | cut -c1-300); grep 'cone of' cone_E1d1_B{}.txt | cut -c1-120"
