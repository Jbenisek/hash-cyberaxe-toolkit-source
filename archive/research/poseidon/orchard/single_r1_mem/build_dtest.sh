#!/bin/bash
cd "$(dirname "$0")"
OUT=${1:-dtest}; shift
gcc -O3 -march=native -g -no-pie -Wall -Wextra -Wno-unused-function -Wno-unused-variable -Wno-unused-parameter "$@" -o $OUT dtest.c common.c ntt.c poly.c hgcd.c pallas.c -lm
