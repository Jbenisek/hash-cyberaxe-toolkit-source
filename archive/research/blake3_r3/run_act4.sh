#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/blake3_r3
g++ -O2 -DBUD=2 -o act4_b2 act4.cpp && g++ -O2 -DBUD=1 -o act4_b1 act4.cpp || exit 1
echo "D={4,5} (the 2-round line's message difference), init diff allowed in v12..v15"
for b in 1 2; do for r in 1 2 3; do echo -n "budget=${b}k rounds=$r : "; ./act4_b$b $r 16 0x30 | head -1; done; done
echo "D={0,1}"; for r in 2 3; do ./act4_b2 $r 16 0x3 | head -1; done
echo "D={2,3}"; for r in 2 3; do ./act4_b2 $r 16 0xc | head -1; done
echo "D={6,7}"; for r in 2 3; do ./act4_b2 $r 16 0xc0 | head -1; done
