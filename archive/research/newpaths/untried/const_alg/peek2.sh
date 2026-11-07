#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# peek2.sh: read-only look at this folder's last process group (from pids.txt) and at the pin-solver log.
D="${HASHCYBERAXE_WORKSPACE}/research/newpaths/untried/const_alg"
date +%H:%M:%S; echo "load $(cut -d' ' -f1-3 /proc/loadavg)"
g=$(tail -1 "$D/pids.txt" | grep -oE 'pgid [0-9]+' | cut -d' ' -f2)
echo "own group pgid=$g:"
ps -eo pid=,pgid=,etimes=,pcpu=,args= | awk -v g="$g" '$2 == g' | cut -c1-220
echo "pinctr.log:"; cut -c1-400 "$D/pinctr.log"
