#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# count-cost reviewer: what is installed, and the shape of the files that will be read. Prints at most ten lines.
W="${HASHCYBERAXE_WORKSPACE}/research"
O="$W/pkg6/review/count-cost_env.out"
{
  for t in kissat cadical cryptominisat5 approxmc drat-trim ganak d4 sharpSAT python3 gcc rustc; do printf '%s: %s\n' "$t" "$(command -v $t || echo none)"; done
  python3 -c 'import numpy; print("numpy", numpy.__version__)' 2>&1
  nproc
  ls -la "$HOME/hashsmash/bin/night_pair_calc2" 2>&1
  sha256sum "$HOME/hashsmash/bin/night_pair_calc2" 2>&1 | cut -c1-64
  echo '--- H8_calc2_mass.txt head'
  head -c 1800 "$W/h8/counts/H8_calc2_mass.txt"
  echo; echo '--- pairs_recount head'
  head -c 2200 "$W/pkg6/evidence/pairs_recount_830303cf.txt"
  echo; echo '--- gpt csv head'
  head -n 4 "$W/pkg6/evidence/gpt_recount/gpt_sol_parts_A.csv"
  echo '--- rule_a_sat rule5 head'
  head -n 8 "$W/pkg6/evidence/rule_a_sat_830303cf_rule5.txt" | cut -c1-260
  echo '--- sat2 cadical rule5 head and counts'
  head -n 6 "$W/pkg6/evidence/rule_a_sat2_cadical_830303cf_rule5.txt" | cut -c1-260
  for f in "$W"/pkg6/evidence/rule_a_sat2_*_rule5.txt; do echo "$(basename "$f") BASE SAT $(grep -c '^BASE .* SAT' "$f") BASE lines $(grep -c '^BASE ' "$f") VIOLATE UNSAT $(grep -c '^VIOLATE .* UNSAT' "$f") VIOLATE lines $(grep -c '^VIOLATE ' "$f") other $(grep -c -v -E '^(BASE|VIOLATE|#|SUMMARY)' "$f")"; done
  echo '--- sat2 log'
  cat "$W/pkg6/evidence/rule_a_sat2_all.log" | cut -c1-240
  echo '--- gpt rust source: lines and io'
  wc -l "$W/pkg6/evidence/gpt_recount/gpt_sol_independent_a.rs"
  grep -n -E 'std::(fs|net|process|env)|Command|TcpStream|File::|unsafe|extern' "$W/pkg6/evidence/gpt_recount/gpt_sol_independent_a.rs" | head -30
  ls -la "$W/pkg6/evidence/gpt_recount/"
  ls "$W/h8/counts/sol_rerun" 2>&1 | head
} > "$O" 2>&1
echo "written $(wc -l < "$O") lines to count-cost_env.out"
