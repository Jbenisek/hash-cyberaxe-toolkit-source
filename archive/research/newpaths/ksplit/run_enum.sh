#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# usage: run_enum.sh <sysfile> <g> <nprocs> <maxB> <tag> <timeout> [LIN] [EXTRA] [GATE]
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/ksplit
sys=$1; g=$2; np=$3; mb=$4; tag=$5; to=$6; lin=${7:-0}; ex=${8:-0}; gate=${9:-0}
for ((p=0; p<np; p++)); do
  ( KS_GATE=$gate KS_LIN=$lin KS_EXTRA=$ex timeout $to ./ks $sys enum $g $p $np $mb > res_${tag}.p$p 2>&1; echo "exit=$?" >> res_${tag}.p$p ) &
done
wait
echo "done $tag" >> res_${tag}.done
