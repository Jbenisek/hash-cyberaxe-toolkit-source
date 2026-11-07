cd historical-sources/~~Projects/~HashSmash/workspace
ls ~/hashsmash/yukon | grep -i "pos_r1_pkg\|pos_b3r3pv"
nice -n 10 bash research/launch/slotstage/slotstage_pareto.sh B3R4T blake3 4 research/blake3_r4/b4/pkg/blake3 research/blake3_r4/b4/pkg/submission-note.md pos_b3r3pv 2>&1 | tail -25
