#!/usr/bin/env bash
# Progress of the running count: DONE lines per run, processes of this job, load.
S="$HOME/hashsmash/pkg7_count"; O="$S/out"
for d in "$O"/*.d; do [ -d "$d" ] && echo "$(basename "$d"): DONE $(cat "$d"/raw_*.out 2>/dev/null | grep -c '^DONE') of $(cat "$d"/slice_*.lst | wc -l), stderr lines $(cat "$d"/raw_*.err 2>/dev/null | wc -l)"; done
echo "pair_calc_sub processes $(pgrep -c -f "$S/bin/pair_calc_sub"), load $(cut -d' ' -f1-3 /proc/loadavg), $(date '+%H:%M:%S')"
