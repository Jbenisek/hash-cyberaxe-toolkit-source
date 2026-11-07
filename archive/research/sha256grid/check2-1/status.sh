#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/sha256grid/check2-1" || exit 1
date
for f in g8_s1 k2_s1 sbase_s2 cbase_s1 cbase_s2 cbase_s3 g32_s2 cbase_s4 cbase_s5; do
  [ -f $f.out ] || continue
  st=$(grep -m1 '^s ' $f.out); pt=$(grep 'process-time' $f.out | tail -1 | awk '{print $(NF-1)}')
  echo "$f: ${st:-running} ${pt:+process-time $pt s} $( [ -f $f.done ] && cat $f.done )"
  [ -f $f.decode.txt ] && grep -E 'valid|failures|A3..A13|^Ax' $f.decode.txt | sed 's/^/    /'
done
for c in A B C; do [ -f $c.chaindone ] && echo "chain $c done: $(cat $c.chaindone)"; done
echo "my kissat PIDs:"; for p in *.pid; do P=$(cat $p); [ -e /proc/$P ] && echo "  $p $P $(tr '\0' ' ' < /proc/$P/cmdline)"; done
