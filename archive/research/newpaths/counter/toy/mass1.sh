#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# exact counts for one set: mass1.sh ID  -> mass_set<ID>.txt and massmat_set<ID>.txt
D="${HASHCYBERAXE_WORKSPACE}"/research/newpaths/counter/toy
cd "$D" || exit 1
/usr/bin/time -f "seconds %e" $HOME/ctr_toy_bin/ctr_toy8 mass sets_w8.txt "$1" "massmat_set$1.txt" > "mass_set$1.txt" 2>&1
grep -E "^(MASS|HEAVIEST|BESTGAIN|seconds)" "mass_set$1.txt"
