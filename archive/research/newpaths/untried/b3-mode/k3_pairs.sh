#!/bin/sh
# K3 scans: pairs "<h7 hex> <dx hex>" given as arguments, one process at a time.
# Usage: k3_pairs.sh <flags> <h7> <dx> [<h7> <dx> ...]
cd "$(dirname "$0")"
gcc -O3 -march=native -std=gnu11 -Wall -o k3_scan k3_scan.c
flags=$1; shift
start=$(date +%s)
while [ $# -ge 2 ]; do
  ./k3_scan "$flags" "$2" 0 100000000 "$1"
  shift 2
done
end=$(date +%s)
echo "total wall=$((end - start))s"