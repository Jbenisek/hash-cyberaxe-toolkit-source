#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# Reviewer (lens construction): the two solver questions for rule A with the reviewer's own formula. CPU only, 3 workers.
P="${HASHCYBERAXE_WORKSPACE}/research/pkg6/review"
export PYTHONDONTWRITEBYTECODE=1
python3 -B "$P/construction_rule.py" 3 2>&1 | cut -c1-420 | tail -12
