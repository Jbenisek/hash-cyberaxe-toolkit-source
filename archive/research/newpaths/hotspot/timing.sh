#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# seconds-long timing check with the main run's settings (2^36 trials)
D="${HASHCYBERAXE_WORKSPACE}"/research/newpaths/hotspot
cd "$D" || exit 1
nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader
time timeout 120 ./hotspot 1 16 5 12 8 9 14 16 19 1 25 40 out/timing.bin > out/timing.txt 2> out/timing.err
echo "exit $?"
grep -E "RUN|trials|listed E1|partial E3 |eta cond|residual word|^HW|OVERFLOW" out/timing.txt
ls -l out/timing.bin
