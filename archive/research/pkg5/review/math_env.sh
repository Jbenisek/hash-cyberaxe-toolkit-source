#!/usr/bin/env bash
# Reviewer (lens: mathematics and cost): what is installed, what is running. Read-only.
for t in kissat cadical cryptominisat5 approxmc ganak sharpSAT drat-trim python3 gcc; do
  p=$(command -v $t 2>/dev/null); echo "$t: ${p:-none}"
done | tr '\n' ' '
echo
ls -la $HOME/hashsmash/bin/ 2>/dev/null | grep -c . | sed 's/^/files in bin: /'
ls $HOME/hashsmash/bin/ | grep -E 'pair_calc' | tr '\n' ' '
echo
sha256sum $HOME/hashsmash/bin/night_pair_calc2 | cut -c1-20
uptime | sed 's/.*load/load/'
