#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# run_tower.sh <log2 samples> <seed> <outname>   (writes tower_<outname>.txt and a timing line)
set -e
cd "${HASHCYBERAXE_WORKSPACE}/research/fifties/perspectives/modular"
s=$(date +%s.%N)
./tower run "$1" "$2" "tower_$3.txt" 2> "tower_$3.log"
e=$(date +%s.%N)
echo "2^$1 samples in $(echo "$e - $s" | bc) s" | tee -a "tower_$3.log"
