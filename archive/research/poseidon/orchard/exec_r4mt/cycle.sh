#!/bin/bash
# cycle.sh: build the program, run it once (the counted run, under memmeter), verify the collision, assemble the package and run prefile_check.
#   usage: bash cycle.sh [--fresh] [--import DIR]      env: NICE=10, PROBES (e.g. 2-11, for the note)
#   --import DIR: take the counted run made in DIR (DIR/single, DIR/run.txt, DIR/mem.json) instead of running here; refused unless DIR/single is
#                 byte-identical to the binary built here from the current sources.
# The program is deterministic (fixed constant start), so there is exactly one counted run; it is cached by the hash of the sources.
set -u
cd "$(dirname "$0")"
HERE=$PWD; NICE=${NICE:-10}; NTHREADS=${NTHREADS:-24}   # threads of the counted run, main included (the second argument of the program; the thread-control charge depends on it)
FRESH=0; IMPORT=""; while [ $# -gt 0 ]; do case $1 in --fresh) FRESH=1;; --import) IMPORT=$2; shift;; *) echo "unknown option $1"; exit 2;; esac; shift; done
CACHE=$HERE/data/cache; mkdir -p "$CACHE" logs data
MM="$HERE/../../../tools/memmeter/memmeter.py"
LIBS="common.c ntt.c poly.c lean.c line.c split.c hgcd.c pallas.c par.c nolibc.c"
CF="-O3 -march=native -static -nostdlib -fno-stack-protector -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=0 -fno-pie -no-pie -ffunction-sections -fdata-sections -Wl,--gc-sections -Wall -Wextra -Wno-unused-function -Wno-unused-variable -Wno-unused-parameter"
GCCV=$(gcc --version | head -1)
SRCS="single.c $LIBS"
KEY=$({ echo "$GCCV $CF threads=$NTHREADS"; gcc -MM $SRCS 2>/dev/null | tr -d '\' | tr -s ' \n' '\n\n' | grep -v ':$' | grep -v '^$' | sort -u | while read -r f; do sha256sum "$f"; done; } | sha256sum | cut -c1-16)
echo "cycle: source-hash=$KEY"
BD=$CACHE/$KEY; mkdir -p "$BD"
if [ $FRESH = 1 ] || [ ! -x "$BD/single" ]; then
  gcc $CF -o "$BD/single.tmp" $SRCS 2>"$BD/gcc.err" && mv "$BD/single.tmp" "$BD/single" || { echo "BUILD FAILED"; tail "$BD/gcc.err"; exit 2; }
fi
cp "$BD/single" single; size single > logs/size_exec.txt
if [ -n "$IMPORT" ]; then
  cmp -s "$IMPORT/single" "$BD/single" || { echo "IMPORT REFUSED: $IMPORT/single differs from the binary built from the current sources"; exit 6; }
  head -1 "$IMPORT/mem.json" > "$BD/mem.json"
  { cat "$IMPORT/run.txt"; echo "EXIT $(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["exit"])' "$BD/mem.json")"; } > "$BD/run.txt"
  echo "imported the counted run from $IMPORT (binary identical: $(sha256sum "$BD/single" | cut -c1-16))"
elif [ $FRESH = 1 ] || [ ! -s "$BD/run.txt" ]; then
  ( cd "$BD" && nice -n $NICE python3 "$MM" --label counted -- bash -c 'ulimit -s 64; exec ./single 1 '$NTHREADS' > run.tmp 2>&1' > mem.tmp 2> mem.err; head -1 mem.tmp > mem.json
    echo "EXIT $(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["exit"])' mem.json)" >> run.tmp; mv run.tmp run.txt )
fi
cp "$BD/run.txt" logs/exec_run.txt; cp "$BD/mem.json" logs/mem_exec.json
python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); print("memmeter peak", d["peak_bytes"], "bytes, wall", d["wall_s"], "s, exit", d["exit"])' logs/mem_exec.json
tail -3 logs/exec_run.txt | head -2 | cut -c1-120
grep -q '^EXIT 0' logs/exec_run.txt || { echo "RUN DID NOT STOP WITH THE COLLISION"; exit 3; }
PY=python3; export R=4
export PKG_OUT=pkg_stage_exec LEDGER=exec_run.txt SIZE_FILE=logs/size_exec.txt MEM_FILE=logs/mem_exec.json NOTE_OUT=submission-note_exec.md NUMBERS=numbers_exec.json COLLS=collisions_exec.json PROBES=${PROBES:-} SIM_EXTENT=${SIM_EXTENT:?set SIM_EXTENT from the arena replay}
$PY collect.py exec_run $COLLS > logs/collect_exec.txt 2>&1; $PY verify_collision.py logs/exec_run.txt > logs/verify_exec.txt 2>&1 || { echo "VERIFY FAILED"; cat logs/verify_exec.txt; exit 4; }
cat logs/verify_exec.txt
$PY build_package.py > logs/build_package_exec.txt 2>&1 || { echo "PACKAGE FAILED"; tail -8 logs/build_package_exec.txt; exit 5; }
CHK=$HERE/pkg_check_exec; rm -rf "$CHK"; mkdir -p "$CHK/poseidon-orchard-r4"; cp -r "$HERE/pkg_stage_exec/." "$CHK/poseidon-orchard-r4/"; cp "$HERE/submission-note_exec.md" "$CHK/submission-note.md"
$PY ../../../launch/prefile_check.py "$CHK" > logs/prefile_exec.txt 2>&1
cat data/numbers_exec.json; echo
echo "prefile: $(tail -1 logs/prefile_exec.txt)"; grep '^FAIL' logs/prefile_exec.txt | cut -c1-200
