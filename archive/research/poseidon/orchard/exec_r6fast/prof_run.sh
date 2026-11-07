#!/bin/bash
# Profile build and run (local WSL, nice 10).  usage: bash prof_run.sh RR T TAG [extra gcc flags]
#   builds /tmp/r6fast_prof/<TAG>/single with -DPROF -DRR=RR (arena per RR) and runs `single 1 T`; stderr has the PROFROW lines.
set -u
RR=$1; T=$2; TAG=$3; shift 3; EXTRA="$*"
SRC=$(cd "$(dirname "$0")" && pwd)
case $RR in 3) AR=290000000ULL;; 4) AR=1227182400ULL;; 5) AR=6400000000ULL;; *) AR=36500000000ULL;; esac
D=/tmp/r6fast_prof/$TAG; rm -rf $D; mkdir -p $D; cp $SRC/*.c $SRC/*.h $D/; cd $D
CF="-O3 -march=native -mcmodel=medium -static -nostdlib -fno-stack-protector -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=0 -fno-pie -no-pie -ffunction-sections -fdata-sections -Wl,--gc-sections -Wall -Wextra -Wno-unused-function -Wno-unused-variable -Wno-unused-parameter"
gcc $CF -DPROF -DRR=$RR -DARENA=$AR $EXTRA -o single single.c common.c ntt.c poly.c lean.c line.c split.c hgcd.c pallas.c par.c nolibc.c 2> build.err; echo "build rc=$? $(wc -l < build.err) warning lines"
head -5 build.err
date +%s > start.txt
( ulimit -s 64; /usr/bin/time -v nice -n 10 ./single 1 $T > out.txt 2> err.txt; echo "EXIT $?" >> out.txt )
date +%s > end.txt
echo "wall $(( $(cat end.txt) - $(cat start.txt) )) s"
grep -E "Elapsed|Maximum resident|User time|Percent of CPU" err.txt
mkdir -p $SRC/prof_out; cp out.txt $SRC/prof_out/${TAG}_out.txt; cp err.txt $SRC/prof_out/${TAG}_err.txt
