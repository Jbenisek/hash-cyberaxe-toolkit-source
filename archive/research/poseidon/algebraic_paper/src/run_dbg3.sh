#!/bin/bash
# DEBUG (not shipped): reproduce the r3 seed-2 out-of-memory. Skips the first 5 coin words (= seed 2 trial 1's centre) and prints gcd loop state on stderr.
SRC=$(cd "$(dirname "$0")" && pwd); D=/tmp/algpaper_dbg3; rm -rf $D; mkdir -p $D; cp $SRC/*.c $SRC/*.h $D/; cd $D
python3 - <<'PY'
s=open('single.c').read()
s=s.replace('    rng_seed(COIN_SEED); ','    rng_seed(COIN_SEED); { fp tmp_; rnd_fp320(&tmp_); } ')
s=s.replace('fflush(stdout);\n        if (dG < 1','fflush(stdout); fprintf(stderr,"DBG trial %d dG %zu\\n", trials, dG);\n        if (dG < 1')
open('single.c','w').write(s)
h=open('hgcd.c').read()
h=h.replace('    while (ly > 0) {\n        CTL(2);\n        size_t n = lx - 1;','    while (ly > 0) {\n        CTL(2);\n        fprintf(stderr,"DBG gcd lx=%zu ly=%zu\\n", lx, ly);\n        size_t n = lx - 1;',1)
h=h.replace('        hgcd(NULL, &c, &lc, &d, &ld, x, lx, y, ly, (n + 1) / 2, 0, 3);\n        CTL(2);','        hgcd(NULL, &c, &lc, &d, &ld, x, lx, y, ly, (n + 1) / 2, 0, 3);\n        CTL(2); fprintf(stderr,"DBG hgcd lc=%zu ld=%zu\\n", lc, ld);',1)
open('hgcd.c','w').write(h)
PY
grep -c DBG single.c hgcd.c
CF="-O3 -march=native -mcmodel=medium -static -nostdlib -fno-stack-protector -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=0 -fno-pie -no-pie -ffunction-sections -fdata-sections -Wl,--gc-sections -Wall -Wextra -Wno-unused-function -Wno-unused-variable -Wno-unused-parameter"
gcc $CF -DRR=3 -DARENA=290000000ULL -DMAXTR=2 -DCOIN_SEED=2 -o dbg3 single.c common.c ntt.c poly.c lean.c line.c split.c hgcd.c pallas.c par.c nolibc.c || exit 1
( ulimit -s 64; nice -n 10 ./dbg3 0 > dbg3_out.txt 2> dbg3_err.txt; echo "EXIT $?" >> dbg3_err.txt )
