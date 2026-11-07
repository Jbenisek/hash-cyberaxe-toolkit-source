#!/bin/bash
cd "$(dirname "$0")"
./build.sh bench_pow.c || exit 1
time ./bench_pow 7812 14
time ./bench_pow 39062 16
