#!/usr/bin/env bash
# Step 0: scratch directory, machine load, what else is running. Prints a few lines.
set -uo pipefail
S="$HOME/hashsmash/pkg7_count"
mkdir -p "$S/bin" "$S/out"
echo "scratch $S; gcc $(gcc -dumpversion); python $(python3 -V 2>&1 | cut -d' ' -f2); cores $(nproc)"
echo "load $(cut -d' ' -f1-3 /proc/loadavg); memory free MB $(free -m | awk '/^Mem/ {print $7}')"
echo "busy processes (cpu > 20%): $(ps -eo pcpu,comm --sort=-pcpu | awk 'NR > 1 && $1 > 20 {printf "%s(%s) ", $2, $1}' | cut -c1-300)"
nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader 2>/dev/null | head -1
