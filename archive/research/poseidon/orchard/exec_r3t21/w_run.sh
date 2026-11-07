#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# waits for 1-min load < 19 (polls every 5 min), then the counted run exactly like exec_r3f/w_run.sh
D="${HASHCYBERAXE_WORKSPACE}"/research/poseidon/orchard/exec_r3t21; cd $D || exit 1
mkdir -p logs
while :; do L=$(cut -d' ' -f1 /proc/loadavg); echo "$(date) load $L" >> logs/wait.txt; awk -v l=$L 'BEGIN{exit !(l<19)}' && break; sleep 300; done
date -u > logs/run_start.txt
NICE=10 SIM_EXTENT=0 bash cycle.sh > logs/cycle_out.txt 2>&1
date -u > logs/run_end.txt
