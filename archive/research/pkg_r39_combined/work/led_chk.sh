#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
P="${HASHCYBERAXE_WORKSPACE}"/research/pkg_r39_combined/work/led
cat $P/launch_pc.txt; ps -eo pid,ni,pcpu,etime,args | grep "r39joint" | grep -v grep; head -c 300 $P/win_1.txt
