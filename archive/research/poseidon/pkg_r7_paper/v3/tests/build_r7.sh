#!/bin/bash
# build-only check of the shipped sources at r = 7 with the ledger arena (wsl -d Ubuntu -- bash build_r7.sh); prints size and a sha256 prefix of the binary
SRC=$(cd "$(dirname "$0")/../src" && pwd); D=/tmp/algpaper_v3_r7; rm -rf $D; mkdir -p $D; cp $SRC/*.c $SRC/*.h $D/; cd $D
CF="-O3 -march=native -mcmodel=medium -static -nostdlib -fno-stack-protector -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=0 -fno-pie -no-pie -ffunction-sections -fdata-sections -Wl,--gc-sections -Wall -Wextra -Wno-unused-function -Wno-unused-variable -Wno-unused-parameter"
gcc $CF -DRR=7 -DARENA=${ARENA:-159958022720}ULL -DMAXTR=2 -o single_r7 single.c common.c ntt.c poly.c lean.c line.c split.c hgcd.c pallas.c par.c nolibc.c 2> build.err; echo "rc=$? warning_lines=$(wc -l < build.err)"; head -5 build.err
size single_r7; sha256sum single_r7 | cut -c1-16
