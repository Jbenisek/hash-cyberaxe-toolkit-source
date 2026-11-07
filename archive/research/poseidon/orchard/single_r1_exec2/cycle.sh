#!/bin/bash
# cycle.sh: build the program, run it once (the counted run), verify the collision, assemble the package and run prefile_check.
#   usage: bash cycle.sh [--fresh]        env: NICE=10
# The program is deterministic (fixed constant start), so there is exactly one counted run; it is cached by the hash of the sources.
set -u
cd "$(dirname "$0")"
HERE=$PWD; NICE=${NICE:-19}
FRESH=0; for a_ in "$@"; do case $a_ in --fresh) FRESH=1;; *) echo "unknown option $a_"; exit 2;; esac; done
CACHE=$HERE/data/cache; mkdir -p "$CACHE" logs data
LIBS="common.c ntt.c poly.c lean.c line.c split.c hgcd.c pallas.c"
CF="-O3 -march=native -Wall -Wextra -Wno-unused-function -Wno-unused-variable -Wno-unused-parameter"
GCCV=$(gcc --version | head -1)
SRCS="single.c $LIBS"
KEY=$({ echo "$GCCV $CF"; gcc -MM $SRCS 2>/dev/null | tr -d '\\' | tr -s ' \n' '\n\n' | grep -v ':$' | grep -v '^$' | sort -u | while read -r f; do sha256sum "$f"; done; } | sha256sum | cut -c1-16)
echo "cycle: source-hash=$KEY"
BD=$CACHE/$KEY; mkdir -p "$BD"
if [ $FRESH = 1 ] || [ ! -x "$BD/single" ]; then
  gcc $CF -o "$BD/single.tmp" $SRCS -lm 2>"$BD/gcc.err" && mv "$BD/single.tmp" "$BD/single" || { echo "BUILD FAILED"; tail "$BD/gcc.err"; exit 2; }
fi
cp "$BD/single" single; size single > logs/size_exec.txt
if [ $FRESH = 1 ] || [ ! -s "$BD/run.txt" ]; then
  ( ulimit -s 64; nice -n $NICE ./single 1 > "$BD/run.tmp" 2>&1; echo "EXIT $?" >> "$BD/run.tmp" ); mv "$BD/run.tmp" "$BD/run.txt"
fi
cp "$BD/run.txt" logs/exec_run.txt
tail -3 logs/exec_run.txt | head -2 | cut -c1-120
grep -q '^EXIT 0' logs/exec_run.txt || { echo "RUN DID NOT STOP WITH THE COLLISION"; exit 3; }
PY=python3
export PKG_OUT=pkg_stage_exec LEDGER=exec_run.txt SIZE_FILE=logs/size_exec.txt NOTE_OUT=submission-note_exec.md NUMBERS=numbers_exec.json COLLS=collisions_exec.json
$PY collect.py exec_run $COLLS > logs/collect_exec.txt 2>&1; $PY verify_collision.py logs/exec_run.txt > logs/verify_exec.txt 2>&1 || { echo "VERIFY FAILED"; cat logs/verify_exec.txt; exit 4; }
$PY build_package.py > logs/build_package_exec.txt 2>&1 || { echo "PACKAGE FAILED"; tail -8 logs/build_package_exec.txt; exit 5; }
CHK=$HERE/pkg_check_exec; rm -rf "$CHK"; mkdir -p "$CHK/poseidon-orchard-r1"; cp -r "$HERE/pkg_stage_exec/." "$CHK/poseidon-orchard-r1/"; cp "$HERE/submission-note_exec.md" "$CHK/submission-note.md"
$PY ../../../launch/prefile_check.py "$CHK" > logs/prefile_exec.txt 2>&1
cat data/numbers_exec.json; echo
echo "prefile: $(tail -1 logs/prefile_exec.txt)"; grep '^FAIL' logs/prefile_exec.txt | cut -c1-200
