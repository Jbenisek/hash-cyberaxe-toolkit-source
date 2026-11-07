#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# GPU joint K3 x K2 test at the root instance (h = IV, t = 0, b = 64, flags 11), then K1 problems and scans.
# One GPU job at a time; each step well under 20 minutes.  Own processes only.
cd "${HASHCYBERAXE_WORKSPACE}/research/newpaths/untried/combo-finder" || exit 1
date
echo "== step A: full A-scan of the 22 good deltas against the K2-solvable bitmap"
./k3gpu scan 0x5BE0CD19 11 deltas_root22.txt k3scan_root22.txt d2_root.bin.bm
date
echo "== step B: random (A,delta) sampling with bitmap, v2(delta) in {1,2}, 240 s"
./k3gpu 0x5BE0CD19 11 240 21 2 k3gpu_root_joint.txt d2_root.bin.bm
date
