#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/sidepaths
bash run_gdx.sh y4_w5 6 300
bash run_gdx.sh y4_w5_t2 6 300
for m in y4_g1_t2 y4_h1_t2 y4_e2_t2 y4_e1d1_t2 y4_e1a2_t2 y4_e1a1_t2 y4_g2_t2; do bash run_gdx.sh $m 6 300; done
echo BATCH2DONE > batch2.done
