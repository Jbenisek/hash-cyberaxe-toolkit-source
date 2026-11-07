export PATH="$HOME/.local/bin:$HOME/.bun/bin:$PATH" NO_COLOR=1
yukon submissions --all --json mooselumph/hashsmash-pareto/blake3 > /tmp/subs_b9.json 2>/dev/null
grep -o '1cf99082-[0-9a-f-]*' /tmp/subs_b9.json | sort -u
