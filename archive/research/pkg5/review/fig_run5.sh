#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# lens EVERY FIGURE: second solver, own encoder (4 workers, CPU). Temporary CNF files go to the session scratchpad.
T="temporary-run-output"
cd "${HASHCYBERAXE_WORKSPACE}"/research/pkg5/review || exit 1
t0=$(date +%s)
PYTHONDONTWRITEBYTECODE=1 nice -n 10 python3 -B fig_sat2.py "$T" "$1" 2> "fig_sat2_$1.err" | tail -2
echo "seconds $(( $(date +%s) - t0 )) stderr lines $(wc -l < "fig_sat2_$1.err")"
tail -2 "fig_sat2_$1.err" | cut -c1-300
