#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# tail_li39_pc.sh : 14 public-seed tail runs for one variant on the PC (WSL), 4 at a time, nice 10; then the stats line.
P="${HASHCYBERAXE_WORKSPACE}"/research/pkg_r39_combined/work
sig=${1:-p_li39tab23s1_luna}
cd $HOME/r39comb || { echo "no ~/r39comb on this machine"; exit 1; }
cp $P/tail_var/$sig/r39tail_free.py ./r39tail_$sig.py
run1() { sig=$1; i=$2; s=$(date +%s.%N); nice -n 10 python3 -B r39tail_$sig.py < $P/req/r39-tail-$i.json > $P/tail_var/$sig/out_$i.json 2> $P/tail_var/$sig/err_$i.txt; echo "$i rc=$? $(echo "$(date +%s.%N) - $s" | bc) s" >> $P/tail_var/$sig/times.txt; }
export -f run1; export P
for i in $(seq -w 1 14); do echo "$sig $i"; done | xargs -P 4 -n 2 bash -c 'run1 "$@"' _
cd $P && python3 tail_stats_dir.py tail_var/$sig 2>&1 | grep -E "mean_lin" | sed "s/^/$sig /" | tee -a tail_var/SUMMARY3.txt
