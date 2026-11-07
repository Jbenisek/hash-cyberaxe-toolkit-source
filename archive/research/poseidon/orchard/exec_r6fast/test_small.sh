#!/bin/bash
# Small-r checks (local WSL, nice 10): RR = 1, 2 with the old plans (-DNO_R2), rows 2 (default) and rows 2 forced (-DNO_R3, AMAX + 1); T = 1 and 4.
set -u
SRC=$(cd "$(dirname "$0")" && pwd)
D=/tmp/r6fast_small; rm -rf $D; mkdir -p $D; cp $SRC/*.c $SRC/*.h $D/; cd $D
CF="-O3 -march=native -mcmodel=medium -static -nostdlib -fno-stack-protector -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=0 -fno-pie -no-pie -ffunction-sections -fdata-sections -Wl,--gc-sections -Wall -Wextra -Wno-unused-function -Wno-unused-variable -Wno-unused-parameter"
L="single.c common.c ntt.c poly.c lean.c line.c split.c hgcd.c pallas.c par.c nolibc.c"
for RR in ${RRS:-1 2}; do
  case $RR in 1) AM=15;; 2) AM=17;; 3) AM=20;; esac
  gcc $CF -DRR=$RR -DARENA=290000000ULL -DNO_R2 -o old_$RR $L 2>>build.err
  gcc $CF -DRR=$RR -DARENA=290000000ULL -o r2_$RR $L 2>>build.err
  gcc $CF -DRR=$RR -DARENA=290000000ULL -DNO_R3 -DAMAX=$((AM+1)) -o f2_$RR $L 2>>build.err
done
echo "build warnings: $(wc -l < build.err)"; head -5 build.err
for RR in ${RRS:-1 2}; do for V in old r2 f2; do for T in ${TS:-1 4}; do
  ( ulimit -s 64; nice -n 10 ./${V}_$RR 1 $T > o_${V}_${RR}_$T.txt 2>&1; echo "EXIT $?" >> o_${V}_${RR}_$T.txt )
  echo "== RR=$RR $V T=$T: $(grep -c COLLISION o_${V}_${RR}_$T.txt) collision lines, md5 $(grep COLLISION o_${V}_${RR}_$T.txt | md5sum | cut -c1-12) $(grep -E '^EXIT' o_${V}_${RR}_$T.txt)"
  grep -E "SUMMARY|THREADS n|TRIALS" o_${V}_${RR}_$T.txt | sed 's/^/   /'
done; done; done
