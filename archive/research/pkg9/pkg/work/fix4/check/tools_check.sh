#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# FIX4 check: run the read-only checks (build --check, fmt, text scan) with output in check/. Nothing is written elsewhere.
P="${HASHCYBERAXE_WORKSPACE}/research/pkg7"; O="$P/work/fix4/check/tools_out.txt"
cd "$P"
{
echo "== build_pkg7.py --check"; nice -n 5 python3 -B tools/build_pkg7.py --check; echo "exit $?"
echo "== build_pkg7.py --program"; nice -n 5 python3 -B tools/build_pkg7.py --program; echo "exit $?"
echo "== fmt_pkg7.py"; nice -n 5 python3 -B tools/fmt_pkg7.py; echo "exit $?"
echo "== text_scan_pkg7.py"; nice -n 5 python3 -B tools/text_scan_pkg7.py; echo "exit $?"
echo "== pycache in package"; find "$P/blake3-r2" -name '__pycache__' -o -name '*.pyc' | wc -l
} > "$O" 2>&1
grep -E '^==|^exit|DRIFT|unchanged|RESULT|findings|ranges:|claim:' "$O" | cut -c1-150 | head -10
