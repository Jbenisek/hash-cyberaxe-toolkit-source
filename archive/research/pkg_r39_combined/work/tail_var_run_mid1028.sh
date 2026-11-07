#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# tail_var_run.sh : 14 public-seed tail runs per variant pair, 40 at a time, nice 10. Outputs tail_var/<sig>/out_NN.json (+ err, times).
P="${HASHCYBERAXE_WORKSPACE}"/research/pkg_r39_combined/work
cd $HOME/r39comb || exit 1
for sig in $(cat $P/tail_var/RUNS_mid1028.txt); do [ -f $P/tail_var/$sig/out_14.json ] && continue; cp $P/tail_var/$sig/r39tail_free.py ./r39tail_$sig.py; for i in $(seq -w 1 14); do echo "$sig $i"; done; done > $P/tail_var/JOBS_mid1028.txt
run1() { sig=$1; i=$2; s=$(date +%s.%N); nice -n 10 python3 -B r39tail_$sig.py < $P/req/r39-tail-$i.json > $P/tail_var/$sig/out_$i.json 2> $P/tail_var/$sig/err_$i.txt; echo "$i rc=$? $(echo "$(date +%s.%N) - $s" | bc) s" >> $P/tail_var/$sig/times.txt; }
export -f run1; export P
cat $P/tail_var/JOBS_mid1028.txt | xargs -P ${LANES:-4} -n 2 bash -c 'run1 "$@"' _
echo "variants done: $(ls $P/tail_var/*/out_14.json | wc -l)"
