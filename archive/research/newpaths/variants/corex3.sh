#!/bin/bash
# finish the Y13 release: all 2-word cores with one internal check, extended by 7 words; then split (F=5, N=2^80)
cd "$(dirname "$0")"
gcc -O3 -march=native -o split split.c 2>&1 | grep -i error
gcc -O3 -march=native -o corex corex.c 2>&1 | grep -i error
m=part_02_t0_Y13
timeout 3000 ./corex models/$m.mdl 2 7 1 > res/corex_${m}_r2e7_full.sol 2> res/corex_${m}_r2e7_full.log
echo "corex exit $?" >> res/corex_${m}_r2e7_full.log
timeout 2400 ./split models/$m.mdl res/corex_${m}_r2e7_full.sol 5 80 > res/split_corex_${m}_r2e7_full.txt
tail -2 res/split_corex_${m}_r2e7_full.txt
echo COREX3DONE
