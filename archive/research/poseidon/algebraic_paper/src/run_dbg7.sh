#!/bin/bash
# DEBUG (not shipped): print the trial-1 centre (canonical limbs) for seed 2 at ARENA 290e6 and 600e6, then stop each run after the print (own PIDs only).
SRC=$(cd "$(dirname "$0")" && pwd); D=/tmp/algpaper_dbg7; rm -rf $D; mkdir -p $D; cp $SRC/*.c $SRC/*.h $D/; cd $D
python3 - <<'PY'
s=open('single.c').read()
s=s.replace('rnd_fp320(&c);','rnd_fp320(&c); { uint64_t v_[4]; fp_to_limbs(v_, &c); fprintf(stderr, "DBG centre %016llx%016llx%016llx%016llx\\n", (unsigned long long)v_[3], (unsigned long long)v_[2], (unsigned long long)v_[1], (unsigned long long)v_[0]); }',1)
open('single.c','w').write(s)
PY
grep -c DBG single.c
CF="-O3 -march=native -mcmodel=medium -static -nostdlib -fno-stack-protector -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=0 -fno-pie -no-pie -ffunction-sections -fdata-sections -Wl,--gc-sections -Wall -Wextra -Wno-unused-function -Wno-unused-variable -Wno-unused-parameter"
for a in 290000000 600000000; do
  gcc $CF -DRR=3 -DARENA=${a}ULL -DMAXTR=2 -DCOIN_SEED=2 -o dbg7_$a single.c common.c ntt.c poly.c lean.c line.c split.c hgcd.c pallas.c par.c nolibc.c || exit 1
  ( ulimit -s 64; ./dbg7_$a 1 > out_$a.txt 2> err_$a.txt & pid=$!; sleep 150; kill $pid; echo "arena $a: $(cat err_$a.txt)" )
done
