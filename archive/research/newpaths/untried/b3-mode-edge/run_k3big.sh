#!/bin/sh
# K3 at h = IV: large screen + rescans, every distinct dS3 looked up in the exact K2-solvable set S2 (one process).
# Args: flags rounds maxrescan seed outtag
cd "$(dirname "$0")"
fl="$1"; rounds="$2"; maxr="$3"; seed="$4"; tag="$5"
cp kpipe kpipe_k3
start=$(date +%s)
./kpipe_k3 k3find "$fl" a54ff53a 5be0cd19 36 "$rounds" "$seed" "$maxr" "k3sol_$tag.txt" 1 s2_iv.bin > "k3big_$tag.out" 2>&1
echo "exit=$? wall=$(( $(date +%s) - start ))s" >> "k3big_$tag.out"
tail -3 "k3big_$tag.out"
