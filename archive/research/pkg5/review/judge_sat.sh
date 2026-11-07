#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# hostile-judge lens: second and third solver on rule A, own encoder; 5 threads, CPU only
cd "${HASHCYBERAXE_WORKSPACE}/research/pkg5/review" || exit 1
S="${1:-cadical}"
start=$(date +%s)
nice -n 10 python3 -B judge_sat.py "$S" 5 2>&1 | cut -c1-300 | head -6
echo "$S seconds $(( $(date +%s) - start ))"
