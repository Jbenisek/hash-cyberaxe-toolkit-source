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
timeout 300 ./traillab window --chi chi/chi38.txt --rows 22 37 --event out --no-elist --autolist --np 4096 --mt 8192 --threads 3 --seeds 9301 --relax 'W23x2=dropx2 W23' --relax 'W23all=dropx W23 ffffffff' --relax 'W23optest=dropx W23 ffffffff ; lin W23[0]^W23[30]=1' --relax 'W23opp=dropx W23 ffffffff ; lin W23[0]^W23[30]=0' > $W/out/_t1.txt 2>&1
