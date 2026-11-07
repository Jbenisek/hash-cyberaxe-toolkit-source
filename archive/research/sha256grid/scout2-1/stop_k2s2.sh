#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/sha256grid/scout2-1" || exit 1
P=$(cat r2k2_s2.pid)
C=$(tr '\0' ' ' < /proc/$P/cmdline 2>/dev/null)
echo "pid $P cmdline: $C"
case "$C" in
  *"kissat --time=1700 --seed=2 step1_k2.cnf"*) kill $P && echo "stopped own pid $P";;
  *) echo "not stopping: cmdline does not match";;
esac