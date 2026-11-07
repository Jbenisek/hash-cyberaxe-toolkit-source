#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# usage: run_round.sh CNF TAG SEED [SEED...]  - starts one detached kissat --time=1700 per seed, prints PIDs
cd "${HASHCYBERAXE_WORKSPACE}/research/sha256grid/scout2-1" || exit 1
CNF=$1; TAG=$2; shift 2
for seed in "$@"; do
  setsid nohup bash -c '
    s=$(date +%s.%N)
    kissat --time=1700 --seed='"$seed"' '"$CNF"' > '"${TAG}_s${seed}"'.out 2>&1 &
    k=$!
    echo $k > '"${TAG}_s${seed}"'.pid
    wait $k; rc=$?
    e=$(date +%s.%N)
    echo "rc=$rc start=$s end=$e wall=$(echo "$e - $s" | bc)" > '"${TAG}_s${seed}"'.done
  ' > /dev/null 2>&1 < /dev/null &
done
sleep 1
for seed in "$@"; do echo "$TAG seed $seed kissat pid $(cat ${TAG}_s${seed}.pid 2>/dev/null)"; done
date