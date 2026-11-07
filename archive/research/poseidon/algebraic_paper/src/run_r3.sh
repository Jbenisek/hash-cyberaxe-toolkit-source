#!/bin/bash
# RR=3 test of the algebraic-paper program: one thread per process, nice 10, ulimit -s 64. Runs the binaries built by build_all.sh (in /tmp/algpaper), one process per coin seed
# (default seeds 1 2 3 = 3 processes). Output: src/logs/r3_s<seed>.txt (program output + EXIT line), start/end times. Run:
#   wsl -d Ubuntu -- bash run_r3.sh
SRC=$(cd "$(dirname "$0")" && pwd)
mkdir -p $SRC/logs; cd /tmp/algpaper || exit 1
for s in ${SEEDS:-1 2 3}; do
  ( ulimit -s 64; date -u > $SRC/logs/r3_s$s.start; nice -n 10 ./single_r3_s$s 1 > $SRC/logs/r3_s$s.txt 2>&1; echo "EXIT $?" >> $SRC/logs/r3_s$s.txt; date -u > $SRC/logs/r3_s$s.end ) &
done
wait
