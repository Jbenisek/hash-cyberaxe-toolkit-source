#!/bin/bash
# usage: run_many.sh <parallel N> <centres file (one decimal per line)> [outdir]
# runs one certb_fast process per centre, N at a time, all on the one GPU (about 4.5 GB device memory each)
cd "$(dirname "$0")"
N="$1"; list="$2"; od="${3:-out/many}"; mkdir -p "$od"
cat "$list" | nl -w1 -s' ' | xargs -P "$N" -L 1 bash -c 'nice -n 10 ./certb_fast ddf --F "${F_BIN:-tests/data/F_j0.bin}" --center "$1" --out "'"$od"'/c$0" > "'"$od"'/c$0.log" 2>&1'
for f in "$od"/c*.log; do echo "$f $(grep '"stage":"done"' "$f" | sed 's/.*"aborted_early":\([a-z]*\).*"residual_degree":\([0-9]*\),.*"ddf_total":\([0-9.]*\).*/aborted=\1 residual=\2 ddf_s=\3/')"; done
