#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# rebuild, then start 4 workers in the background with a 90-minute limit each; PIDs in my_pids.txt
D="${HASHCYBERAXE_WORKSPACE}"/research/newpaths/counter/toy
B=$HOME/ctr_toy_bin
cd "$D" || exit 1
g++ -O3 -march=native -x c++ -DWBITS=8 -w -o "$B/ctr_toy8" ctr_toy.c -lm || { echo BUILD FAILED; exit 1; }
mkdir -p out
rm -f STOP
for w in 0 1 2 3; do
  nohup timeout 5400 bash "$D/worker.sh" $w > /dev/null 2>&1 &
  echo "worker $w pid $! started $(date +%H:%M:%S)" >> my_pids.txt
done
tail -4 my_pids.txt
