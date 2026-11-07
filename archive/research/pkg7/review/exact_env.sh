#!/bin/bash
# exact lens: look only; copies the organizer's reference hash into a scratch directory of this review.
M=~/hashsmash/hash-smash-pkg7text
S=~/hashsmash/exact_review
mkdir -p "$S"
cp "$M/verifier/blake3.py" "$S/org_blake3.py"
cp "$M/verifier/hash_functions.py" "$S/org_hash_functions.py"
wc -l "$S/org_blake3.py" "$S/org_hash_functions.py"
grep -n "^def \|^class \|rounds" "$S/org_blake3.py" | head -30
grep -n "blake3\|rounds" "$S/org_hash_functions.py" | head -12
