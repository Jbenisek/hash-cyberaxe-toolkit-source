#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
W="${HASHCYBERAXE_WORKSPACE}"/research
for p in "s108 f1027030816"; do set -- $p
  for f in r39joint.py r39tail.py; do a=$(sha256sum < $W/pkg_r39_$1/sha256/experiments/$f | cut -c1-16); b=$(sha256sum < ~/hashsmash/yukon/pos_$2/pareto/candidates/sha256/experiments/$f | cut -c1-16); echo "$1 $f local $a staged $b $([ $a = $b ] && echo SAME || echo DIFF)"; done; done
