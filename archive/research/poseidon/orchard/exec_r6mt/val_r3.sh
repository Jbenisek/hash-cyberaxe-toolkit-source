set -u
SRC=$(cd "$(dirname "$0")" && pwd)
D=/tmp/r6val; rm -rf $D; mkdir -p $D; cp $SRC/*.c $SRC/*.h $D/; cd $D
CF="-O3 -march=native -mcmodel=medium -static -nostdlib -fno-stack-protector -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=0 -fno-pie -no-pie -ffunction-sections -fdata-sections -Wl,--gc-sections -Wall -Wextra -Wno-unused-function -Wno-unused-variable -Wno-unused-parameter"
gcc $CF -DRR=3 -DARENA=290000000ULL -o single_r3 single.c common.c ntt.c poly.c lean.c line.c split.c hgcd.c pallas.c par.c nolibc.c 2> build_r3.err; echo build_r3 rc=$?; size single_r3
gcc $CF -o single_r6 single.c common.c ntt.c poly.c lean.c line.c split.c hgcd.c pallas.c par.c nolibc.c 2> build_r6.err; echo build_r6 rc=$?; size single_r6; cat build_r6.err | head
date > start.txt
( ulimit -s 64; nice -n 10 ./single_r3 1 4 > out4.txt 2>&1; echo EXIT $? >> out4.txt; date > end.txt )
