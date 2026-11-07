#!/bin/bash
cd "$(dirname "$0")"
CF="-O3 -march=native -Wall -Wextra -Wno-unused-function -Wno-unused-variable -Wno-unused-parameter"
gcc $CF -o exec_attack lean_attack.c common.c ntt.c poly.c loop.c lean.c line.c euclid.c hgcd.c pallas.c -lm
gcc $CF -o test_ntt test_ntt.c common.c ntt.c poly.c pallas.c -lm
gcc -O3 -march=native -o prof3 prof3.c common.c ntt.c poly.c pallas.c -lm
