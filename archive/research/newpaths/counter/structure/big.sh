#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# large-t run of tree64 (4 threads); usage: big.sh T OUTFILE TIMELIMIT
cd "${HASHCYBERAXE_WORKSPACE}/research/newpaths/counter/structure" || exit 1
T=$1; OUT=$2; LIM=$3
CH=$(cat big_chunk.hex); XS=$(cat big_x.hex)
echo "start $(date +%T) T=$T" > "$OUT"
/usr/bin/time -f "elapsed %e s, user %U s, maxrss %M KB" timeout "$LIM" ./tree64 "$T" "$CH" $XS >> "$OUT" 2>&1 &
echo $! > big_pid.txt
wait
echo "end $(date +%T) exit $?" >> "$OUT"
