#!/bin/bash
set -e
cd "$(dirname "$0")"
gcc -O2 -march=native -Wall -Wextra -Wno-unused-function -Wno-unused-variable -o test_ntt test_ntt.c common.c ntt.c ../impl/pallas.c
./test_ntt
