#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# THE bounded GPU run (hotspot folder; research only): two sequential jobs, hard caps 1380 s + 360 s (< 30 min total).
# Same arrangement and events as counter/value ctr_gpu.cu real mode; fresh seeds (201, 202).
D="${HASHCYBERAXE_WORKSPACE}"/research/newpaths/hotspot
cd "$D" || exit 1
echo "run_main.sh pid $$ started $(date +%T)" >> my_pids.txt
echo "start $(date +%T)" > out/main_runs.log
nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader >> out/main_runs.log
run() { local name=$1 cap=$2; shift 2; local t0=$(date +%s)
  timeout $cap ./hotspot "$@" out/$name.bin > out/$name.txt 2> out/$name.err &
  local p=$!; echo "$name pid $p (timeout wrapper) $(date +%T)" >> my_pids.txt; wait $p
  echo "$name: exit $?, $(( $(date +%s) - t0 )) s, $(date +%T)" >> out/main_runs.log; }
#            SUB THR OUT IN LAUNCH SEED NSEL TSEL RSEL ESEL HWT HWH
run h_sub 1380 1  16  5   12 3584   201  14   16   19   1    23  32
run h_all 360  0  16  5   12 1024   202  13   15   18   0    23  32
echo "done $(date +%T)" >> out/main_runs.log
