#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# derive-dense-held-j8-9 part 3: split the W8-cell extras; then 4 SMC bases (rows 4..21 conditioned prefix). --threads 2, timeout 1200.
cd "${HASHCYBERAXE_WORKSPACE}/research/tools/traillab"
O=atlas_runs/derive-dense-held-j8-9
T="timeout 1200 /usr/bin/time -f %es"
RL=(--relax 'xorW8=dropx W8 e0000000' --relax 'x2W8=dropx2 W8' --relax 'xorx2W8=dropx W8 e0000000 ; dropx2 W8' --relax 'noW8=droprow W8')
$T ./traillab exact --chi $O/chi37_W8fset.txt --rows 4 9 --enum W8:set --base pub --event out "${RL[@]}" --threads 2 > $O/exact_r4_9_W8fset_pub_split.txt 2>&1
$T ./traillab exact --chi $O/chi37_W8fset.txt --rows 22 36 --enum W8:set --base smc --np 64 --pick 4 --seed 1 --event out "${RL[@]}" --threads 2 > $O/exact_r22_36_W8fset_smc4.txt 2>&1
echo DONE3
