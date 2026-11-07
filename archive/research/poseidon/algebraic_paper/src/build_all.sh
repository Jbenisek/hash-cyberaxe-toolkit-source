#!/bin/bash
# Build the algebraic-paper program for RR=3 (r3 arena, as exec_r6mt/val_r3.sh) and RR=7, RR=8 (build-only: arena and bss link check).
# Flags are those of exec_r6mt (cycle.sh / build_cloud_r6.sh). Run:  wsl -d Ubuntu -- bash build_all.sh
# Optional env: MAXTR_K (K, default 2), SEEDS (space separated coin seeds for extra RR=3 binaries, default "1 2 3")
set -u
SRC=$(cd "$(dirname "$0")" && pwd)
D=/tmp/algpaper; rm -rf $D; mkdir -p $D; cp $SRC/*.c $SRC/*.h $D/; cd $D
CF="-O3 -march=native -mcmodel=medium -static -nostdlib -fno-stack-protector -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=0 -fno-pie -no-pie -ffunction-sections -fdata-sections -Wl,--gc-sections -Wall -Wextra -Wno-unused-function -Wno-unused-variable -Wno-unused-parameter"
SRCS="single.c common.c ntt.c poly.c lean.c line.c split.c hgcd.c pallas.c par.c nolibc.c"
K=${MAXTR_K:-2}
for s in ${SEEDS:-1 2 3}; do
  gcc $CF -DRR=3 -DARENA=290000000ULL -DMAXTR=$K -DCOIN_SEED=$s -o single_r3_s$s $SRCS 2> build_r3_s$s.err; echo "build_r3 seed=$s K=$K rc=$? warnings_lines=$(wc -l < build_r3_s$s.err)"; size single_r3_s$s
done
# r7: live peak ~136e9 (README), arena 160e9 ; r8: live peak ~602e9, arena 710e9 (formula of R6_PLAN.md section 2, AMAX 29 / 31)
gcc $CF -DRR=7 -DARENA=160000000000ULL -DMAXTR=$K -o single_r7 $SRCS 2> build_r7.err; echo "build_r7 rc=$? warnings_lines=$(wc -l < build_r7.err)"; size single_r7
gcc $CF -DRR=8 -DARENA=710000000000ULL -DMAXTR=$K -o single_r8 $SRCS 2> build_r8.err; echo "build_r8 rc=$? warnings_lines=$(wc -l < build_r8.err)"; size single_r8
head -20 build_r3_s1.err build_r7.err build_r8.err
sha256sum single_r3_s* single_r7 single_r8
