#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
P="${HASHCYBERAXE_WORKSPACE}"/research/pkg_r39_combined/work
python3 -B $P/gen_req.py $P/req || exit 1
cp $P/tail/r39tail_free.py $HOME/r39comb/ ; cd $HOME/r39comb
for i in $(seq -w 1 14); do
  ( s=$(date +%s.%N); python3 -B r39tail_free.py < $P/req/r39-tail-$i.json > $P/tail/out_$i.json 2> $P/tail/err_$i.txt; echo "$i rc=$? $(echo "$(date +%s.%N) - $s" | bc) s" >> $P/tail/times.txt ) &
done
wait; echo done
