#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
echo "STOP: copy of a script of research/pkg6 inside research/pkg7; it still points at research/pkg6, which is filed and read only. Not ported yet (PROGRAM_STEP.md, section 6 item 1)."; exit 9
# The self-test of the program in the package with many batches, once for every rule given (4, 5 or 6 conditions),
# one process per rule. The program has one line RULE_CONDITIONS = n. For every rule the program is copied outside
# the package with that one line set to the rule (for the rule that the package uses the copy is the program,
# byte for byte) and the copy runs N batches for the seed text. Each run prints the program's one JSON line, kept
# as evidence/selftest_<N>_rule<n>_<seed>.json after one line with: the SHA-256 of the program in the package, the
# rule of the run, the rule of the package, the SHA-256 of the copy that ran, the exit status and the seconds.
# A file is evidence for the program only while the program still has the first SHA-256 of that line.
# CPU only, one thread per rule. Research helper, not submitted.
#
#   wsl -d Ubuntu -- bash './research/pkg6/tools/selftest_big.sh' N seed rule [rule ...]
set -uo pipefail
PKG="${HASHCYBERAXE_WORKSPACE}/research/pkg6"
PROGRAM="$PKG/blake3-r2/experiments/halfsearch.py"
N="$1"; SEED="$2"; shift 2
SHA=$(sha256sum "$PROGRAM" | cut -c1-64)
DEFAULT=$(sed -n 's/^RULE_CONDITIONS = \([0-9]*\)$/\1/p' "$PROGRAM")
TMP="$HOME/hashsmash/pkg6-selftest"; mkdir -p "$TMP"
for rule in "$@"; do
  COPY="$TMP/halfsearch_${SHA}_rule$rule.py"
  sed "s/^RULE_CONDITIONS = .*\$/RULE_CONDITIONS = $rule/" "$PROGRAM" > "$COPY"
  if [ "$(grep -c "^RULE_CONDITIONS = $rule\$" "$COPY")" != 1 ] || [ "$(diff "$PROGRAM" "$COPY" | grep -c '^[<>]')" -gt 2 ]; then
    echo "rule $rule: the line RULE_CONDITIONS was not found once"; exit 2
  fi
  CSHA=$(sha256sum "$COPY" | cut -c1-64)
  ( t0=$(date +%s)
    PYTHONDONTWRITEBYTECODE=1 nice -n 5 python3 -B -s "$COPY" --selftest "$N" "$SEED" > "$TMP/selftest_${N}_rule${rule}_$SEED.out" 2> "$TMP/selftest_${N}_rule${rule}_$SEED.err"
    status=$?
    { echo "PROGRAM sha256 $SHA RULE_CONDITIONS $rule (package: $DEFAULT) copy sha256 $CSHA exit $status seconds $(( $(date +%s) - t0 ))"
      cat "$TMP/selftest_${N}_rule${rule}_$SEED.out"; } > "$PKG/evidence/selftest_${N}_rule${rule}_$SEED.json"
  ) &
done
wait
for rule in "$@"; do head -1 "$PKG/evidence/selftest_${N}_rule${rule}_$SEED.json" | cut -c1-230; done
