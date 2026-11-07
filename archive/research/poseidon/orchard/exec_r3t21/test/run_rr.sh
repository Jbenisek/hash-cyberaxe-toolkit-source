#!/bin/bash
# usage: bash test/run_rr.sh RR   builds the baseline (../exec_r3f) and the variant with -DRR=$1, runs each once (nice 10), prints the ledger lines to compare.
cd "$(dirname "$0")/.." || exit 1
HERE=$PWD
RRV=${1:-1}
CF="-O3 -march=native -static -nostdlib -fno-stack-protector -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=0 -fno-pie -no-pie -ffunction-sections -fdata-sections -Wl,--gc-sections -Wno-unused-function -Wno-unused-variable -Wno-unused-parameter -DRR=$RRV"
LIBS="common.c ntt.c poly.c lean.c line.c split.c hgcd.c pallas.c nolibc.c"
mkdir -p test/out
( cd ../exec_r3f && gcc $CF -o $HERE/test/out/base_rr$RRV single.c $LIBS 2>$HERE/test/out/base_rr$RRV.gcc ) || { echo base build failed; exit 2; }
gcc $CF -o test/out/new_rr$RRV single.c $LIBS 2>test/out/new_rr$RRV.gcc || { echo new build failed; tail test/out/new_rr$RRV.gcc; exit 2; }
for v in base new; do
  ( ulimit -s 64; /usr/bin/time -f "%e s wall, %M KB maxrss" nice -n 10 ./test/out/${v}_rr$RRV 1 > test/out/${v}_rr$RRV.txt 2> test/out/${v}_rr$RRV.err ) &
done
wait
for v in base new; do echo "== $v rr=$RRV"; grep -E "^(COLLISION|RESULT|SUMMARY|ARENA|PEAKLIVE|TRIALS|TRIALROW 1|  [A-I]:)" test/out/${v}_rr$RRV.txt | cut -c1-200; tail -1 test/out/${v}_rr$RRV.err; done
