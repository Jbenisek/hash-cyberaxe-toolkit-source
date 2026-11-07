#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# functional-graph runs, part 2
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/nature || exit 1
echo "fg2 pid $$ start $(date)" >> pids.txt
{
timeout 1800 ./nature funcgraph 5,8,12,15 0 0 5 300 2
timeout 1800 ./nature funcgraph 12,13,14,15 1 0 6 300 2
timeout 1800 ./nature funcgraph msb2 0 0 7 300 2
timeout 1800 ./nature funcgraph 0,1,2,3 0 1 8 300 3
} > fg2.out 2>&1
echo "fg2 done $(date)" >> pids.txt
