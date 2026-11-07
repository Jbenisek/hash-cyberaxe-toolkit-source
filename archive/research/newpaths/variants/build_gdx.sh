#!/bin/bash
cd "$(dirname "$0")"
gcc -O3 -march=native -o gdx gdx.c && echo built
for k in 3 4 5; do /usr/bin/time -f "%e s" ./gdx models/fixed_02_64_t0.mdl $k 0 1 5 | tail -3; done
