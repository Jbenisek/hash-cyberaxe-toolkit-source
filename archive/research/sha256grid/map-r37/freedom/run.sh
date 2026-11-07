#!/bin/bash
cd "$(dirname "$0")"
gcc -O3 -march=native -o freedom freedom.c || exit 1
for k in 0 1 2 3; do /usr/bin/time -f "k=$k %es" ./freedom $k; done
