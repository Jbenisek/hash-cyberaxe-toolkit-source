#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/nb_verify_sidepaths_0 || exit 1
gcc -O3 -march=native -o cvrate cvrate.c 2>&1
for m in "iv 0" "cv 1" "cv 2" "cv 3"; do ./cvrate $m 4 5; done
# timing
/usr/bin/time -f "elapsed %e s" ./cvrate cv 1 24 9 | grep -v DBG | head -3
/usr/bin/time -f "elapsed %e s" ./cvrate m 0 24 9 | grep -v DBG | head -3
