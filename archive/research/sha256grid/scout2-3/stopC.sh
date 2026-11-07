#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# stop ONLY my own lane C process (pid recorded by cpulaneC.sh, exec'd into q3gpu2 cpubatch 4444)
cd "${HASHCYBERAXE_WORKSPACE}/research/sha256grid/scout2-3" || exit 1
pid=$(cat cpulaneC.pid)
if ps -p "$pid" -o args= | grep -q "q3gpu2 cpubatch 4444"; then kill "$pid" && echo "stopped lane C pid $pid"; else echo "pid $pid is not lane C; nothing stopped"; fi
