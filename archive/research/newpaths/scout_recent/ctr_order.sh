#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# ctr_order.sh TARGETS OUTFILE [extra basis_sat options]: one basis with the chunk counter word T0 free
# (COUNTER=1, PIN_EXTRA=w14 = pin H8) and its complete solving order.
cd "${HASHCYBERAXE_WORKSPACE}/research/newpaths/scout_recent"
export PYTHONDONTWRITEBYTECODE=1 COUNTER="${COUNTER:-1}" PIN_EXTRA="${PIN_EXTRA-w14}"
t="$1"; o="$2"; shift 2
python3 -B basis_sat_ctr.py "$t" --order --levels 110 --time 120 "$@" > "$o" 2>&1
head -1 "$o" | cut -c1-300; wc -l < "$o"
