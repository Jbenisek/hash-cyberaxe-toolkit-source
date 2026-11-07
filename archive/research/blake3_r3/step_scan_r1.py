"""Scan round-1 steps (C1,C2,C3,D0,D1 x q1..q4) of the shipped 3-round SWAR circuit. Output: step_scan_r1.json"""
import json, itertools, re, sys
from step_profile_r1 import *

RD = 1
base_tr, base_out = build()
BASE = base_tr.ops
base_fn, _ = compile_circuit(base_tr, base_out)
SETS = test_inputs(base_tr)
assert check(base_tr, base_fn, SETS)[0] == 0
GCALL_J = {"C1": 1, "C2": 2, "C3": 3, "D0": 4, "D1": 5}
# message index of round-1 words
mi = list(range(16))
for _ in range(RD): mi = [mi[i] for i in PERM]

def step_lines(tr, tag):
    return [i for i, (t, k) in enumerate(tr.tags) if t == tag]

def ablate(tr, out, idxs):
    res = []
    for i in idxs:
        ln = tr.lines[i]; name, expr = ln.split("=", 1)
        kind = tr.tags[i][1]
        regs = re.findall(r"\b[ti]\d+\b", expr)
        cands = []
        for r_ in dict.fromkeys(regs): cands.append(r_)
        outcome = []
        for rep in cands:
            lines = list(tr.lines); lines[i] = "%s=%s" % (name, rep)
            fn, _ = compile_circuit(tr, out, lines)
            c = check(tr, fn, SETS)
            outcome.append({"replace_with": rep, "wrong_lanes": None if c is None else c[0], "of": None if c is None else c[1]})
        res.append({"line": ln, "kind": kind, "variants": outcome,
                    "removable_by_test": any(o["wrong_lanes"] == 0 for o in outcome)})
    return res

def variant_total(**kw):
    tr, out = build(**kw); fn, _ = compile_circuit(tr, out); c = check(tr, fn, SETS)
    return tr.ops, c

def deps_before():
    # free-word dependence sets of each state word before each step (round RD), via set propagation
    st = [set() for _ in range(16)]
    mm = [set() for _ in range(8)] + [{i} for i in range(8, 16)]
    res = {}
    for rd in range(RD + 1):
        for j, (a, b, c, d) in enumerate(GCALLS):
            x, y = mm[2*j], mm[2*j+1]
            for q in (1, 2, 3, 4):
                if rd == RD: res[(j, q)] = {"a": sorted(st[a]), "b": sorted(st[b]), "c": sorted(st[c]), "d": sorted(st[d])}
                if q == 1: st[a] = st[a] | st[b] | x; st[d] = st[d] | st[a]
                if q == 2: st[c] = st[c] | st[d]; st[b] = st[b] | st[c]
                if q == 3: st[a] = st[a] | st[b] | y; st[d] = st[d] | st[a]
                if q == 4: st[c] = st[c] | st[d]; st[b] = st[b] | st[c]
        mm = [mm[i] for i in PERM]
    return res
DEPS = deps_before()
out = {"baseline_ops": BASE, "steps": {}}
for cn, j in GCALL_J.items():
    ga, gb, gc, gd = GCALLS[j]
    x, y = mi[2*j], mi[2*j+1]
    for q in (1, 2, 3, 4):
        tag = (RD, j, q); idxs = step_lines(base_tr, tag)
        by = {}
        for i in idxs: by[base_tr.tags[i][1]] = by.get(base_tr.tags[i][1], 0) + 1
        rec = {"deps": DEPS[(j, q)], "call": cn, "q": q, "gcall": [ga, gb, gc, gd], "msg_x": x, "msg_y": y, "ops": len(idxs), "by": by, "lines": [base_tr.lines[i] for i in idxs]}
        # Q2 ablation
        ab = ablate(base_tr, base_out, idxs)
        rec["ablation"] = {"n_ops": len(ab), "removable": [r["line"] for r in ab if r["removable_by_test"]],
                           "necessary": sum(1 for r in ab if not r["removable_by_test"]),
                           "by_kind_necessary": {}, "detail": [(r["line"], r["kind"], [(v["replace_with"], v["wrong_lanes"], v["of"]) for v in r["variants"]]) for r in ab]}
        for r in ab:
            if not r["removable_by_test"]: rec["ablation"]["by_kind_necessary"][r["kind"]] = rec["ablation"]["by_kind_necessary"].get(r["kind"], 0) + 1
        # Q3 operand orders for the add of this step
        nterm = 3 if q in (1, 3) else 2
        orders = {}
        for perm in itertools.permutations(range(nterm)):
            ops, c = variant_total(order={tag: perm})
            orders[str(perm)] = {"total_ops": ops, "wrong": None if c is None else c[0]}
        rec["orders"] = orders
        # Q4 alternatives
        alts = {}
        ops, c = variant_total(rotmode={tag: "maskfirst"}); alts["rot_maskfirst"] = {"total_ops": ops, "wrong": c[0]}
        ops, c = variant_total(dist={tag}); alts["rot_distributed_xor"] = {"total_ops": ops, "wrong": None if c is None else c[0]}
        pit = {}
        for p in (33, 34, 35, 36, 37, 40):
            tr, o = build(pitch=p); fn, _ = compile_circuit(tr, o); cc = check(tr, fn, test_inputs(tr, 150))
            pit[p] = {"lanes": tr.lanes, "total_ops": tr.ops, "step_ops": len(step_lines(tr, tag)), "ops_per_instance": round(tr.ops / tr.lanes, 3), "wrong": None if cc is None else cc[0]}
        alts["pitch"] = pit
        rec["alts"] = alts
        out["steps"]["%s.q%d" % (cn, q)] = rec
json.dump(out, open("step_scan_r1.json", "w"), indent=1)
print("done", BASE)
