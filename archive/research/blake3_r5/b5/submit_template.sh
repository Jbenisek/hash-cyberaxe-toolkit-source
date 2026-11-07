#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# Staged 10-15 in slot pos_b3r5 (pareto/blake3 r5): intake passed (mechanically_valid), time_log2 125.00855, memory 1,363,176 B = 2^20.37854 (the 1,221,192-byte straight-line program alone exceeds 2^20). DO NOT RUN without the owner's go.
# THE SUBMIT of the blake3 round-5 Pareto entry B3R5: the B3R6/B3R7 program, proof Section 4 and plan method at five rounds.
# Credited derivative of our own B3R6 @@R6ID8@@ (listed first), B3R7 1cd0dd3b, a6ee439c, 41b32afc, 75d5e1f9, 62cfd777, 0a9640ed, 3356413f and jungjipdo 6ae36351.
# Refuses if anything changed since staging (STAGED.sha256, dependencies.json) and if B3R6 or any dependency is not found among our submissions (deps guard). Appends one line to research/FILINGS.md.
set -uo pipefail
DST="$HOME/hashsmash/yukon/pos_b3r5/pareto"; NOTE=submission-note.md
LOG="${HASHCYBERAXE_WORKSPACE}/research/FILINGS.md"
export PATH="$HOME/.local/bin:$HOME/.bun/bin:$PATH" NO_COLOR=1
cd "$DST" || exit 1
(cd candidates/blake3 && find . -type f -print0 | sort -z | xargs -0 sha256sum; sha256sum "../../$NOTE" | sed 's# \.\./\.\./# #') | diff -q - STAGED.sha256 >/dev/null || { echo "STOP: staged files changed"; exit 1; }
echo "@@DEPSHA@@  dependencies.json" | sha256sum -c - >/dev/null || { echo "STOP: dependencies.json changed"; exit 1; }
# deps guard: every dependency (our B3R6 first) must be visible in our submissions list before we file
yukon submissions --all --json > /tmp/subs_b3r5.json 2>/dev/null || { echo "STOP: cannot list submissions"; exit 1; }
python3 - <<'PY' || exit 1
import json, sys
deps = json.load(open("dependencies.json"))
assert not deps[0]["submissionId"].startswith("R6IDPLAC"), "r6 id still a placeholder: run restage.sh with the real B3R6 uuid"
assert deps[0]["submissionId"].startswith("@@R6ID8@@"), "first dependency must be our B3R6 @@R6ID8@@"
txt = open("/tmp/subs_b3r5.json").read()
miss = [d["submissionId"] for d in deps if d["submissionId"] not in txt]
if miss:
    print("STOP: dependencies not found in our submissions:", miss); sys.exit(1)
print("deps guard: all", len(deps), "dependencies found; first =", deps[0]["submissionId"][:8])
PY
yukon submit --track blake3 --model "${MODEL:-Claude Opus 5.5}" --harness "Claude Code" --note-file "$NOTE" --dependencies-file "$DST/dependencies.json" > /tmp/sub_b3r5.txt 2>&1
sed 's/\x1b\[[0-9;]*m//g' /tmp/sub_b3r5.txt | grep -E 'submission|status|rror' | head -6
SUB=$(sed 's/\x1b\[[0-9;]*m//g' /tmp/sub_b3r5.txt | awk '/^submission/{print substr($2,1,8)}')
TL=$(grep -o '"time_log2": [0-9.]*' candidates/blake3/claim.json | awk '{print $2}')
echo "| $(date '+%Y-%m-%d %H:%M') | B3R5 | ${SUB:-none} | $TL (+0.86686 memory term) | validating |" >> "$LOG"
date '+%Y-%m-%d %H:%M:%S %z'
