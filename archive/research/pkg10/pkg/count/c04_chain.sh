#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# The three counts one after the other (4 processes each): cube k = 15, cube k = 17, the full class.
H="${HASHCYBERAXE_WORKSPACE}/research/pkg7/count"
bash "$H/c03_run.sh" a15 07ef8303 030c0303 cube 4 -capwork 24 -capx 24
bash "$H/c03_run.sh" a17 07ef831b 030c031b cube 4 -capwork 24 -capx 24
bash "$H/c03_run.sh" full none none full 4 -capwork 24 -capx 24
