#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/tools/traillab"
W="${HASHCYBERAXE_WORKSPACE}"/research/dig/incoming/sha256-38-U01/work
ONLY='droprow E22 ; droprow E23 ; droprow W23 ; droprow W25'
A=(--relax "ALL=$ONLY")
i=0
for r in "0 30 1" "1 31 1" "14 21 0" "16 25 0"; do
  set -- $r
  A+=(--relax "P_${1}_${2}=$ONLY ; lin W23[$1]^W23[$2]=$3")
  o=$((1-$3))
  A+=(--relax "O_${1}_${2}=$ONLY ; lin W23[$1]^W23[$2]=$o")
done
timeout 900 ./traillab window --chi chi/chi38.txt --rows 22 37 --event out --no-elist --autolist --np 4096 --mt 8192 --threads 3 --seeds 9301,9302 "${A[@]}" > $W/out/R23_relations.txt 2>&1
echo "exit $?" >> $W/out/R23_relations.txt
