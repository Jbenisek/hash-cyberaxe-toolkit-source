#!/bin/sh
# Build and run the K3 stage scan (one process). Args are passed to k3_scan.
set -e
cd "$(dirname "$0")"
gcc -O3 -march=native -std=gnu11 -Wall -o k3_scan k3_scan.c
start=$(date +%s)
./k3_scan "$@"
end=$(date +%s)
echo "wall=$((end - start))s"
