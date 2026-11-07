#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# Reviewer, lens mathematics and cost: all 287 outcomes, three solvers on "violate", cadical on "all" and "keep".
R="${HASHCYBERAXE_WORKSPACE}/research/pkg5/review"
t0=$(date +%s)
for job in "violate cadical" "violate kissat" "violate cms" "all cadical" "keep cadical"; do
  python3 -B "$R/math_sat.py" run $job 5 2>&1 | cut -c1-300 | head -2
done
python3 -B "$R/math_sat.py" count 2>&1 | cut -c1-400 | head -9
echo "seconds $(( $(date +%s) - t0 ))"
