#!/bin/bash
set -e
cd "$(dirname "$0")"
gcc -O2 -march=native -Wall -Wextra -Wno-unused-function -Wno-unused-variable -o test_loop test_loop.c common.c ntt.c poly.c loop.c ../impl/pallas.c
./test_loop
