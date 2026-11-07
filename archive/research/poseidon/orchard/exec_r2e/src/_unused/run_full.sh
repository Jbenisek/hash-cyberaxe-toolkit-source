#!/bin/bash
# One command for the full-size executed-outcome run (r=2, odd-part, centres c_i = i in order, fixed line j=0).
# usage: bash run_full.sh [maxcentres]     (owner's go required: one centre takes ~20-40 min of one core)
# Runs the counted program once (nice 10), writes logs/full_r2.txt, then verifies the collision with the reference hash.
cd "$(dirname "$0")"
mkdir -p ../logs
bash build_exec.sh || exit 1
MAXC=${1:-8}
( ulimit -s 64; nice -n 19 ./exec_attack 2 $MAXC 1 0 1 0 0 1 ) | tee ../logs/full_r2.txt
R=2 python3 verify_collision.py ../logs/full_r2.txt
