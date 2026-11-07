#!/bin/sh
# Full K3 scans for several x-differences, one after another (one process at a time).
# Usage: k3_multi.sh <flags> <dx hex> [<dx hex> ...]
cd "$(dirname "$0")"
gcc -O3 -march=native -std=gnu11 -Wall -o k3_scan k3_scan.c
flags=$1; shift
start=$(date +%s)
for dx in "$@"; do
  ./k3_scan "$flags" "$dx"
done
end=$(date +%s)
echo "total wall=$((end - start))s"
