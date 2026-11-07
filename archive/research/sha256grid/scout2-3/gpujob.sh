#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# GPU job wrapper: takes GPU.lock only if free (noclobber), runs the given command, removes ONLY its own lock on exit.
# usage: gpujob.sh <tag> <command...>
cd "${HASHCYBERAXE_WORKSPACE}/research/sha256grid/scout2-3" || exit 1
LOCK="${HASHCYBERAXE_WORKSPACE}/research/sha256grid/GPU.lock"
LABEL="scout2-3 (SHA-256 r38 q3 GPU SMC, $1) since $(date '+%Y-%m-%d %H:%M:%S')"
shift
if ( set -o noclobber; printf '%s\n' "$LABEL" > "$LOCK" ) 2>/dev/null; then
  trap 'if [ "$(head -1 "$LOCK" 2>/dev/null | tr -d "\r")" = "$LABEL" ]; then rm -f "$LOCK"; echo "lock released"; fi' EXIT
  echo "lock taken: $LABEL"
  echo $$ > gpujob.pid
  "$@"
  echo "exit $?"
else
  echo "GPU.lock held: $(cat "$LOCK")"; exit 9
fi
