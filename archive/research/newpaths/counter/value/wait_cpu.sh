#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# exits when all four CPU rate runs have written their output (or their timeout parents are gone)
D="${HASHCYBERAXE_WORKSPACE}"/research/newpaths/counter/value/out
for i in $(seq 1 330); do
  n=0
  for f in r_sub_cube_s11 r_sub_cube_s12 r_all_cube_s13 r_all_free_s14; do
    grep -q "^COP" "$D/$f.txt" 2>/dev/null && n=$((n+1))
  done
  if [ "$n" = 4 ]; then echo "all 4 CPU runs done"; exit 0; fi
  if ! pgrep -f "ctr_rates rates" > /dev/null; then echo "no ctr_rates left, $n of 4 complete"; exit 0; fi
  sleep 5
done
echo "still running after wait"
