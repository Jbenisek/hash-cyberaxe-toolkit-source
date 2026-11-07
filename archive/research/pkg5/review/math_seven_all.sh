#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# Reviewer, lens mathematics and cost: the whole seven-word system per beta, 39 betas with a part and 3 flagged.
R="${HASHCYBERAXE_WORKSPACE}/research/pkg5/review"
t0=$(date +%s)
for job in "any cadical" "violate cadical" "violate kissat" "any kissat"; do
  python3 -B "$R/math_seven.py" $job 5 "${1:-300}" 2>&1 | cut -c1-300 | tail -1
done
echo "seconds $(( $(date +%s) - t0 ))"
