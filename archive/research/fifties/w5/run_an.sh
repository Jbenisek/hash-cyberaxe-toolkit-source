#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# usage: bash run_an.sh <main|fresh|x9>
cd "${HASHCYBERAXE_WORKSPACE}"/research/fifties/w5 || exit 1
python3 -B w5_analyse.py "$1" > an_$1.log 2>&1
echo "exit $?" >> an_$1.log
