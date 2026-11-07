#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# Reviewer, lens mathematics and cost: wrapper for math_sat.py (arguments are passed on).
#   math_sat.sh run violate cadical 5 [limit]     math_sat.sh count
R="${HASHCYBERAXE_WORKSPACE}/research/pkg5/review"
t0=$(date +%s)
python3 -B "$R/math_sat.py" "$@" 2>&1 | cut -c1-400 | head -12
echo "exit ${PIPESTATUS[0]} seconds $(( $(date +%s) - t0 ))"
