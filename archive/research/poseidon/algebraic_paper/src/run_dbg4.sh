#!/bin/bash
# DEBUG (not shipped): print mem_used / mem_live / arena_hwm on stderr at the start of every trial (leak / fragmentation check), RR=1, seed 4 (2 failed trials then success), K=8.
SRC=$(cd "$(dirname "$0")" && pwd); D=/tmp/algpaper_dbg4; rm -rf $D; mkdir -p $D; cp $SRC/*.c $SRC/*.h $D/; cd $D
python3 - <<'PY'
s=open('single.c').read()
s=s.replace('stage_open("A: centre from coins", trials);','fprintf(stderr,"DBG trial %d start mem_used=%zu live=%zu hwm=%zu\\n", trials, mem_used, mem_live, arena_hwm); stage_open("A: centre from coins", trials);')
open('single.c','w').write(s)
PY
grep -c DBG single.c
CF="-O3 -march=native -mcmodel=medium -static -nostdlib -fno-stack-protector -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=0 -fno-pie -no-pie -ffunction-sections -fdata-sections -Wl,--gc-sections -Wall -Wextra -Wno-unused-function -Wno-unused-variable -Wno-unused-parameter"
gcc $CF -DRR=1 -DARENA=200000000ULL -DMAXTR=8 -DCOIN_SEED=4 -o dbg4 single.c common.c ntt.c poly.c lean.c line.c split.c hgcd.c pallas.c par.c nolibc.c || exit 1
( ulimit -s 64; ./dbg4 0 > out.txt 2> err.txt; echo "EXIT $?" >> err.txt ); cat err.txt; grep -E "^trial" out.txt
