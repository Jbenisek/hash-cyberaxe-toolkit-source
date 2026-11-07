#!/bin/bash
set -e
cd "$(dirname "$0")"
CF="-O3 -march=native -Wall -Wextra -Wno-unused-function -Wno-unused-variable -Wno-unused-parameter"
T=$1; shift || true
gcc $CF -o $T $T.c common.c ntt.c poly.c lean.c line.c split.c pallas.c "$@" -lm
