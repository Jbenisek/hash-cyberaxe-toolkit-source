#!/bin/bash
# Algorithmic identity of the new splits (local WSL, nice 10): RR=$1 (default 2); builds NO_R2 (old plans, new splits) and default (rows 2, new splits);
# runs each at T=1 and T=$2 (default 3) and prints algorithmic_total, thread_control and the md5 of the COLLISION lines.
set -u
RR=${1:-2}; T=${2:-3}
SRC=$(cd "$(dirname "$0")" && pwd)
D=/tmp/r6fast_mt_$RR; rm -rf $D; mkdir -p $D; cp $SRC/*.c $SRC/*.h $D/; cd $D
CF="-O3 -march=native -mcmodel=medium -static -nostdlib -fno-stack-protector -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=0 -fno-pie -no-pie -ffunction-sections -fdata-sections -Wl,--gc-sections -Wall -Wextra -Wno-unused-function -Wno-unused-variable -Wno-unused-parameter"
L="single.c common.c ntt.c poly.c lean.c line.c split.c hgcd.c pallas.c par.c nolibc.c"
gcc $CF -DRR=$RR -DARENA=290000000ULL -DNO_R2 -o old $L 2>>b.err; gcc $CF -DRR=$RR -DARENA=290000000ULL -o r2 $L 2>>b.err
echo "build warnings $(grep -c warning b.err)"
for V in old r2; do for TT in 1 $T; do
  ( ulimit -s 64; nice -n 10 ./$V 1 $TT > o_${V}_$TT.txt 2>&1 )
  echo "$V T=$TT: $(grep -a -E '^trial' o_${V}_$TT.txt | tr '\n' ' ') | $(grep -a -o 'algorithmic_total=[0-9]*' o_${V}_$TT.txt) $(grep -a -o 'thread_control=[0-9]*' o_${V}_$TT.txt) | md5 $(grep -a COLLISION o_${V}_$TT.txt | md5sum | cut -c1-12)"
done; done
