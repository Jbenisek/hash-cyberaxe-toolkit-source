#!/bin/bash
# Verify the COLLISION lines of each RR=3 log with the organizer-compatible check of the r5 package (verify_collision.py: big-int reference + organizer's verifier.poseidon digest). R=3.
cd "$(dirname "$0")" || exit 1
for f in logs/r3_s*.txt; do
  echo "== $f"; grep -E "^(RESULT|TRIALS|SUMMARY|EXIT|TRIALROW [0-9]+ centre)|COLLISION" $f
  grep -q COLLISION $f && R=3 python3 verify_collision.py $f
done
