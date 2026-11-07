#!/usr/bin/env bash
S=$HOME/hashsmash/yukon/scratch_dk_0b2616e3
ls $S $S/scripts | head -40
grep -rn "def .*seed\|sha256(.*seed\|\"seed\"" $S/scripts/*.py $S/pareto/*.py 2>/dev/null | head -20
python3 -B $S/scripts/pareto_pipeline.py --help 2>&1 | head -30
nproc; cat /proc/loadavg
