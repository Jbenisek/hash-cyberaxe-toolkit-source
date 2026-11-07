#!/usr/bin/env python3
"""Hostile-judge lens: wall time of the two declared experiments for 256 seeds of my own (not the organizer's), one
process each, against the organizer's default 20-second limit; and in-sample / out-of-sample figures for rule A.
Read-only for the package. Output: review/judge_time.out"""
import hashlib
import json
import re
import subprocess
import sys
import time
from fractions import Fraction
from pathlib import Path

sys.dont_write_bytecode = True
PKG = Path(__file__).resolve().parent.parent
PROG = PKG / "blake3-r2" / "experiments" / "halfsearch.py"
out = []
manifest = json.loads((PKG / "blake3-r2" / "experiments" / "manifest.json").read_text())
for exp in manifest["experiments"]:
    for label in ("judge-a", "judge-b"):
        req = {"schema_version": 1, "experiment_id": exp["id"], "target_profile": "blake3-r2-prefix-v1", "event": exp["event"],
               "max_message_bytes": 4096,
               "trials": [{"trial": i, "seed": hashlib.sha256(("%s %s %d" % (label, exp["id"], i)).encode()).hexdigest()}
                          for i in range(256)]}
        t = time.time()
        r = subprocess.run([sys.executable, "-B", "-s", str(PROG)], input=json.dumps(req), capture_output=True, text=True)
        dt = time.time() - t
        rows = json.loads(r.stdout)["trials"] if r.returncode == 0 else []
        obs = [x.get("observations", {}) for x in rows]
        tries = [o.get("tries", 0) for o in obs]
        out.append("%s seeds %s: exit %d, %.1f s, pairs %d of %d, stdout %d bytes, tries mean %.1f max %d, stage 2 entered %d, "
                   "lanes right %s, counts %s" % (
                       exp["id"], label, r.returncode, dt, sum(x["message_a_hex"] is not None for x in rows), len(rows), len(r.stdout),
                       sum(tries) / max(1, len(tries)), max(tries or [0]), sum(o.get("batch_stage_2_entered", 0) for o in obs),
                       sorted({o.get("batch_lanes_right") for o in obs}, key=str),
                       sorted({(o.get("batch_stage_a_operations"), o.get("batch_stage_a_loads"), o.get("batch_stage_2_operations"),
                                o.get("batch_stage_2_loads")) for o in obs}, key=str)))
out.append("python " + sys.version.split()[0])

# rule A: the outcomes the rule was read from (betas of the 1,500 list, k <= 13) against the betas added later (k = 14)
EV = PKG / "evidence"
k_of = {}
for line in (EV / "pinB_e7c1815f.total").read_text().split("\n"):
    f = line.split()
    if len(f) >= 2:
        k_of[f[0]] = int(f[1])
outx = {}
for line in (EV / "pairs_recount_e7c1815f.txt").read_text().split("\n"):
    f = line.split()
    if f and f[0] == "OUTX":
        outx[(f[2], f[3], f[4])] = Fraction(int(f[6]) * int(f[8]), 2 ** 80)
sat = {}
for line in (EV / "rule_a_sat_e7c1815f.txt").read_text().split("\n"):
    f = line.split()
    if f and f[0] == "VIOLATE":
        sat[(f[1], f[2], f[3])] = f[4]
short = set()
m = re.search(r"BETAS_BY_MASS (\S+)", (EV / "followup" / "pinB3_rules.txt").read_text())
short = set(m.group(1).split(","))
for name, keys in (("betas the rule was read from (%d)" % len(short), [k for k in outx if k[0] in short]),
                   ("betas added later", [k for k in outx if k[0] not in short])):
    tot = sum(outx[k] for k in keys)
    drop = [k for k in keys if sat[k] == "SAT"]
    out.append("%s: betas %d, k %s, outcomes %d, with a violating solution %d, count %.1f, of it in outcomes with a violating "
               "solution %.1f (%.4f%%)" % (name, len({k[0] for k in keys}), sorted({k_of[k[0]] for k in keys}), len(keys), len(drop),
                                         float(tot), float(sum(outx[k] for k in drop)), 100 * float(sum(outx[k] for k in drop) / tot)))
(PKG / "review" / "judge_time.out").write_text("\n".join(out) + "\n", encoding="ascii")
print(len(out), "lines written")
