#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# hostile-judge lens: H3 over many sets of seed words; CPU only, at most 5 worker processes, numpy threads off
cd "${HASHCYBERAXE_WORKSPACE}/research/pkg5/review" || exit 1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
python3 -c "import numpy; print('numpy', numpy.__version__)" 2>&1 | tail -1
start=$(date +%s)
nice -n 10 python3 -B judge_h3.py "${1:-16}" "${2:-12}" "${3:-5}" "${4:-0}" 2>&1 | cut -c1-330 | tail -7
echo "seconds $(( $(date +%s) - start ))"
