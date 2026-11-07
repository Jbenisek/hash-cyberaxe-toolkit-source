#!/bin/bash
# usage: bash test/run_bench.sh base|new c|d [steps]   builds bench_r3 against the baseline (../exec_r3f) or the variant sources and runs it (nice 10)
cd "$(dirname "$0")/.." || exit 1
HERE=$PWD
V=$1; MODE=$2; ST=${3:-2}
SRC=$HERE; [ "$V" = base ] && SRC=$HERE/../exec_r3f
mkdir -p test/out
L="common.c ntt.c poly.c lean.c line.c split.c hgcd.c pallas.c"
( cd $SRC && gcc -O3 -march=native -DARENA=300000000 -I$SRC -o $HERE/test/out/benchk_$V $HERE/test/bench_r3.c $L 2>$HERE/test/out/benchk_$V.gcc ) || { echo build failed; tail $HERE/test/out/benchk_$V.gcc; exit 2; }
/usr/bin/time -f "%e s wall, %M KB maxrss" nice -n 10 ./test/out/benchk_$V $MODE $ST > test/out/benchk_${V}_$MODE.txt 2> test/out/benchk_${V}_$MODE.err
cat test/out/benchk_${V}_$MODE.txt; tail -1 test/out/benchk_${V}_$MODE.err
