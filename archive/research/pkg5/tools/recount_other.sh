#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# The calculator on OTHER constants, for the pairs whose sampler figures are quoted in pkg5 Section 10 as a
# check of the calculator: the constants of the 112.4 submission (classes e96d6d6b and e96d7579) and one
# other pin of the night's search ("pin A"). Same binary and options as recount_exact.sh; full output lines
# kept in research/pkg5/evidence/other_pairs_recount.txt. CPU only, four threads. Research helper.
#
#   wsl -d Ubuntu -- bash './research/pkg5/tools/recount_other.sh'
set -uo pipefail
B="$HOME/hashsmash/bin"
OUT="${HASHCYBERAXE_WORKSPACE}/research/pkg5/evidence"
mkdir -p "$OUT"
FILE="$OUT/other_pairs_recount.txt"
: > "$FILE"
one() {   # label D3 D11 DELTA Y3 Y11 ETA BETA
  start=$(date +%s)
  echo "CASE $1: D3 $2 D11 $3 delta $4 Y3 $5 Y11 $6 eta $7 beta $8" >> "$FILE"
  OMP_NUM_THREADS=4 timeout 3600 "$B/night_pair_calc" "$2" "$3" "$4" "$5" "$7" "$8" 31 -y11 "$6" >> "$FILE" 2>&1
  echo "DONE $1 exit $? seconds $(( $(date +%s) - start ))" >> "$FILE"
}
one filed-e96d6d6b-953908d0 6d59272d 708af931 00000002 c952ec69 31fc40b2 e96d6d6b 953908d0
one filed-e96d6d6b-953f08d0 6d59272d 708af931 00000002 c952ec69 31fc40b2 e96d6d6b 953f08d0
one filed-e96d6d6b-95390bd0 6d59272d 708af931 00000002 c952ec69 31fc40b2 e96d6d6b 95390bd0
one filed-e96d7579-953908d0 6d59272d 708af931 00000002 c952ec69 31fc40b2 e96d7579 953908d0
one pinA-31b13fea-c93210a5  3ae5f151 1ef63391 00000002 628da757 d0b4e857 31b13fea c93210a5
grep -E '^CASE|^EXACT|^DONE|^PAIR' "$FILE" | cut -c1-300
