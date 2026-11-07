#!/bin/bash
cd "$(dirname "$0")"
gcc -O3 -march=native -o corex corex.c 2>&1 | grep -i error
m=part_02_t0_Y13
timeout 900 ./corex models/$m.mdl 2 7 1 > res/corex_${m}_r2e7.sol 2> res/corex_${m}_r2e7.log &
timeout 900 ./corex models/$m.mdl 3 6 1 > res/corex_${m}_r3e6.sol 2> res/corex_${m}_r3e6.log &
wait
for f in res/corex_${m}_r2e7 res/corex_${m}_r3e6; do tail -1 $f.log; n=$(grep -c '^SOL' $f.sol); echo "$f sets $n";
  if [ "$n" != "0" ]; then timeout 900 ./split models/$m.mdl $f.sol 5 80 200000 > res/split_$(basename $f).txt; tail -2 res/split_$(basename $f).txt; fi; done
