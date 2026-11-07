#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# lens EVERY FIGURE: file lists (names only) to a file
P="${HASHCYBERAXE_WORKSPACE}"/research
R="$P/pkg5/review"
{
echo "== night/cheaper"
ls -la --time-style=+%H:%M "$P/night/cheaper" | awk '{print $5, $6, $7}'
echo "== pkg5 tools"
ls -la --time-style=+%m-%d_%H:%M "$P/pkg5/tools" "$P/pkg5" "$P/pkg5/src" "$P/pkg5/blake3-r2" "$P/pkg5/blake3-r2/experiments" | awk '{print $5, $6, $7}'
echo "== which solvers"
for b in kissat cadical cryptominisat5 minisat approxmc drat-trim python3; do echo "$b: $(command -v $b)"; done
python3 -c "import jsonschema; print('jsonschema', jsonschema.__version__)" 2>&1
echo "== nproc $(nproc)  load $(cut -d' ' -f1-3 /proc/loadavg)"
ls "$P/../hash-smash/schemas" 2>&1 | head -20
} > "$R/fig_ls.out" 2>&1
wc -l "$R/fig_ls.out"
