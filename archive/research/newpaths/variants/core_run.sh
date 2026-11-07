#!/bin/bash
cd "$(dirname "$0")"
gcc -O3 -march=native -o core core.c 2>/dev/null
for m in fixed_02_64_t0 fixed_02_64_t1 part_02_t0_Y13; do echo "== $m"; timeout 100 ./core models/$m.mdl 4; done > res/core.txt
cat res/core.txt
