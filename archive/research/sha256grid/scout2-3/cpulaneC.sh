#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# CPU lane C (no GPU): variant-dispersion study, ONE fresh uniform variant per run (R2 design), master 4444
cd "${HASHCYBERAXE_WORKSPACE}/research/sha256grid/scout2-3" || exit 1
echo $$ > cpulaneC.pid
exec ./q3gpu2 cpubatch 4444 0 1 "$1" 4000 2048 64 64 8 8 4 8192 1 cpuC_m4444_v1
