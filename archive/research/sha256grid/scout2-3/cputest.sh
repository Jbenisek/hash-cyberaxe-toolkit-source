#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# CPU-only checks (no GPU): selftest with |F7| count, validity dump for vt38 comparison, one small CPU SMC run with dumps
cd "${HASHCYBERAXE_WORKSPACE}/research/sha256grid/scout2-3" || exit 1
grep -A3 "k_tail" build.log | grep -E "registers|spill|stack" | head -4
./q3gpu selftest f7 > selftest.txt 2>&1; cat selftest.txt
./q3gpu dumpvalid 200000 7 valid_dump.bin
# master 777 run 0: NP 200, children 2048 64 64 8 8 4, MT 8192, V 4096; dump first 3000 proposals per stage + all survivors/hits
./q3gpu cpusmc 777 0 200 2048 64 64 8 8 4 8192 4096 smc_dump.bin 3000 smc_hits.bin > cpusmc.txt 2>&1; cat cpusmc.txt
ls -la valid_dump.bin smc_dump.bin smc_hits.bin
