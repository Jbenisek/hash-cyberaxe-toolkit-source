#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# exact model P(coll | member, E1.d1, w8) for the cells in p3_in.txt (one process, light)
set -e
H="${HASHCYBERAXE_WORKSPACE}/research/newpaths/collision_pattern"
T="${HASHCYBERAXE_WORKSPACE}/astra-jobs/server_tasks_2026-10-06/task5_small_h8"
C="${HASHCYBERAXE_WORKSPACE}/research/newpaths/counter/toy"
cd "$H"
bash build.sh > /dev/null
time ./feat8 "$T/sets_w8.txt" "$C" < p3_in.txt > p3_out.txt
wc -l p3_out.txt
