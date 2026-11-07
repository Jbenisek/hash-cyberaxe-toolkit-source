cd "historical-sources/~~Projects/~HashSmash/workspace"
nice -n 10 bash research/launch/file_pkg.sh pareto blake3 4 research/blake3_r4/bsel/pkg --base research/blake3_r4/compact_u5b/pkg --base-slot pos_b3r4u5b --intake --stage-only 2>&1 | tail -60
