#!/bin/bash
# RR=3 test with more coin seeds (K=2, one process per seed, one thread, nice 10, ulimit -s 64). Edit SEEDS below. Output logs/r3_s<seed>.txt
SRC=$(cd "$(dirname "$0")" && pwd); SEEDS="4 5"
D=/tmp/algpaper_more; rm -rf $D; mkdir -p $D; cp $SRC/*.c $SRC/*.h $D/; cd $D; mkdir -p $SRC/logs
CF="-O3 -march=native -mcmodel=medium -static -nostdlib -fno-stack-protector -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=0 -fno-pie -no-pie -ffunction-sections -fdata-sections -Wl,--gc-sections -Wall -Wextra -Wno-unused-function -Wno-unused-variable -Wno-unused-parameter"
for s in $SEEDS; do
  gcc $CF -DRR=3 -DARENA=290000000ULL -DMAXTR=2 -DCOIN_SEED=$s -o single_r3_s$s single.c common.c ntt.c poly.c lean.c line.c split.c hgcd.c pallas.c par.c nolibc.c 2> build_s$s.err || exit 1
  ( ulimit -s 64; date -u > $SRC/logs/r3_s$s.start; nice -n 10 ./single_r3_s$s 1 > $SRC/logs/r3_s$s.txt 2>&1; echo "EXIT $?" >> $SRC/logs/r3_s$s.txt; date -u > $SRC/logs/r3_s$s.end ) &
done
wait
