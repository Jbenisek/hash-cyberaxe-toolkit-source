#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# lens EVERY FIGURE: two starts of a run in the exact layout of 6.4 (2 processes, CPU)
cd "${HASHCYBERAXE_WORKSPACE}"/research/pkg5/review || exit 1
t0=$(date +%s)
for s in one two; do
  PYTHONDONTWRITEBYTECODE=1 nice -n 10 python3 -B fig_h3_layout.py $s 8 8 > fig_h3_layout_$s.out 2> fig_h3_layout_$s.err &
done
wait
echo "seconds $(( $(date +%s) - t0 ))"
cat fig_h3_layout_one.out fig_h3_layout_two.out | cut -c1-520
cat fig_h3_layout_one.err fig_h3_layout_two.err | tail -3 | cut -c1-300
