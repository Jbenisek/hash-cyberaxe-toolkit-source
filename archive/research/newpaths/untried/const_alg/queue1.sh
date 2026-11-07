#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# queue1.sh: the three strongest pins without a per-beta file (by the screened counter objective: L4b, L8b, L8c),
# one after the other, each through run_pin.sh with k <= 18, 2 processes, a budget of 1140 s (under 20 min each).
# L4b was run first with k <= 15 (26 s); its filter files are removed so the filter can be extended
# (ATLAS section 8, caution 1: the filter splits its list by the number of processes). Only this folder is touched.
D="${HASHCYBERAXE_WORKSPACE}/research/newpaths/untried/const_alg"
rm -f "$D/scratch/L4b/filter_"*
for spec in "L4b 18" "L8b 18" "L8c 18"; do
  set -- $spec
  [ -f "$D/STOP" ] && break
  bash "$D/run_pin.sh" "$1" "$2" 1140 2
done
tail -12 "$D/status.txt" | cut -c1-300
