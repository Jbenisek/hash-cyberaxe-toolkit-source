#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# stageB_pf013.sh : fresh-seed re-measure of pf_013's r39 tail (14 new request files, seeds never used before), 4 lanes, nice 10
P="${HASHCYBERAXE_WORKSPACE}"/research/pkg_r39_combined/work; cd $HOME/r39comb || exit 1
cp $P/tail_var/pf_013/r39tail_free.py ./r39tail_pf013B.py
run1() { i=$1; nice -n 10 python3 -B r39tail_pf013B.py < $P/req/r39-tail-fresh-$i.json > $P/tail_var/pf_013_B/out_$i.json 2> $P/tail_var/pf_013_B/err_$i.txt; echo "$i rc=$?"; }
export -f run1; export P
seq -w 1 14 | xargs -P 4 -n 1 bash -c 'run1 "$@"' _
