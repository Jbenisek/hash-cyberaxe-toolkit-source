#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# Read-only look at the WSL side before any run: clock, load, the binaries the count pipeline executes, kissat.
date
echo "nproc $(nproc); load $(cut -d' ' -f1-3 /proc/loadavg)"
for b in "$HOME/hashsmash/h8/bin/h8_pair_list" "$HOME/hashsmash/h8/bin/h8_pair_calc_batch"; do
  if [ -x "$b" ]; then echo "$b $(sha256sum "$b" | cut -c1-16)"; else echo "$b MISSING"; fi
done
echo "calculator.sha (research/paths/counts): $(cat ""${HASHCYBERAXE_WORKSPACE}"/research/paths/counts/calculator.sha")"
command -v kissat && kissat --version
command -v python3 && python3 --version
echo "running processes by command name (count):"
ps -eo comm= | sort | uniq -c | sort -rn | head -12
