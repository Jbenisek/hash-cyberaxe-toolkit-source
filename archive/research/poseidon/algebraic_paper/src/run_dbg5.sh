#!/bin/bash
# DEBUG (not shipped): RR=3 seed 4 (died "out of memory (50331648)") with stage names, mem_used, live, hwm on stderr at every stage_open and the gcd loop prints.
SRC=$(cd "$(dirname "$0")" && pwd); D=/tmp/algpaper_dbg5; rm -rf $D; mkdir -p $D; cp $SRC/*.c $SRC/*.h $D/; cd $D
python3 - <<'PY'
s=open('single.c').read()
s=s.replace('    stage_close(); cur = snap();','    fprintf(stderr,"DBG stage %s trial %d mem_used=%zu live=%zu hwm=%zu\\n", name, trial, mem_used, mem_live, arena_hwm); stage_close(); cur = snap();',1)
s=s.replace('fflush(stdout);\n        if (dG < 1','fflush(stdout); fprintf(stderr,"DBG trial %d dG %zu\\n", trials, dG);\n        if (dG < 1')
open('single.c','w').write(s)
PY
grep -c DBG single.c
CF="-O3 -march=native -mcmodel=medium -static -nostdlib -fno-stack-protector -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=0 -fno-pie -no-pie -ffunction-sections -fdata-sections -Wl,--gc-sections -Wall -Wextra -Wno-unused-function -Wno-unused-variable -Wno-unused-parameter"
gcc $CF -DRR=3 -DARENA=290000000ULL -DMAXTR=2 -DCOIN_SEED=4 -o dbg5 single.c common.c ntt.c poly.c lean.c line.c split.c hgcd.c pallas.c par.c nolibc.c || exit 1
( ulimit -s 64; nice -n 10 ./dbg5 0 > dbg5_out.txt 2> dbg5_err.txt; echo "EXIT $?" >> dbg5_err.txt )
