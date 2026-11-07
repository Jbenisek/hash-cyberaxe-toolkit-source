#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# tail_pool.sh : 56 more tail replica runs (ids r39-tail-15..70, seeds by the organizer's public derivation rule) on our advice, all at once, nice 0.
P="${HASHCYBERAXE_WORKSPACE}"/research/pkg_r39_combined/work
python3 -B $P/gen_req_pool.py $P/req_pool || exit 1
cd $HOME/r39comb || exit 1
for i in $(seq -w 15 70); do
  ( s=$(date +%s.%N); python3 -B r39tail_free.py < $P/req_pool/r39-tail-$i.json > $P/tail_pool/out_$i.json 2> $P/tail_pool/err_$i.txt; echo "$i rc=$? $(echo "$(date +%s.%N) - $s" | bc) s" >> $P/tail_pool/times.txt ) &
done
wait; echo "pool done: $(ls $P/tail_pool/out_*.json | wc -l) outputs"
