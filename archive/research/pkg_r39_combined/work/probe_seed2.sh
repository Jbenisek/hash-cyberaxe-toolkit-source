#!/usr/bin/env bash
S=$HOME/hashsmash/yukon/scratch_dk_0b2616e3
grep -rn "seed" --include=*.py $S/experiments $S/verifier $S/judge 2>/dev/null | grep -i "sha256\|hmac\|derive\|def " | head -20
ps -eo pid,ni,pcpu,etime,args --sort=-pcpu | head -15
