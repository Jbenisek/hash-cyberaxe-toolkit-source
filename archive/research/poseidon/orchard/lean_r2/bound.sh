#!/bin/bash
# builds and runs the budget derivations: bound.sh r
set -e
cd "$(dirname "$0")"
CF="-O3 -march=native -Wall -Wextra -Wno-unused-function -Wno-unused-variable -Wno-unused-parameter -Wno-unused-but-set-variable"
LIBS="common.c ntt.c poly.c loop.c lean.c line.c euclid.c pallas.c"
gcc $CF -o bound_gcd bound_gcd.c $LIBS -lm
gcc $CF -DROOT_TRIES=1 -o bound_root bound_root.c $LIBS -lm
./bound_gcd $1
./bound_root
