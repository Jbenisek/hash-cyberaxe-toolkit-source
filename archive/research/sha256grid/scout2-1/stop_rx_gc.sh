#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/sha256grid/scout2-1" || exit 1
P=$(cat r3rx_s1.pid)
C=$(tr '\0' ' ' < /proc/$P/cmdline 2>/dev/null)
echo "pid $P cmdline: $C"
case "$C" in
  *"kissat --time=1700 --seed=1 step1_k2_relaxW.cnf"*) kill $P && echo "stopped own pid $P";;
  *) echo "not stopping: cmdline does not match";;
esac
sleep 1
for f in gc_fix32 gc_fix33; do
  s=$(date +%s.%N)
  kissat -q --time=300 $f.cnf > $f.out 2>&1
  rc=$?
  e=$(date +%s.%N)
  echo "$f rc=$rc $(grep '^s ' $f.out) wall=$(echo "$e - $s" | bc)"
done