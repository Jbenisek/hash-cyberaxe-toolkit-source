#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# build the feature program for W = 8 and W = 10 (task5 toy.h and tl_lines.inc, read-only)
set -e
H="${HASHCYBERAXE_WORKSPACE}/research/newpaths/collision_pattern"
T="${HASHCYBERAXE_WORKSPACE}/astra-jobs/server_tasks_2026-10-06/task5_small_h8"
cd "$H"
g++ -O2 -w -x c++ -DWBITS=8 -I"$T" -o feat8 feat.c
g++ -O2 -w -x c++ -DWBITS=10 -I"$T" -o feat10 feat.c
ls -la feat8 feat10
