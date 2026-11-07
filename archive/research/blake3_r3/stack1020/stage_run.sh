#!/usr/bin/env bash
cd "historical-sources/~~Projects/~HashSmash/workspace"
export PATH=$HOME/.local/bin:$HOME/.bun/bin:$PATH
P=research/blake3_r3/stack1020/pkg
(cd $P/blake3/experiments && nice -n 10 python3 -B bsrho.py --selftest | tail -4; rm -rf __pycache__)
nice -n 10 python3 research/launch/prefile_scan.py $P research/blake3_r3/compact_u5b/pkg
