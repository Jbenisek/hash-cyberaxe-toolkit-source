#!/bin/bash
# DEBUG build (not shipped): single.c copy with progress lines on stderr (immediate). RRX=2 seeds from $SEEDS. wsl -d Ubuntu -- bash run_dbg.sh
SRC=$(cd "$(dirname "$0")" && pwd); RRX=${RRX:-2}; D=/tmp/algpaper_dbg$RRX; rm -rf $D; mkdir -p $D; cp $SRC/*.c $SRC/*.h $D/; cd $D
python3 - <<'PY'
s=open('single.c').read()
s=s.replace('fflush(stdout);\n        if (dG < 1','fflush(stdout); fprintf(stderr,"DBG trial %d dG %zu\\n", trials, dG);\n        if (dG < 1')
s=s.replace('        CTL(2);\n        if (!found) continue;','        CTL(2); fprintf(stderr,"DBG E found=%d\\n", found);\n        if (!found) continue;')
s=s.replace('        success = found && same_dg && !same_in;','        success = found && same_dg && !same_in; fprintf(stderr,"DBG G same_dg=%d same_in=%d sq=%d\\n", same_dg, same_in, sq);')
open('single.c','w').write(s)
PY
grep -c DBG single.c
CF="-O3 -march=native -mcmodel=medium -static -nostdlib -fno-stack-protector -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=0 -fno-pie -no-pie -ffunction-sections -fdata-sections -Wl,--gc-sections -Wall -Wextra -Wno-unused-function -Wno-unused-variable -Wno-unused-parameter"
for s in ${SEEDS:-1 2}; do
  gcc $CF -DRR=$RRX -DARENA=${ARENA:-200000000ULL} -DMAXTR=${K:-8} -DCOIN_SEED=$s -o dbg_s$s single.c common.c ntt.c poly.c lean.c line.c split.c hgcd.c pallas.c par.c nolibc.c || exit 1
  ( ulimit -s 64; nice -n 10 ./dbg_s$s 0 > dbg_out_s$s.txt 2> dbg_err_s$s.txt; echo "EXIT $?" >> dbg_err_s$s.txt ) &
done
wait
