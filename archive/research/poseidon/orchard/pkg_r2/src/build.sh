#!/bin/bash
# usage: build.sh target.c [extra.c...]
cd "$(dirname "$0")"
t=$1; shift
gcc -O3 -march=native -Wall -Wextra -Wno-unused-function -Wno-unused-variable -Wno-unused-parameter -o "${t%.c}" "$t" common.c ntt.c poly.c loop.c pallas.c "$@" -lm
