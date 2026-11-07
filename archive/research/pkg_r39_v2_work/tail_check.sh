#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# tail_check.sh TAG : the 14 tail experiments of the staged r39tail.py on the public seeds (requests of the 2b4af365 build), 14 at once
W="${HASHCYBERAXE_WORKSPACE}"/research; P=$W/pkg_r39_$1; O=$W/pkg_r39_v2_work/tail_$1; mkdir -p $O; cd $O; rm -f times.txt
for i in $(seq -w 1 14); do ( s=$(date +%s%N); python3 -B $P/sha256/experiments/r39tail.py < $W/pkg_r39_best_work/tail/r39-tail-$i.json > out_$i.json 2> err_$i.txt; echo "$i rc=$? ms=$(( ($(date +%s%N)-s)/1000000 ))" >> times.txt ) & done; wait
echo "$1 tail: $(grep -c 'rc=0' times.txt)/14 rc=0; ms $(sed 's/.*ms=//' times.txt | sort -n | head -1)..$(sed 's/.*ms=//' times.txt | sort -n | tail -1)"
