#!/bin/bash
# variant forced to rows==2 plans only (-DNO_R3) at RR=$1: same collision expected; compares with the baseline binary from run_rr.sh
cd "$(dirname "$0")/.." || exit 1
RRV=${1:-1}
CF="-O3 -march=native -static -nostdlib -fno-stack-protector -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=0 -fno-pie -no-pie -ffunction-sections -fdata-sections -Wl,--gc-sections -Wno-unused-function -Wno-unused-variable -Wno-unused-parameter -DRR=$RRV -DNO_R3 -DAMAX=17"
LIBS="common.c ntt.c poly.c lean.c line.c split.c hgcd.c pallas.c nolibc.c"
gcc $CF -o test/out/r2only_rr$RRV single.c $LIBS 2>test/out/r2only_rr$RRV.gcc || { echo build failed; tail test/out/r2only_rr$RRV.gcc; exit 2; }
( ulimit -s 64; /usr/bin/time -f "%e s wall, %M KB maxrss" nice -n 10 ./test/out/r2only_rr$RRV 1 > test/out/r2only_rr$RRV.txt 2> test/out/r2only_rr$RRV.err )
grep -E "^(COLLISION|RESULT|SUMMARY|  [CD]:)" test/out/r2only_rr$RRV.txt | cut -c1-200; tail -1 test/out/r2only_rr$RRV.err
