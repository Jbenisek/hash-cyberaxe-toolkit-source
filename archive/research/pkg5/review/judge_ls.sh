#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# hostile-judge lens: list sizes of the pkg5 files (read-only)
P="${HASHCYBERAXE_WORKSPACE}/research/pkg5"
OUT="$P/review/judge_ls.out"
{
  find "$P" -type f -printf '%s %P\n' | sort -k2
} > "$OUT"
wc -l < "$OUT"
which kissat cadical minisat cryptominisat5 approxmc python3 2>/dev/null | head -8
nproc
