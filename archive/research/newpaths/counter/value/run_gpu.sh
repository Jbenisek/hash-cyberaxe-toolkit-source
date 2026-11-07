#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# sequential GPU runs (one GPU job at a time), each with a time limit (counter/value)
D="${HASHCYBERAXE_WORKSPACE}"/research/newpaths/counter/value
cd "$D" || exit 1
mkdir -p out
echo "start $(date +%T)" > out/gpu_runs.log
run() { local name=$1; shift; local t0=$(date +%s)
  timeout 2700 ./ctr_gpu "$@" > out/$name.txt 2> out/$name.err
  echo "$name: exit $?, $(( $(date +%s) - t0 )) s, $(date +%T)" >> out/gpu_runs.log; }
run g_real_sub45   real  1 16 5 12 4096 101
run g_model_sub44  model 1 16 4 12 4096 102
run g_real_all44   real  0 16 4 12 4096 103
run g_model_all43  model 0 16 3 12 4096 104
echo "done $(date +%T)" >> out/gpu_runs.log
