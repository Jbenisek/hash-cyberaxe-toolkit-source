#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
D="${HASHCYBERAXE_WORKSPACE}"/research/newpaths/counter/toy
cd "$D" || exit 1
$HOME/ctr_toy_bin/ctr_toy8 run filed sets_w8.txt 0 0 0 1 2048 | grep -E "^(PART|RUN)"
$HOME/ctr_toy_bin/ctr_toy8 run ctr sets_w8.txt 0 bf 0 1 512 | grep -E "^(PART|RUN)"
