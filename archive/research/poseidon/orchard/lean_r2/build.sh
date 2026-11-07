#!/bin/bash
# usage: build.sh target [extra.c...]   (builds target.c with the shared library files)
set -e
cd "$(dirname "$0")"
CF="-O3 -march=native -Wall -Wextra -Wno-unused-function -Wno-unused-variable -Wno-unused-parameter"
T=$1; shift || true
gcc $CF -o $T $T.c common.c ntt.c poly.c loop.c lean.c line.c euclid.c hgcd.c pallas.c "$@" -lm
