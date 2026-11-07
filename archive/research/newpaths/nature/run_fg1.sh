#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# functional-graph runs, part 1 (one process at a time, each 2^32 evaluations, 4 GB counter array)
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/nature || exit 1
echo "fg1 pid $$ start $(date)" >> pids.txt
{
timeout 900 ./nature funcgraph ctrl 0 1 1 300 2
timeout 1800 ./nature funcgraph 0,1,2,3 0 1 2 300 2
timeout 1800 ./nature funcgraph 0,1,2,3 1 1 3 300 2
timeout 1800 ./nature funcgraph 1,9,11,14 0 1 4 300 2
timeout 1800 ./nature funcgraph 0,1,2,3 0 1 9 300 1
} > fg1.out 2>&1
echo "fg1 done $(date)" >> pids.txt
