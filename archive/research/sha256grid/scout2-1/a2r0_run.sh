#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# usage: a2r0_run.sh TAG A0..A15
cd "${HASHCYBERAXE_WORKSPACE}/research/sha256grid/scout2-1" || exit 1
TAG=$1; shift
s=$(date +%s.%N); ./a2r0 "$@" 24 7 48 > a2r0_$TAG.txt 2>&1; e=$(date +%s.%N)
echo "wall $(echo "$e - $s" | bc)" >> a2r0_$TAG.txt
cat a2r0_$TAG.txt