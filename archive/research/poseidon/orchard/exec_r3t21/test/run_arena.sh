#!/bin/bash
# stage D bench of the variant with a tight arena (default 215000000 bytes): does the allocator's fragmentation fit? usage: bash test/run_arena.sh [ARENA]
cd "$(dirname "$0")/.." || exit 1
A=${1:-215000000}
L="common.c ntt.c poly.c lean.c line.c split.c hgcd.c pallas.c"
gcc -O3 -march=native -DARENA=$A -I. -o test/out/benchA_new test/bench_r3.c $L 2>test/out/benchA_new.gcc || { echo build failed; exit 2; }
/usr/bin/time -f "%e s wall, %M KB maxrss" nice -n 10 ./test/out/benchA_new d > test/out/benchA_new_d.txt 2> test/out/benchA_new_d.err
echo "ARENA=$A"; cat test/out/benchA_new_d.txt test/out/benchA_new_d.err
