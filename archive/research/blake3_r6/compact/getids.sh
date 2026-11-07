export PATH="$HOME/.local/bin:$HOME/.bun/bin:$PATH" NO_COLOR=1
yukon submissions --all --json mooselumph/hashsmash-pareto/blake3 > /tmp/s6.json 2>/dev/null
grep -o 'a5248fe7-[0-9a-f-]*' /tmp/s6.json | sort -u; grep -o '616120b2-[0-9a-f-]*' /tmp/s6.json | sort -u
