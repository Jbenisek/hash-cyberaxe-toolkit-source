#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/fifties/perframe"
rm -rf dry
python3 -B run_main.py dry 512 256 2 > dry_run.log 2>&1
python3 -B analyse_pf.py dry dry_out.json > dry_analyse.log 2>&1
tail -2 dry_run.log; cat dry_analyse.log | head -c 2500
