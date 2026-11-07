#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# two independent 2^39 runs (train seed / test seed), about 7 minutes each on the RTX 3090
D="${HASHCYBERAXE_WORKSPACE}/research/fifties/perspectives/modular"
bash "$D/run_tower.sh" 39 0x544F574552410001 trainA
bash "$D/run_tower.sh" 39 0x544F574552420002 testB
