#!/bin/bash
set -e
cd "$(dirname "$0")"
CF="-O2 -march=native -Wall -Wextra -Wno-unused-function -Wno-unused-variable -Wno-unused-parameter"
TGT=${1:-attack}; shift || true
gcc $CF -o $TGT $TGT.c common.c ntt.c poly.c loop.c line.c euclid.c $EXTRA pallas.c -lm "$@"
