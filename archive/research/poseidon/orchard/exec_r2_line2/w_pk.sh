#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/poseidon/orchard/${1:-exec_r2_line2_synth}" || exit 1
PY=python3; export R=2
export PKG_OUT=pkg_stage_exec LEDGER=exec_run.txt SIZE_FILE=logs/size_exec.txt NOTE_OUT=submission-note_exec.md NUMBERS=numbers_exec.json COLLS=collisions_exec.json
$PY collect.py exec_run $COLLS > logs/collect_exec.txt 2>&1; $PY verify_collision.py logs/exec_run.txt > logs/verify_exec.txt 2>&1 || { echo "VERIFY FAILED"; cat logs/verify_exec.txt; exit 4; }
cat logs/verify_exec.txt
$PY build_package.py > logs/build_package_exec.txt 2>&1 || { echo "PACKAGE FAILED"; tail -12 logs/build_package_exec.txt; exit 5; }
tail -5 logs/build_package_exec.txt
CHK=$PWD/pkg_check_exec; rm -rf "$CHK"; mkdir -p "$CHK/poseidon-orchard-r2"; cp -r "$PWD/pkg_stage_exec/." "$CHK/poseidon-orchard-r2/"; cp "$PWD/submission-note_exec.md" "$CHK/submission-note.md"
$PY ../../../launch/prefile_check.py "$CHK" > logs/prefile_exec.txt 2>&1
tail -15 logs/prefile_exec.txt | cut -c1-200
