"""Writes research/launch/submit_pareto_<slot>.sh for a staged rolled r6/r5 package (modelled on submit_pareto_pos_b3r7c.sh). Does NOT run it.
usage (WSL): python3 -B mkroll8_submit.py R <slot dir name e.g. pos_b3r6d> <label e.g. B3R6c> <first-dep id8> <old row text e.g. "125.03893 (57174971)">"""
import sys, os, re, hashlib, json
R, slot, label, first, old = int(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
WS = 'historical-sources/~~Projects/~HashSmash/workspace'
S = os.path.join(os.path.expanduser("~"), "hashsmash/yukon", slot, "pareto")
dep = open(os.path.join(S, "dependencies.json"), "rb").read()
sha = hashlib.sha256(dep).hexdigest()
deps = json.loads(dep)
assert deps[0]["submissionId"].startswith(first) and deps[1]["submissionId"].startswith("a2e94df7"), [d["submissionId"] for d in deps]
assert os.path.exists(os.path.join(S, "STAGED.sha256"))
tl = re.search(r'"time_log2": *([0-9.]+)', open(os.path.join(S, "candidates/blake3/claim.json")).read()).group(1)
out = os.path.join(WS, "research/launch/submit_pareto_%s.sh" % slot)
assert not os.path.exists(out), out
txt = f'''#!/usr/bin/env bash
# Staged in slot {slot} (pareto/blake3 r{R}, the rolled round body of B3R7c a2e94df7 taken to {R} rounds): time_log2 {tl} (our filed row {old}). DO NOT RUN without the owner's go.
# THE SUBMIT of {label}: same search, plan method, Section 4 and experiments as the filed row; the step is rolled (memory term 0).
# Dependencies: {first} first, then a2e94df7 (see dependencies.json).
# Refuses if anything changed since staging (STAGED.sha256, dependencies.json) and if any dependency is not found among our submissions (deps guard). Appends one line to research/FILINGS.md.
set -uo pipefail
DST="$HOME/hashsmash/yukon/{slot}/pareto"; NOTE=submission-note.md
LOG='{WS}/research/FILINGS.md'
export PATH="$HOME/.local/bin:$HOME/.bun/bin:$PATH" NO_COLOR=1
cd "$DST" || exit 1
(cd candidates/blake3 && find . -type f -print0 | sort -z | xargs -0 sha256sum; sha256sum "../../$NOTE" | sed 's# \\.\\./\\.\\./# #') | diff -q - STAGED.sha256 >/dev/null || {{ echo "STOP: staged files changed"; exit 1; }}
echo "{sha}  dependencies.json" | sha256sum -c - >/dev/null || {{ echo "STOP: dependencies.json changed"; exit 1; }}
yukon submissions --all --json mooselumph/hashsmash-pareto/blake3 > /tmp/subs_{slot}.json 2>/dev/null || {{ echo "STOP: cannot list submissions"; exit 1; }}
python3 - <<'PY' || exit 1
import json, sys
deps = json.load(open("dependencies.json"))
assert deps[0]["submissionId"].startswith("{first}"), "first dependency must be {first}"
txt = open("/tmp/subs_{slot}.json").read()
miss = [d["submissionId"] for d in deps if d["submissionId"] not in txt]
if miss:
    print("STOP: dependencies not found in our submissions:", miss); sys.exit(1)
print("deps guard: all", len(deps), "dependencies found; first =", deps[0]["submissionId"][:8])
PY
yukon submit --track blake3 --model "${{MODEL:-Claude Opus 5.5}}" --harness "Claude Code" --note-file "$NOTE" --dependencies-file "$DST/dependencies.json" > /tmp/sub_{slot}.txt 2>&1
sed 's/\\x1b\\[[0-9;]*m//g' /tmp/sub_{slot}.txt | grep -E 'submission|status|rror' | head -6
SUB=$(sed 's/\\x1b\\[[0-9;]*m//g' /tmp/sub_{slot}.txt | awk '/^submission/{{print substr($2,1,8)}}')
TL=$(grep -o '"time_log2": [0-9.]*' candidates/blake3/claim.json | awk '{{print $2}}')
echo "| $(date '+%Y-%m-%d %H:%M') | {label} | ${{SUB:-none}} | $TL (rolled; filed row {old}) | validating |" >> "$LOG"
date '+%Y-%m-%d %H:%M:%S %z'
'''
open(out, "w", newline="\n").write(txt)
os.chmod(out, 0o755)
print(out)
