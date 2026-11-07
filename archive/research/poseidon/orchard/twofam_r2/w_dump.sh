#!/bin/bash
cd "$(dirname "$0")"
gcc -O3 -march=native -w -o twofam_dump twofam_dump.c common.c ntt.c poly.c lean.c line.c split.c pallas.c -lm 2>&1 | grep -i error
setsid nohup bash -c 'nice -n 10 ./twofam_dump 2 401 > logs/dump401.txt 2>&1' > /dev/null 2>&1 < /dev/null &
sleep 1; pgrep -a twofam_dump
