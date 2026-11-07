#!/bin/sh
# K2-solvable set S2 at two non-IV chaining values (the mode lever: an internal block after a prefix redraws h2,h6).
cd "$(dirname "$0")"
start=$(date +%s)
./kpipe s2enum 9e3779b9 7f4a7c15 64 s2_hA.bin > s2enum_hA.out 2>&1
./kpipe s2enum 243f6a88 85a308d3 64 s2_hB.bin > s2enum_hB.out 2>&1
echo "wall=$(( $(date +%s) - start ))s"
cat s2enum_hA.out s2enum_hB.out
