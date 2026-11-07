#!/bin/bash
cd "$(dirname "$0")"
OUT=${1:-single_cap6}; shift
gcc -O3 -march=native -Wall -Wextra -Wno-unused-function -Wno-unused-variable -Wno-unused-parameter -DDEG_CAP=6 "$@" -o $OUT single.c common.c ntt.c poly.c lean.c line.c split.c hgcd.c pallas.c -lm
