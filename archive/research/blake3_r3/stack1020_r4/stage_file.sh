#!/usr/bin/env bash
cd "historical-sources/~~Projects/~HashSmash/workspace"
export PATH=$HOME/.local/bin:$HOME/.bun/bin:$PATH
nice -n 10 bash research/launch/file_pkg.sh pareto blake3 4 research/blake3_r3/stack1020_r4/pkg --base research/blake3_r3/stack1020/pkg --base-slot pos_b3r4d --intake --stage-only
