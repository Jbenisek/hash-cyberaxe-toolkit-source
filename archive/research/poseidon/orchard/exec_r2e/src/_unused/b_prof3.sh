#!/bin/bash
cd "$(dirname "$0")"
gcc -O3 -march=native -o prof3 prof3.c common.c ntt.c poly.c pallas.c -lm && ./prof3
