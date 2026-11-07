#!/bin/bash
# post_run.sh: after the counted run: collect and verify the collision, build the package, run prefile_check.
set -u
cd "$(dirname "$0")"; HERE=$PWD
grep -q '^EXIT 0' logs/exec_run.txt || { echo "RUN DID NOT STOP WITH THE COLLISION"; exit 3; }
mkdir -p data
export R=2 PKG_OUT=pkg_stage LEDGER=exec_run.txt SIZE_FILE=logs/size.txt NOTE_OUT=submission-note.md NUMBERS=numbers.json COLLS=collisions.json
python3 collect.py exec_run collisions.json > logs/collect.txt 2>&1
python3 verify_collision.py logs/exec_run.txt > logs/verify.txt 2>&1 || { echo "VERIFY FAILED"; cat logs/verify.txt; exit 4; }
cat logs/verify.txt
python3 build_package.py > logs/build_package.txt 2>&1 || { echo "PACKAGE FAILED"; tail -12 logs/build_package.txt; exit 5; }
cat data/numbers.json; echo
CHK=$HERE/pkg_check; rm -rf "$CHK"; mkdir -p "$CHK/poseidon-orchard-r2"; cp -r "$HERE/pkg_stage/." "$CHK/poseidon-orchard-r2/"; cp "$HERE/submission-note.md" "$CHK/submission-note.md"
python3 ../../../launch/prefile_check.py "$CHK" > logs/prefile.txt 2>&1
echo "prefile: $(tail -1 logs/prefile.txt)"; grep '^FAIL' logs/prefile.txt | cut -c1-200
