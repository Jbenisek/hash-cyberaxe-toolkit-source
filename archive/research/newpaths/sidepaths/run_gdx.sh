#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# usage: run_gdx.sh model K timeout_seconds   -> writes res_<model>_k<K>.txt
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/sidepaths
m=$1; k=$2; t=$3
start=$(date +%s)
timeout $t ./gdx m_$m.model $k 0 1 5 > res_${m}_k${k}.txt 2>&1
echo "exit=$? secs=$(( $(date +%s) - start ))" >> res_${m}_k${k}.txt
