#!/usr/bin/env bash
# tail_var_stats.sh : per-variant tail bound (14 public-seed runs) -> mean, lcb999, QDECL; sorted best first.
cd "$(dirname "$0")"
for sig in $(cat tail_var/RUNS.txt); do
  n=$(ls tail_var/$sig/out_*.json 2>/dev/null | xargs -I{} sh -c 'test -s {} && echo x' | wc -l)
  [ "$n" -eq 14 ] || { echo "$sig incomplete ($n/14)"; continue; }
  python tail_stats_dir.py tail_var/$sig 2>&1 | grep -E "mean_lin" | sed "s/^/$sig /"
done | sort -k3 -n -r | tee tail_var/SUMMARY.txt
