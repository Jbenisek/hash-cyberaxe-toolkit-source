#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# 12 ledger windows on the PC (seeds 1..12), one process per window, nice 0, check mode; per-window stdout + json streamed to led/
P="${HASHCYBERAXE_WORKSPACE}"/research/pkg_r39_best
D=$HOME/r39best; mkdir -p $D; cp $P/sha256/experiments/r39joint.py $D/
cd $D; sha256sum r39joint.py > $P/work/led/prog_pc.sha
for S in $(seq 1 12); do
  python3 -B r39joint.py --windows 1 --seed $S --check --out $P/work/led/win_$S.json > $P/work/led/win_$S.txt 2>&1 &
  echo "launched S=$S pid $!" >> $P/work/led/launch_pc.txt
done
wait
echo "ALL DONE $(date)" >> $P/work/led/launch_pc.txt
