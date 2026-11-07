#!/bin/bash
# Arena-dependence scan at RR=3, coin seed 2 (trial-1 centre 0x3aa12224...ffdf9, which has a verified collision at ARENA 600e6 but gave gcd degree 0 at 290e6). K=1: one trial per run.
SRC=$(cd "$(dirname "$0")" && pwd)
D=/tmp/algpaper_scan; rm -rf $D; mkdir -p $D; cp $SRC/*.c $SRC/*.h $D/; cd $D; rm -f test_*.c; mkdir -p $SRC/logs
CF="-O3 -march=native -mcmodel=medium -static -nostdlib -fno-stack-protector -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=0 -fno-pie -no-pie -ffunction-sections -fdata-sections -Wl,--gc-sections -Wall -Wextra -Wno-unused-function -Wno-unused-variable -Wno-unused-parameter"
for a in 340000000 420000000 500000000; do
  n=scan_s2_a$a
  gcc $CF -DRR=3 -DARENA=${a}ULL -DMAXTR=1 -DCOIN_SEED=2 -o $n single.c common.c ntt.c poly.c lean.c line.c split.c hgcd.c pallas.c par.c nolibc.c 2> $n.err || exit 1
  ( ulimit -s 64; nice -n 10 ./$n 1 > $SRC/logs/$n.txt 2>&1; echo "EXIT $?" >> $SRC/logs/$n.txt ) &
done
wait
