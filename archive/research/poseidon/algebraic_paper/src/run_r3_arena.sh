#!/bin/bash
# RR=3 test, K=2, one process per run: (seed, arena bytes) pairs below. Output logs/r3_s<seed>_a<arena>.txt . One thread, nice 10, ulimit -s 64, argument 1 as the shipped runs.
SRC=$(cd "$(dirname "$0")" && pwd)
D=/tmp/algpaper_arena; rm -rf $D; mkdir -p $D; cp $SRC/*.c $SRC/*.h $D/; cd $D; mkdir -p $SRC/logs
CF="-O3 -march=native -mcmodel=medium -static -nostdlib -fno-stack-protector -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=0 -fno-pie -no-pie -ffunction-sections -fdata-sections -Wl,--gc-sections -Wall -Wextra -Wno-unused-function -Wno-unused-variable -Wno-unused-parameter"
for pair in "4 600000000" "2 600000000" "6 290000000"; do
  set -- $pair; s=$1; a=$2; n=r3_s${s}_a${a}
  gcc $CF -DRR=3 -DARENA=${a}ULL -DMAXTR=2 -DCOIN_SEED=$s -o $n single.c common.c ntt.c poly.c lean.c line.c split.c hgcd.c pallas.c par.c nolibc.c 2> $n.err || exit 1
  ( ulimit -s 64; date -u > $SRC/logs/$n.start; nice -n 10 ./$n 1 > $SRC/logs/$n.txt 2>&1; echo "EXIT $?" >> $SRC/logs/$n.txt; date -u > $SRC/logs/$n.end ) &
done
wait
