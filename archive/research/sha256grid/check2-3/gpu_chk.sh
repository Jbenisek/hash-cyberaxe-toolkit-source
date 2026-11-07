#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# check2-3 GPU job: takes GPU.lock only if free (noclobber), removes ONLY its own lock on exit.
# (a) reproduce G2 runs 0..1023 and 130048..131071 (master 20261010, V 4096) and G3a runs 0..1023 (master 20261012, V 1)
#     with a binary built here from the scout's source -> compare log lines with the scout's logs;
# (b) fresh replicate, master 8675309 (chosen by the checker), runs 0..32767, V 4096, same SMC parameters.
cd "${HASHCYBERAXE_WORKSPACE}/research/sha256grid/check2-3" || exit 1
LOCK="${HASHCYBERAXE_WORKSPACE}/research/sha256grid/GPU.lock"
LABEL="check2-3 (SHA-256 r38 q3 GPU replicate check) since $(date '+%Y-%m-%d %H:%M:%S')"
if ( set -o noclobber; printf '%s\n' "$LABEL" > "$LOCK" ) 2>/dev/null; then
  trap 'if [ "$(head -1 "$LOCK" 2>/dev/null | tr -d "\r")" = "$LABEL" ]; then rm -f "$LOCK"; echo "lock released $(date +%H:%M:%S)"; fi' EXIT
  echo "lock taken: $LABEL"
  echo $$ > gpu_chk.pid
  P="4000 2048 64 64 8 8 4 8192"
  ./q3gpu_chk gpusmc 20261010 0 1024 $P 4096 rep_g2a 1 2> rep_g2a.err; echo "rep_g2a exit $?"
  ./q3gpu_chk gpusmc 20261010 130048 1024 $P 4096 rep_g2b 1 2> rep_g2b.err; echo "rep_g2b exit $?"
  ./q3gpu_chk gpusmc 20261012 0 1024 $P 1 rep_g3a 1 2> rep_g3a.err; echo "rep_g3a exit $?"
  ./q3gpu_chk gpusmc 8675309 0 32768 $P 4096 fresh_m8675309 1 2> fresh_m8675309.err; echo "fresh exit $?"
  tail -1 fresh_m8675309.log
  echo "done $(date +%H:%M:%S)"
else
  echo "GPU.lock held: $(cat "$LOCK")"; exit 9
fi
