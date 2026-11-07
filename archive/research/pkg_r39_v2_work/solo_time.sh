#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# solo_time.sh : sequential wall times (one process at a time) of the staged programs on public-seed requests
W="${HASHCYBERAXE_WORKSPACE}"/research
for T in s108 7111; do P=$W/pkg_r39_$T/sha256/experiments; O=$W/pkg_r39_v2_work/solo_$T.txt; rm -f $O
  for x in r39-transplant-claw r39-window-small; do s=$(date +%s%N); python3 -B $P/r39joint.py < $W/pkg_r39_best_work/exp/$x.json > /dev/null 2>&1; echo "$x rc=$? ms=$(( ($(date +%s%N)-s)/1000000 ))" >> $O; done
  for i in 02 09; do s=$(date +%s%N); python3 -B $P/r39tail.py < $W/pkg_r39_best_work/tail/r39-tail-$i.json > /dev/null 2>&1; echo "tail-$i rc=$? ms=$(( ($(date +%s%N)-s)/1000000 ))" >> $O; done
done; cat $W/pkg_r39_v2_work/solo_*.txt; uptime
