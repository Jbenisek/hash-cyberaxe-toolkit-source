#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# features of the found collisions and of the null trials (W = 8 and 10); single process each, light
set -e
H="${HASHCYBERAXE_WORKSPACE}/research/newpaths/collision_pattern"
T="${HASHCYBERAXE_WORKSPACE}/astra-jobs/server_tasks_2026-10-06/task5_small_h8"
C="${HASHCYBERAXE_WORKSPACE}/research/newpaths/counter/toy"
cd "$H"
time ./feat8 "$T/sets_w8.txt" "$C" < feat_in8.txt > feat_out8.txt
time ./feat10 "$T/sets_w10.txt" - < feat_in10.txt > feat_out10.txt
wc -l feat_out8.txt feat_out10.txt
