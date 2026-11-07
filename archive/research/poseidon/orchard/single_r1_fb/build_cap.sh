#!/bin/bash
# cap variant (the main entry): binary single_cap6
set -e
cd "$(dirname "$0")"
gcc -O3 -march=native -Wall -Wextra -Wno-unused-function -Wno-unused-variable -Wno-unused-parameter -DDEG_CAP=6 -o single_cap6 single.c common.c ntt.c poly.c lean.c line.c split.c hgcd.c pallas.c -lm
