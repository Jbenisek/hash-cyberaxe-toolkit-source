#!/usr/bin/env bash
# intake.sh SLOT : organizer intake on a staged pareto slot (read-only check), status lines
export PATH="$HOME/.local/bin:$HOME/.bun/bin:$PATH" NO_COLOR=1
cd "$HOME/hashsmash/yukon/pos_$(echo $1 | tr A-Z a-z)/pareto" || exit 1
python3 -B ../scripts/pareto_pipeline.py --family sha256 intake > /tmp/intake_$1.txt 2>&1; echo "rc=$?"; grep -oE '"(status|reason|message|error)[a-z_]*": *"[^"]*"' /tmp/intake_$1.txt | head -12; tail -5 /tmp/intake_$1.txt
