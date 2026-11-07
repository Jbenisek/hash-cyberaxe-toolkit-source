#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/sha256grid/scout2-1" || exit 1
for f in *.pid; do P=$(cat $f); if [ -e /proc/$P ]; then echo "$f pid $P STILL RUNNING: $(tr '\0' ' ' < /proc/$P/cmdline)"; else echo "$f pid $P ended"; fi; done
for f in *.done; do echo "$f: $(cat $f)"; done