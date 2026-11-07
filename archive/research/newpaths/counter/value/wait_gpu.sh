#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# exits when the GPU run log has at least N finished lines (arg 1), or the run script is gone
L="${HASHCYBERAXE_WORKSPACE}"/research/newpaths/counter/value/out/gpu_runs.log
N=${1:-1}
for i in $(seq 1 340); do
  n=$(grep -c ": exit" "$L" 2>/dev/null)
  if [ "$n" -ge "$N" ]; then echo "GPU runs finished: $n"; cat "$L"; exit 0; fi
  if ! pgrep -f run_gpu.sh > /dev/null; then echo "run_gpu.sh gone, finished $n"; cat "$L"; exit 0; fi
  sleep 5
done
echo "still running"; cat "$L"
