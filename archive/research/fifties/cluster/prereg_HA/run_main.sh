#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# prereg_HA step 3: the main GPU run, once. $1 = seed64 hex of "prereg_HA 2026-10-09" (ref.py seed).
set -e
cd "${HASHCYBERAXE_WORKSPACE}/research/fifties/cluster/prereg_HA"
test -x gate
test ! -e main_result.json || { echo "main_result.json exists: main run already done, refusing to rerun"; exit 3; }
nvidia-smi --query-gpu=name,utilization.gpu --format=csv,noheader
./gate count "$1" 4294967296 > main_result.tmp
mv main_result.tmp main_result.json
cat main_result.json
