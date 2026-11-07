#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# Reviewer, lens mathematics and cost: is the calculator's list of outcomes complete for each beta with a part?
R="${HASHCYBERAXE_WORKSPACE}/research/pkg5/review"
t0=$(date +%s)
for s in cadical kissat; do python3 -B "$R/math_seven.py" other $s 5 "${1:-300}" 2>&1 | cut -c1-300 | tail -1; done
python3 -B "$R/math_seven_cross.py" 2>&1 | cut -c1-330 | head -8
echo "seconds $(( $(date +%s) - t0 ))"
