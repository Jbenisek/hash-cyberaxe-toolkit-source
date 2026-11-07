#!/bin/bash
# debug: RR=1 (RRX), MAXTR=K (default 8), random tapes from /dev/urandom, quick check of the coin-tape program: RRX=1 K=8 bash small_r1.sh
T=$(cd "$(dirname "$0")" && pwd); SRC=$T/../src; RRX=${RRX:-1}; D=/tmp/algpaper_v3_small$RRX; rm -rf $D; mkdir -p $D; cp $SRC/*.c $SRC/*.h $D/; cd $D
CF="-O3 -march=native -mcmodel=medium -static -nostdlib -fno-stack-protector -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=0 -fno-pie -no-pie -ffunction-sections -fdata-sections -Wl,--gc-sections -Wall -Wextra -Wno-unused-function -Wno-unused-variable -Wno-unused-parameter"
K=${K:-8}
gcc $CF -DRR=$RRX -DARENA=${ARENA:-200000000ULL} -DMAXTR=$K -o single_small single.c common.c ntt.c poly.c lean.c line.c split.c hgcd.c pallas.c par.c nolibc.c || exit 1
for i in 1 2 3 4 5 6; do head -c $((K*65*5*8)) /dev/urandom > tape$i.bin; ( ulimit -s 64; ./single_small 0 < tape$i.bin > out$i.txt 2>&1; echo "EXIT $?" >> out$i.txt; echo "tape $i: $(grep -E '^trial |^EXIT|^RESULT|^COINS' out$i.txt | tr '\n' '|')" ); done
