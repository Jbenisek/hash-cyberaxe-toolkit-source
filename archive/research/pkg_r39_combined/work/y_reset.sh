#!/usr/bin/env bash
set -uo pipefail
export PATH="$HOME/.local/bin:$HOME/.bun/bin:$PATH" NO_COLOR=1
S=$HOME/hashsmash/yukon/scratch_dk_0b2616e3
[ -e "$S" ] && { echo "exists $S"; ls $S; exit 0; }
cp -a $HOME/hashsmash/yukon/pos_s256u5_r39 "$S" || exit 1
cd "$S/pareto" 2>/dev/null || cd "$S"
pwd; cat .yukon/*.json 2>/dev/null | head -20; ls -a
yukon reset 0b2616e3 --force 2>&1 | tail -15
git log --oneline -3
ls candidates/sha256 candidates/sha256/experiments 2>&1 | head
