#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# The self-test of the program of research/pkg7 with many cases, one process per job, at most four jobs, every
# process started with nice -n 5 (after work/selftest_big.sh of research/pkg7_prep/opt). A job is rule:cases. For
# every job the program is copied outside the folder with its one line RULE_CONDITIONS set to the rule (for the
# rule that the program has, the copy is the program, byte for byte) and the copy runs the cases for the seed text.
# Each run prints the program's one JSON line, kept as work/evidence/selftest_<cases>_rule<rule>_<seed>.json after
# one line with: the SHA-256 of the program, the rule of the run, the rule of the program, the SHA-256 of the copy
# that ran, the exit status and the seconds. A file is evidence for the program only while the program still has
# the first SHA-256 of that line. CPU only. Research helper, not submitted.
#
#   wsl -d Ubuntu -- bash "./research/pkg7/work/selftest_big.sh" seed job [job ...]
set -uo pipefail
ROOT="${HASHCYBERAXE_WORKSPACE}/research/pkg8/pkg"
PROGRAM="$ROOT/blake3-r2/experiments/halfsearch.py"
SEED="$1"; shift
if [ "$#" -gt 4 ]; then echo "at most four jobs"; exit 2; fi
TMP="$HOME/hashsmash/pkg7run/selftest"; mkdir -p "$TMP"; PIDS="$TMP/pids_$$"; : > "$PIDS"
mkdir -p "$ROOT/work/evidence"
for job in "$@"; do
  IFS=: read -r rule N <<< "$job"
  SHA=$(sha256sum "$PROGRAM" | cut -c1-64)
  DEFAULT=$(sed -n 's/^RULE_CONDITIONS = \([0-9]*\)$/\1/p' "$PROGRAM")
  COPY="$TMP/halfsearch_${SHA}_rule$rule.py"
  sed "s/^RULE_CONDITIONS = .*\$/RULE_CONDITIONS = $rule/" "$PROGRAM" > "$COPY"
  if [ "$(grep -c "^RULE_CONDITIONS = $rule\$" "$COPY")" != 1 ] || [ "$(diff "$PROGRAM" "$COPY" | grep -c '^[<>]')" -gt 2 ]; then
    echo "job $job: the line RULE_CONDITIONS was not found once"; exit 2
  fi
  CSHA=$(sha256sum "$COPY" | cut -c1-64)
  OUT="$ROOT/work/evidence/selftest_${N}_rule${rule}_$SEED.json"
  ( t0=$(date +%s)
    PYTHONDONTWRITEBYTECODE=1 nice -n 5 python3 -B -s "$COPY" --selftest "$N" "$SEED" > "$TMP/${N}_rule${rule}_$SEED.out" 2> "$TMP/${N}_rule${rule}_$SEED.err"
    status=$?
    { echo "PROGRAM sha256 $SHA RULE_CONDITIONS $rule (program: $DEFAULT) copy sha256 $CSHA exit $status seconds $(( $(date +%s) - t0 ))"
      cat "$TMP/${N}_rule${rule}_$SEED.out"; } > "$OUT"
  ) &
  echo "$! $job" >> "$PIDS"
done
wait
for job in "$@"; do
  IFS=: read -r rule N <<< "$job"
  echo "rule $rule: $(head -1 "$ROOT/work/evidence/selftest_${N}_rule${rule}_$SEED.json" | cut -c1-40,82-110,180-240)"
done
