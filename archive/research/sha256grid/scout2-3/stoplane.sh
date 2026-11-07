#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# stop ONLY my own CPU lane loop (PID recorded by cpubatch.sh); the running child finishes its current run
cd "${HASHCYBERAXE_WORKSPACE}/research/sha256grid/scout2-3" || exit 1
pid=$(cat "cpubatch_lane$1.pid")
if ps -p "$pid" -o args= | grep -q "cpubatch.sh $1"; then kill "$pid" && echo "stopped lane $1 loop pid $pid"; else echo "pid $pid is not lane $1; nothing stopped"; fi
