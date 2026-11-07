#!/usr/bin/env python3
"""Reviewer, lens mathematics and cost: the self-test figures quoted in proof.md 6.5 against the evidence files."""
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
EV = Path(__file__).resolve().parent.parent / "evidence"
tot = {"lanes_checked": 0, "lanes_right": 0, "lanes_passing_rule_a": 0, "batches_entering_stage_2": 0, "zero_test_words": 0, "cases": 0}
big, regs, shapes = 0, set(), set()
for name in ("selftest_1200000_61.json", "selftest_1200000_62.json"):
    text = (EV / name).read_text(encoding="ascii", errors="replace")
    d = json.loads(next(l for l in text.splitlines() if l.startswith("{")))
    extra = [l[:80] for l in text.splitlines() if l.strip() and not l.startswith("{")]
    if extra:
        print("   other lines in", name, extra[:2])
    for k in tot:
        tot[k] += d[k]
    big = max(big, d["largest_lane"])
    regs.add(d["registers"])
    shapes.add((d["stage_a"]["operations"], d["stage_a"]["loads"], d["stage_2"]["operations"], d["stage_2"]["loads"],
                d["same_counts_in_every_case"], d["counts_equal_table"], d["sums_below_bounds"], d["seed"]))
print("long self-tests:", tot, "largest lane %.3f" % (big / 2 ** 32), "registers", sorted(regs))
print("  ", sorted(shapes))
p = EV / "followup" / "batch4_two_class_filed_1200000_s51.json"
d = json.loads(next(l for l in p.read_text(encoding="ascii", errors="replace").splitlines() if l.startswith("{")))
keys = [k for k in d if not isinstance(d[k], (dict, list))]
print("follow-up batch file keys:", ", ".join(keys)[:330])
print("  ", {k: d[k] for k in keys if any(s in k for s in ("lane", "pass", "enter", "stage", "cases", "batch", "ops", "load"))})
for k in d:
    if isinstance(d[k], dict):
        print("  ", k, json.dumps(d[k])[:300])
