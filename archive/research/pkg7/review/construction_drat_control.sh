#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# Reviewer (lens construction): negative controls for the reviewer's proof checker. CPU, one process.
P="${HASHCYBERAXE_WORKSPACE}/research/pkg6/review"
export PYTHONDONTWRITEBYTECODE=1
python3 -B "$P/construction_drat_control.py" 2>&1 | cut -c1-340 | tail -8
