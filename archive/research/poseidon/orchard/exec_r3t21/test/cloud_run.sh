#!/bin/bash
# Counted r3 run of exec_r3t21 on the cloud box (NOT queued yet). Expects /root/hs/r3t21.tar (this directory without test/out) already uploaded.
# Same recipe as exec_r3f/cycle.sh: gcc with the filed flags, ./single 1 under memmeter with a 64 KiB stack. ARENA 250000000 = the filed ratio (290000000 for a 236.36 MB peak) on a 202.80 MB peak.
set -e
mkdir -p /root/hs/r3t21 && cd /root/hs/r3t21
tar -xf /root/hs/r3t21.tar
CF="-O3 -march=native -static -nostdlib -fno-stack-protector -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=0 -fno-pie -no-pie -ffunction-sections -fdata-sections -Wl,--gc-sections -Wall -Wextra -Wno-unused-function -Wno-unused-variable -Wno-unused-parameter"
gcc $CF -DRR=3 -DARENA=250000000 -o single single.c common.c ntt.c poly.c lean.c line.c split.c hgcd.c pallas.c nolibc.c
date -u > start.txt
python3 /root/hs/mt/memmeter/memmeter.py --label counted -- bash -c 'ulimit -s 64; exec ./single 1 > run.tmp 2>&1' > mem.tmp 2> mem.err
echo "EXIT $?" >> run.tmp
mv run.tmp run.txt
date -u > end.txt
