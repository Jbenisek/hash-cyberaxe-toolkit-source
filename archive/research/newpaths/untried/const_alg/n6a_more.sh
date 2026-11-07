#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# n6a_more.sh: the calculator on N6a's remaining SAT betas (k <= 16), nearest to 13140f5f first, 313c0f55 last (it
# held the only process for the whole 682 s limit of run_pin), ONE process (the delta-8 solver run holds the other),
# time limit 480 s; then the report. Log lines to status.txt as run_pin.sh writes them.
export PYTHONDONTWRITEBYTECODE=1
D="${HASHCYBERAXE_WORKSPACE}/research/newpaths/untried/const_alg"
cd "$D" || exit 3
echo "$(date +%H:%M:%S) n6a_more pid $$ pgid $(ps -o pgid= $$ | tr -d ' ')" >> "$D/pids.txt"
t0=$(date +%s)
r=$(nice -n 5 python3 -B ctr_count.py satfirst N6a 1 480 13140f5f 313c0f55 2>> "$D/run.err" | tail -1)
echo "$(date +%H:%M:%S) [satfirst $(( $(date +%s) - t0 ))s] $(echo "$r" | cut -c1-700)" >> "$D/status.txt"
r=$(nice -n 5 python3 -B ctr_count.py report N6a 2>> "$D/run.err" | tail -1)
echo "$(date +%H:%M:%S) [report] $(echo "$r" | cut -c1-700)" >> "$D/status.txt"
