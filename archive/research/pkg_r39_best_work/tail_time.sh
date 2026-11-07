#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# sequential wall time: dk's accepted r39tail.py vs ours, same request, same machine state (3 alternations)
P="${HASHCYBERAXE_WORKSPACE}"/research
cd $P/pkg_r39_best/work/tail
for k in 1 2 3; do
 for f in $P/pkg_r39_combined/work/dk/experiments/r39tail.py $P/pkg_r39_best/sha256/experiments/r39tail.py; do
  s=$(date +%s%N); python3 -B $f < r39-tail-02.json > /dev/null; echo "$(basename $(dirname $(dirname $f))) rc=$? ms=$(( ($(date +%s%N)-s)/1000000 ))"
 done
done; uptime
