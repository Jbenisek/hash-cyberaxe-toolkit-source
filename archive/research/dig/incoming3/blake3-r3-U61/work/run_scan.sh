#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# usage: run_scan.sh "0 1 2 3" outfile
cd "${HASHCYBERAXE_WORKSPACE}/research/dig/incoming3/blake3-r3-U61/work"
for i in $1; do nice -n 10 ./site_scan $i 11 >> $2; done
echo finished >> $2
