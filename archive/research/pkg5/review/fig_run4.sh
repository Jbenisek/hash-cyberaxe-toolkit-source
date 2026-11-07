#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# lens EVERY FIGURE: the package's own numerical check, output to a file (read only; -B: no bytecode written anywhere)
P="${HASHCYBERAXE_WORKSPACE}"/research/pkg5
cd "$P" || exit 1
PYTHONDONTWRITEBYTECODE=1 nice -n 10 python3 -B check_pkg5.py > "$P/review/fig_check_pkg5.out" 2> "$P/review/fig_check_pkg5.err"
echo "exit $?"
echo "ok lines: $(grep -c '^ *ok' "$P/review/fig_check_pkg5.out")  lines not ok: $(grep -ciE 'fail|wrong|differ' "$P/review/fig_check_pkg5.out")  stderr: $(wc -l < "$P/review/fig_check_pkg5.err")"
tail -4 "$P/review/fig_check_pkg5.out" | cut -c1-220
