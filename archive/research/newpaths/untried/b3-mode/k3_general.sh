#!/bin/sh
# Build and run k3_general (one process). Args: <log2 trials> <seed>
set -e
cd "$(dirname "$0")"
gcc -O3 -march=native -std=gnu11 -Wall -o k3_general k3_general.c -lm
./k3_general "$@"