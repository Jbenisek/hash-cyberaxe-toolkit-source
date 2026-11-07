"""Writes research/launch/submit_pareto_pos_b3r3v2.sh for the staged Lemma-2-v2 rebuild of 62cfd777 (modelled on submit_pareto_pos_b3r7c.sh). Does NOT run it.
Usage (WSL): python3 -B mk_submit.py"""
import os, json, hashlib, re

WS = 'historical-sources/~~Projects/~HashSmash/workspace'
HOME = os.path.expanduser("~")
slot, label, first = "pos_b3r3v2", "B3R3V2", "62cfd777"
S = os.path.join(HOME, "hashsmash/yukon", slot, "pareto")
dep = open(os.path.join(S, "dependencies.json"), "rb").read()
sha = hashlib.sha256(dep).hexdigest()
deps = json.loads(dep)
assert deps[0]["submissionId"].startswith(first), deps[0]["submissionId"]
assert os.path.exists(os.path.join(S, "STAGED.sha256"))
tl = re.search(r'"time_log2": *([0-9.]+)', open(os.path.join(S, "candidates/blake3/claim.json")).read()).group(1)
LANE = "mooselumph/hashsmash-pareto/blake3"
out = os.path.join(WS, "research/launch/submit_pareto_%s.sh" % slot)
txt = f'''#!/usr/bin/env bash
# Staged 10-15 in slot {slot} (pareto/blake3 r3, Lemma 2 v2 rebuild of 62cfd777 (B3R3PV, filed 10-14, 124.8123)): time_log2 {tl}. DO NOT RUN without the owner's go.
# THE SUBMIT of {label}: the same program, circuit and ledger as the filed entry; Section 4 (Lemma 2) replaced by Lemma 2 v2 (no premise besides H1, H2 withdrawn, CMAX = 2 handled exactly,
# Chernoff tail certified in exact arithmetic), Section 9 answers the findings of the rulings on 1cd0dd3b (and 41b32afc, same Lemma 2) by id.
# First dependency {first} (the filed entry; see dependencies.json for the full credited list).
# Refuses if anything changed since staging (STAGED.sha256, dependencies.json) and if any dependency is not found in the pareto/blake3 lane (deps guard, lane named explicitly). Appends one line to research/FILINGS.md.
set -uo pipefail
DST="$HOME/hashsmash/yukon/{slot}/pareto"; NOTE=submission-note.md
LOG='{WS}/research/FILINGS.md'
export PATH="$HOME/.local/bin:$HOME/.bun/bin:$PATH" NO_COLOR=1
cd "$DST" || exit 1
(cd candidates/blake3 && find . -type f -print0 | sort -z | xargs -0 sha256sum; sha256sum "../../$NOTE" | sed 's# \\.\\./\\.\\./# #') | diff -q - STAGED.sha256 >/dev/null || {{ echo "STOP: staged files changed"; exit 1; }}
echo "{sha}  dependencies.json" | sha256sum -c - >/dev/null || {{ echo "STOP: dependencies.json changed"; exit 1; }}
# deps guard: every dependency ({first} first) must be visible in the lane's submissions list before we file (lane named explicitly: a lane-less call reads the base slot's lane)
yukon submissions --all --json {LANE} > /tmp/subs_{slot}.json 2>/dev/null || {{ echo "STOP: cannot list submissions"; exit 1; }}
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
echo "| $(date '+%Y-%m-%d %H:%M') | {label} | ${{SUB:-none}} | $TL (Lemma 2 v2; filed 124.8123 (62cfd777)) | validating |" >> "$LOG"
date '+%Y-%m-%d %H:%M:%S %z'
'''
open(out, "w", newline="\n").write(txt)
print("wrote", out, "deps sha", sha[:12], "time_log2", tl)
