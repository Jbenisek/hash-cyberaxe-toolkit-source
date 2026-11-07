#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/sidepaths
for m in y4_h1 y4_e2 y4_e1d1 y4_e1a2 y4_e1a1 y4_g2; do bash run_gdx.sh $m 6 300; done
for m in y4_g1_e1d1 y4_h1_g1 y4_h1_e1d1 y4_w5_e1d1 y4_w5_g1; do bash run_gdx.sh $m 5 300; done
for m in g1 e1d1 h1; do bash run_gdx.sh $m 7 900; done
echo BATCH1DONE > batch1.done
