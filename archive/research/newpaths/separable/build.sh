#!/bin/bash
cd "$(dirname "$0")"
for p in split fullsets jtree kdiag lsearch; do gcc -O3 -march=native -o $p $p.c || echo FAIL $p; done
./split sys_fixed_t2.txt stats 1 | head -3
