#!/bin/sh
# K3 joint passes vs the exact K2-solvable set: screen, rescan, and DFS every joint-pass x whose -dA is in S2.
# Args: flags rounds maxrescan seed tag   (one process; uses its own binary copy)
cd "$(dirname "$0")"
fl="$1"; rounds="$2"; maxr="$3"; seed="$4"; tag="$5"
cp kpipe kpipe_hit
start=$(date +%s)
./kpipe_hit k3hit "$fl" 5be0cd19 s2_iv.bin 36 "$rounds" "$seed" "$maxr" "k3hit_$tag.txt" > "k3hit_$tag.out" 2>&1
echo "exit=$? wall=$(( $(date +%s) - start ))s" >> "k3hit_$tag.out"
tail -4 "k3hit_$tag.out"
