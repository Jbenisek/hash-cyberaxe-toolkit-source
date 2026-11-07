#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/dig/incoming2/sha256-37-G07-U03/work" || exit 1
gcc -O3 -march=native -o smc smc.c -lm 2>&1 | grep -E "error" 
date
# RULE (written before run): sd(log2 q3) must scale as NP^-1/2 (ratio NP512/NP8192 = 4 within [2.5,6.4] using 95% chi2 intervals); means of log2 q3 across NP equal within 2 se; control arm NP=16 must show larger sd/bias
./smc 9101 8192 512 4096 1024 12 0 > out_np8192.txt
./smc 9102 2048 512 4096 1024 24 0 > out_np2048.txt
./smc 9103 512 512 4096 1024 48 0 > out_np512.txt
./smc 9104 64 512 4096 1024 96 0 > out_np64.txt
./smc 9105 8 512 4096 1024 150 0 > out_np8.txt
date
