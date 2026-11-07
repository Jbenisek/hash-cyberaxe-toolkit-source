export PATH="$HOME/.local/bin:$HOME/.bun/bin:$PATH" NO_COLOR=1
cd ~/hashsmash/yukon/pos_b3r4f2/pareto
yukon submissions --all --json mooselumph/hashsmash-pareto/blake3 2>/dev/null | grep -o 'eaef120f-[0-9a-f-]*' | sort -u
