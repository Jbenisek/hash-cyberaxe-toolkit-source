#!/usr/bin/env bash
S=$HOME/hashsmash/yukon/scratch_dk_0b2616e3
sed -n 150,215p $S/experiments/runner.py
sed -n 340,460p $S/experiments/runner.py
grep -rn "target_config_sha256\b" $S/scripts/pareto_pipeline.py | head -5
