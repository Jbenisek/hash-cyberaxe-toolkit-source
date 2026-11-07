#!/bin/bash
cd "$(dirname "$0")"
gcc -O3 -march=native -o freedom2 freedom2.c -lm || exit 1
/usr/bin/time -f "total %es" ./freedom2 16
