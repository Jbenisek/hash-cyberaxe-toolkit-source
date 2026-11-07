#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
S=$HOME/hashsmash/yukon/scratch_dk_0b2616e3/pareto/candidates/sha256
D="${HASHCYBERAXE_WORKSPACE}"/research/pkg_r39_combined/work/dk
mkdir -p $D; cp -r $S/. $D/; find $S -type f | xargs ls -la
