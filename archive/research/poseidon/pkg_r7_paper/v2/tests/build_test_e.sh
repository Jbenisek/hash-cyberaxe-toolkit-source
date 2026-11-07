#!/bin/bash
# wsl -d Ubuntu -- bash build_test_e.sh   (builds tests/test_e.c against ../src with a small arena and runs it)
SRC=$(cd "$(dirname "$0")/../src" && pwd); T=$(cd "$(dirname "$0")" && pwd); D=/tmp/algpaper_v2_e; rm -rf $D; mkdir -p $D; cp $SRC/*.c $SRC/*.h $D/; cp $T/test_e.c $D/; cd $D; rm single.c
CF="-O3 -g -march=native -mcmodel=medium -static -nostdlib -fno-stack-protector -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=0 -fno-pie -no-pie -Wall -Wextra -Wno-unused-function -Wno-unused-variable -Wno-unused-parameter"
gcc $CF -DRR=3 -DARENA=290000000ULL -o test_e test_e.c common.c ntt.c poly.c lean.c line.c split.c hgcd.c pallas.c par.c nolibc.c || exit 1
( ulimit -s 64; ./test_e; echo EXIT $? )
