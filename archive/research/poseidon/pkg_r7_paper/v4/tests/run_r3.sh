#!/bin/bash
# RR=3 test of the program of Appendix A with RANDOM coin tapes: builds single_r3 (MAXTR=2, ARENA=600000000, no seed: the tape is read from standard input), makes N tapes of
# COIN_BYTES random bytes from /dev/urandom (tests/r3/tape_<i>.bin), and runs one single-thread process per tape (nice 10, ulimit -s 64): ./single_r3 1 < tape_<i>.bin.
# Output: tests/r3/run_<i>.txt (program output + EXIT line), start/end times.   wsl -d Ubuntu -- bash run_r3.sh
T=$(cd "$(dirname "$0")" && pwd); SRC=$T/../src; D=/tmp/algpaper_v3_r3; rm -rf $D; mkdir -p $D $T/r3; cp $SRC/*.c $SRC/*.h $D/; cd $D || exit 1
CF="-O3 -march=native -mcmodel=medium -static -nostdlib -fno-stack-protector -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=0 -fno-pie -no-pie -ffunction-sections -fdata-sections -Wl,--gc-sections -Wall -Wextra -Wno-unused-function -Wno-unused-variable -Wno-unused-parameter"
gcc $CF -DRR=3 -DARENA=600000000ULL -DMAXTR=2 -o single_r3 single.c common.c ntt.c poly.c lean.c line.c split.c hgcd.c pallas.c par.c nolibc.c 2> build.err; echo "build rc=$? warning_lines=$(wc -l < build.err)"; size single_r3; sha256sum single_r3
for i in ${TAPES:-1 2 3 4 5 6 7 8}; do
  [ -f $T/r3/tape_$i.bin ] || head -c 5200 /dev/urandom > $T/r3/tape_$i.bin
  ( ulimit -s 64; date -u > $T/r3/run_$i.start; nice -n 10 ./single_r3 1 < $T/r3/tape_$i.bin > $T/r3/run_$i.txt 2>&1; echo "EXIT $?" >> $T/r3/run_$i.txt; date -u > $T/r3/run_$i.end ) &
done
wait
