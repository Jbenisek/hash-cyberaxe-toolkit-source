#!/bin/bash
# debug runs at small RR (RRX, default 2) on given seeds in parallel (one process each): RRX=2 SEEDS="1 2 3" K=8 ARENA=... bash run_small.sh
SRC=$(cd "$(dirname "$0")" && pwd); RRX=${RRX:-2}; D=/tmp/algpaper_small$RRX; rm -rf $D; mkdir -p $D; cp $SRC/*.c $SRC/*.h $D/; cd $D
CF="-O3 -march=native -mcmodel=medium -static -nostdlib -fno-stack-protector -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=0 -fno-pie -no-pie -ffunction-sections -fdata-sections -Wl,--gc-sections -Wall -Wextra -Wno-unused-function -Wno-unused-variable -Wno-unused-parameter"
for s in ${SEEDS:-1 2 3}; do
  gcc $CF -DRR=$RRX -DARENA=${ARENA:-200000000ULL} -DMAXTR=${K:-8} -DCOIN_SEED=$s -o single_s$s single.c common.c ntt.c poly.c lean.c line.c split.c hgcd.c pallas.c par.c nolibc.c || exit 1
  ( ulimit -s 64; nice -n 10 ./single_s$s 0 > out_s$s.txt 2>&1; echo "EXIT $?" >> out_s$s.txt; echo "RR=$RRX seed $s: $(grep -E '^trial |^EXIT|out of memory|^RESULT' out_s$s.txt | tr '\n' '|')" ) &
done
wait
