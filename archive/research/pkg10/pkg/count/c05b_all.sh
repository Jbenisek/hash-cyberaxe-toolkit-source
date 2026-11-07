#!/usr/bin/env bash
# Step 5b: the ORIGINAL calculator (pair_calc.c, option -sub) on ALL 60 betas of a cube, 4 processes, a time limit
# per beta (default 90 s; a beta that hits it is listed as not finished and is NOT in the sum).
#   c05b_all.sh NAME EXTRA_MASK EXTRA_VALUE [SECONDS]
set -uo pipefail
W='historical-sources/~~Projects/~HashSmash/workspace'
H="$W/research/pkg7/count"; S="$HOME/hashsmash/pkg7_count"; B="$S/bin"; O="$S/out/origall_$1"
NAME=$1; XM=$2; XV=$3; TMO=${4:-90}
mkdir -p "$O"; rm -f "$O"/*
t0=$(date +%s)
cut -d' ' -f1 "$H/h8_betas_pos.txt" | xargs -P 4 -I{} sh -c "OMP_NUM_THREADS=1 nice -n 5 timeout $TMO '$B/pair_calc_orig' fdb77cfd 0a08818b fffffff8 8127c181 830303cf {} 31 -y11 7af77f38 -sub $XM $XV > '$O/{}.txt' 2>&1; echo \"exit \$? beta {}\" >> '$O/{}.txt'"
{ echo "original pair_calc.c sha256 $(sha256sum "$W/research/night/main/pair_calc.c" | cut -c1-16), binary $(sha256sum "$B/pair_calc_orig" | cut -c1-16); -sub $XM $XV; time limit $TMO s per beta; $(date '+%Y-%m-%d %H:%M')"
  for b in $(cut -d' ' -f1 "$H/h8_betas_pos.txt"); do
    part=$(grep '^EXACT-E1' "$O/$b.txt" | sed 's/.*class-rate part \([0-9.]*\).*/\1/'); fb=$(grep '^EXACT-E1' "$O/$b.txt" | sed 's/.*formula fallbacks \([0-9]*\).*/\1/')
    smp=$(grep '^PAIR' "$O/$b.txt" | sed 's/.* sampled \([0-9]*\) .*/\1/'); ex=$(grep '^exit' "$O/$b.txt" | cut -d' ' -f2)
    echo "$b part ${part:-none} sampled ${smp:-none} fallbacks ${fb:-none} exit ${ex:-none}"
  done; } > "$H/origall_$NAME.txt"
echo "seconds $(( $(date +%s) - t0 )); $(awk 'NR > 1 {n++; if ($9 == 0 && $3 != "none") {f++; s += $3; if ($5 > 0) sm++} else u++} END {printf "betas %d, finished %d (with a sampled outcome %d), not finished %d, sum of the finished parts %.4f", n, f, sm, u, s}' "$H/origall_$NAME.txt")"
