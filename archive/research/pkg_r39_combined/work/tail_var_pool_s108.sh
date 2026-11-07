#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# tail_var_pool.sh : 56 more runs (ids 15..70, public seed rule) for the two best-tailed variants, 40 at a time, nice 0.
P="${HASHCYBERAXE_WORKSPACE}"/research/pkg_r39_combined/work
cd $HOME/r39comb || exit 1
for sig in p_p39chars108_p39s; do for i in $(seq -w 15 70); do echo "$sig $i"; done; done > $P/tail_var/JOBS_pool_s108.txt
run1() { sig=$1; i=$2; python3 -B r39tail_$sig.py < $P/req_pool/r39-tail-$i.json > $P/tail_var/$sig/out_$i.json 2> $P/tail_var/$sig/err_$i.txt; echo "$i rc=$?" >> $P/tail_var/$sig/times_pool.txt; }
export -f run1; export P
cat $P/tail_var/JOBS_pool_s108.txt | xargs -P 40 -n 2 bash -c 'run1 "$@"' _
echo "pool done: $(ls $P/tail_var/p_p39chars108_p39s/out_*.json | wc -l) outputs"
