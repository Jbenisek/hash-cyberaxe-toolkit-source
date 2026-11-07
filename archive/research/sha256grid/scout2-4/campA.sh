#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# campaign A: cell replica (cut 37) and tail-only relaxation (cut 22), filed sizes, NP 4000
cd "${HASHCYBERAXE_WORKSPACE}/research/sha256grid/scout2-4" || exit 1
date > campA.log
for s in 31011 31012 31013 31014 31015 31016 31017 31018; do ./smc38r C $s 4000 2048 64 64 8 8 4 8192 0 0 0 0 0 0 0 >> campA.log; done
for s in 32011 32012 32013 32014 32015 32016 32017 32018; do ./smc38r 22 $s 4000 2048 64 64 8 8 4 8192 0 0 0 0 0 0 131072 >> campA.log; done
for s in 33011 33012 33013 33014 33015 33016 33017 33018; do ./smc38r 17 $s 4000 2048 64 64 8 8 4 8192 0 4096 4096 512 512 128 131072 >> campA.log; done
date >> campA.log