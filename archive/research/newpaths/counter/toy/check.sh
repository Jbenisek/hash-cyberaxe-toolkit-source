#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# construction checks, sets 0..7, heaviest beta of each (research only)
D="${HASHCYBERAXE_WORKSPACE}"/research/newpaths/counter/toy
cd "$D" || exit 1
: > check_w8.txt
for i in 0 1 2 3 4 5 6 7; do
  b=$(grep ^HEAVIEST mass_set$i.txt | awk '{print $3}')
  $HOME/ctr_toy_bin/ctr_toy8 check sets_w8.txt $i $b 3000 $((9100+i)) >> check_w8.txt
done
cat check_w8.txt
