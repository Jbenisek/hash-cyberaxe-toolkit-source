#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
bash "${HASHCYBERAXE_WORKSPACE}/research/dig/incoming3/blake3-r3-U55/work/pin_run.sh"
bash "${HASHCYBERAXE_WORKSPACE}/research/dig/incoming3/blake3-r3-U61/work/tag_run.sh"
echo all finished > "${HASHCYBERAXE_WORKSPACE}/research/dig/incoming3/blake3-r3-U55/work/chain_done.txt"
