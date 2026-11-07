#!/bin/bash
cd "$(dirname "$0")"
f=$1; n=$2; t=$3
/usr/bin/time -f "%e s" cryptominisat5 --verb 0 --maxsol "$n" --maxtime "$t" "$f" > "${f%.cnf}.sol" 2> "${f%.cnf}.time"
echo "$f: $(grep -c '^s SATIS' "${f%.cnf}.sol") solutions in $(tail -1 "${f%.cnf}.time")"
