#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# peek.sh NAME : read-only progress of one pin's run in this folder (clock, load, step outputs so far).
D="${HASHCYBERAXE_WORKSPACE}/research/newpaths/untried/const_alg"; s="$D/scratch/$1"
date +%H:%M:%S; echo "load $(cut -d' ' -f1-3 /proc/loadavg)"
[ -f "$s/betas_all.txt" ] && echo "betas listed $(wc -l < "$s/betas_all.txt"); filtered $(cat "$s"/filter_out_*.txt 2>/dev/null | wc -l)"
[ -f "$s/sys_list.txt" ] && echo "sys asked $(wc -l < "$s/sys_list.txt"); answered $(grep -c '^SYS' "$s/sys_result.txt" 2>/dev/null); SAT $(grep -c ' SAT ' "$s/sys_result.txt" 2>/dev/null); sample answered $(grep -c '^SYS' "$s/sys_sample_result.txt" 2>/dev/null)"
ls "$s"/sat_raw_*.txt >/dev/null 2>&1 && echo "calculator DONE lines $(cat "$s"/sat_raw_*.txt | grep -c '^DONE'); raw bytes $(cat "$s"/sat_raw_*.txt | wc -c)"
tail -4 "$D/status.txt" 2>/dev/null | cut -c1-400
echo "own processes (pgid of the last run_pin):"
g=$(tail -1 "$D/pids.txt" 2>/dev/null | grep -oE 'pgid [0-9]+' | cut -d' ' -f2)
[ -n "$g" ] && ps -o pid=,pgid=,etimes=,pcpu=,comm= -g "$g" 2>/dev/null | head -12
