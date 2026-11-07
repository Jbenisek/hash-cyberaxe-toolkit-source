#!/bin/bash
# builds /tmp/r6fast_chk/{base,fast}_chk from exec_r6fast sources: base = -DNO_R2 -DNO_TK -DNO_ST and the exec_r6mt thresholds, fast = default
SRC=$(cd "$(dirname "$0")/.." && pwd); D=/tmp/r6fast_chk; rm -rf $D; mkdir -p $D/test; cp $SRC/*.c $SRC/*.h $D/; cp $SRC/test/bench_chk.c $D/test/; cd $D
CF="-O3 -march=native -mcmodel=medium -static -nostdlib -fno-stack-protector -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=0 -fno-pie -no-pie -ffunction-sections -fdata-sections -Wl,--gc-sections -w -DARENA=400000000ULL -DAMAX=21"
L="common.c ntt.c poly.c lean.c line.c split.c hgcd.c pallas.c par.c nolibc.c"
gcc $CF -DNO_R2 -DNO_TK -DNO_ST -DPAR_LMIN_ELEM=15 -DPAR_LMIN_LIN=17 -o base_chk test/bench_chk.c $L && gcc $CF -o fast_chk test/bench_chk.c $L && echo built && ls -la base_chk fast_chk
# split = unchanged plans (-DNO_R2) with the new splits; r4-size builds with AMAX=23
gcc $CF -DNO_R2 -o split_chk test/bench_chk.c $L && echo built split
CF4=$(echo "$CF" | sed 's/-DAMAX=21/-DAMAX=23/; s/-DARENA=400000000ULL/-DARENA=2000000000ULL/')
gcc $CF4 -DNO_R2 -DNO_TK -DNO_ST -DPAR_LMIN_ELEM=15 -DPAR_LMIN_LIN=17 -o base4_chk test/bench_chk.c $L && gcc $CF4 -DNO_R2 -o split4_chk test/bench_chk.c $L && gcc $CF4 -o fast4_chk test/bench_chk.c $L && echo built r4 && ls -la *_chk
