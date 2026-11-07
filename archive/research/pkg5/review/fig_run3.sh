#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/pkg5/review || exit 1
PYTHONDONTWRITEBYTECODE=1 python3 -B fig_schema.py 2> fig_schema.err | tail -2
echo "stderr lines: $(wc -l < fig_schema.err)"; tail -2 fig_schema.err | cut -c1-300
