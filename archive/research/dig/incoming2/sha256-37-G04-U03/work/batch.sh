#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/dig/incoming2/sha256-37-G04-U03/work" || exit 1
export TL=600
./run.sh w17_base w17 29 7101
./run.sh bucket_base bucket 30 7201
./run.sh real_base real 29 7301
for spec in "1 315a2db3" "1 00000000" "2 5ed877a8" "2 ffffffff" "3 78a7f752" "3 00000000"; do
  set -- $spec; tag="k$1_$2"
  ./run.sh w17_fix_$tag w17 27 7400 --fix $1 $2
  ./run.sh bucket_fix_$tag bucket 28 7500 --fix $1 $2
done
echo ALLDONE > batch.done
