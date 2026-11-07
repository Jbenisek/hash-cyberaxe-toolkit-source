#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# worker.sh W: takes jobs from jobs.txt (claim = mkdir claims/N, atomic), writes out/<tag>_set<i>_r<first>.txt
# research only; at most 4 workers are started (start_all.sh)
D="${HASHCYBERAXE_WORKSPACE}"/research/newpaths/counter/toy
BIN=$HOME/ctr_toy_bin/ctr_toy8
cd "$D" || exit 1
mkdir -p out claims
n=0
while read -r arr set beta first count nouter tag; do
  n=$((n+1))
  [ -z "$arr" ] && continue
  f="out/${tag}_set${set}_r${first}.txt"
  [ -f "$f" ] && continue
  mkdir "claims/$n" 2>/dev/null || continue
  [ -f STOP ] && { rmdir "claims/$n"; break; }
  "$BIN" run "$arr" sets_w8.txt "$set" "$beta" "$first" "$count" "$nouter" > "$f.part" 2> "$f.err"
  if grep -q '^END' "$f.part"; then mv "$f.part" "$f"; rm -f "$f.err"; echo "$(date +%H:%M:%S) worker $1 done $f" >> out/progress.txt
  else echo "$(date +%H:%M:%S) worker $1 FAILED $f" >> out/progress.txt; fi
done < jobs.txt
echo "$(date +%H:%M:%S) worker $1 finished" >> out/progress.txt
