#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# Reviewer: is cadical's internal proof checking really active with --check --checkproof=3 in this build?
R="${HASHCYBERAXE_WORKSPACE}/research/pkg5/review"
T="$HOME/hashsmash/pkg5-review-math"
python3 -B - "$R" "$T/probe.cnf" <<'EOF'
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, sys.argv[1])
import math_sat as ms
c, _ = ms.build(0x481c6852, 0x481c1830, 0x2d5730a9, "violate")
c.write(sys.argv[2])
EOF
cadical -v --check --checkproof=3 "$T/probe.cnf" > "$T/probe.out" 2>&1; echo "exit $?"
grep -iE 'checker|checked|lrat' "$T/probe.out" | cut -c1-110 | head -7
rm -f "$T/probe.cnf"
