#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/dig/incoming2/sha256-38-G04-U03/work" || exit 1
bash build.sh >/dev/null
chmod +x scan38b
TL=400 ./runb.sh real_base real 22 7301
TL=600 ./runb.sh steer_big steer 33 7102
TL=300 ./runb.sh exact2_more exact 2 12 9902
for spec in "1 315a2db3" "1 00000000" "2 5ed877a8" "2 ffffffff" "3 78a7f752" "3 00000000"; do
  set -- $spec; TL=200 ./runb.sh steer_fixbig_$1_$2 steer 30 7600 --fix $1 $2
done
TL=400 ./runb.sh exact1_more exact 1 8 9901
TL=400 ./runb.sh exact3_more exact 3 8 9903
echo ALLDONE > batch2.done
