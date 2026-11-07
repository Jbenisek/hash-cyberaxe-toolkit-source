#!/bin/bash
cd "$(dirname "$0")"
gcc -O3 -march=native -o corex corex.c 2>&1 | grep -i error
timeout 1000 ./corex models/fixed_02_64_t0.mdl 3 6 > res/corex_fixed02_r3e6.sol 2> res/corex_fixed02_r3e6.log
tail -3 res/corex_fixed02_r3e6.log; grep -c '^SOL' res/corex_fixed02_r3e6.sol
timeout 600 ./split models/fixed_02_64_t0.mdl res/corex_fixed02_r3e6.sol 4 64 200000 > res/split_corex_fixed02_r3e6.txt; tail -2 res/split_corex_fixed02_r3e6.txt
