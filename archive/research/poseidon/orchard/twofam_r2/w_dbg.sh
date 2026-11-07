#!/bin/bash
cd "$(dirname "$0")"
gcc -O3 -march=native -w -o twofam_dbg twofam_dbg.c common.c ntt.c poly.c lean.c line.c split.c pallas.c -lm 2>&1 | grep -i error
timeout 1500 nice -n 10 ./twofam_dbg 2 401 > logs/dbg401.txt 2>&1 &
