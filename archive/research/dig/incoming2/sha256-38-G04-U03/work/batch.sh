#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/dig/incoming2/sha256-38-G04-U03/work" || exit 1
export TL=900
TL=120 ./run.sh steer_test steer 22 7000
./run.sh steer_base steer 28 7101
TL=300 ./run.sh real_base real 22 7301
for k in 1 2 3; do TL=400 ./run.sh exact_k$k exact $k 4 77$k; done
for spec in "1 315a2db3" "1 00000000" "2 5ed877a8" "2 ffffffff" "3 78a7f752" "3 00000000"; do
  set -- $spec; ./run.sh steer_fix_$1_$2 steer 26 7500 --fix $1 $2
done
echo ALLDONE > batch.done
