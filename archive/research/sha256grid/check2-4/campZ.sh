#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# check2-4 campaign Z: heavy-tail check of the M event (filed first test kept + collision): 2x particles, 2-4x streams
# usage: campZ.sh first_seed count logfile
cd "${HASHCYBERAXE_WORKSPACE}/research/sha256grid/check2-4" || exit 1
s0=$1; n=$2; log=$3
date > "$log"
for ((s = s0; s < s0 + n; s++)); do ./chk38 M $s 8000 4096 131072 262144 512 2048 32 524288 >> "$log"; done
date >> "$log"
