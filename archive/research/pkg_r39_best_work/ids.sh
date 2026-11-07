#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
for i in 0b2616e3 0c307634 44870635 38912d66 4e396742 2c48b18c cfe5c4e2 744875ec 6b678689 0c1ef7c3; do
  echo "$i $(bash ""${HASHCYBERAXE_WORKSPACE}"/research/launch/full_id.sh" $i)"
done
