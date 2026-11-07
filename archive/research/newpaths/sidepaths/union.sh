#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# all 0-check bases containing Y4 and w5 (k = 6 more words), printed in full
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/sidepaths
timeout 600 ./gdx m_y4_w5.model 6 0 1 1000000 > all_y4_w5_k6.txt
echo done > union.done
