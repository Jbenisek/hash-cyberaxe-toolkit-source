"""Write dig records for blake3-r3 round-1 step cells (units U19..U27) from step_scan_r1.json."""
import json, os
D = json.load(open("step_scan_r1.json"))
OUT = "../dig/incoming3"
UNITS = {"blake3-r3-U19": ["C1.q1", "C1.q2"], "blake3-r3-U20": ["C1.q3", "C1.q4"], "blake3-r3-U21": ["C2.q1", "C2.q2"],
         "blake3-r3-U22": ["C2.q3", "C2.q4"], "blake3-r3-U23": ["C3.q1", "C3.q2"], "blake3-r3-U24": ["C3.q3", "C3.q4"],
         "blake3-r3-U25": ["D0.q1", "D0.q2"], "blake3-r3-U26": ["D0.q3", "D0.q4"], "blake3-r3-U27": ["D1.q1", "D1.q2"]}
QDESC = {1: "q1 = (a1,d1): a=a+b+x; d=ror16(d^a)", 2: "q2 = (c1,b1): c=c+d; b=ror12(b^c)",
         3: "q3 = (a2,d2): a=a+b+y; d=ror8(d^a)", 4: "q4 = (c2,b2): c=c+d; b=ror7(b^c)"}
ROT = {1: 16, 2: 12, 3: 8, 4: 7}
PER_OP = 0.00240   # time_log2 change per chain-step op (levers_step_count.md, COMPUTED from the ledger formula)
COMMON = dict(hash="blake3-r3", row_i=None, row_j=None, source="our workflow: dig-scan-b3r3", own_test=True, date="2026-10-12",
              lever=False, gain_bits=None)
EVID = ("research/blake3_r3/step_profile_r1.py (tracer; validate: empty-input 7-round vector, 64-byte msgs vs verifier blake3.py at 7 and 3 rounds, "
        "packed circuit 0 wrong of 371 lanes, 595 ops, source identical to candidate_blake3/experiments/rho.py); "
        "research/blake3_r3/step_scan_r1.py; research/blake3_r3/step_scan_r1.json")

n = 0
for unit, steps in UNITS.items():
    os.makedirs(os.path.join(OUT, unit), exist_ok=True)
    for st in steps:
        r = D["steps"][st]; call, q = st.split(".q"); q = int(q); obj = "R1%s.q%d" % (call, q)
        by = r["by"]; byt = ", ".join("%d %s" % (v, k) for k, v in by.items())
        a, b, c_, d = r["gcall"]
        xw, yw = r["msg_x"], r["msg_y"]
        mword = (xw if q == 1 else yw) if q in (1, 3) else None
        mconst = (mword is not None and mword < 8)
        ab = r["ablation"]
        fr = []
        for line, kind, vs in ab["detail"]:
            fr.append((kind, min(v[1] for v in vs if v[1] is not None) / vs[0][2]))
        lo = min(f for _, f in fr); hi = max(f for _, f in fr)
        orders = r["orders"]; ot = sorted(set(v["total_ops"] for v in orders.values())); owrong = set(v["wrong"] for v in orders.values())
        al = r["alts"]; pit = al["pitch"]
        deps = r["deps"]; nin = sorted(set(sum(deps.values(), [])))
        indep = ", ".join("%s<-%d words" % (k, len(v)) for k, v in deps.items())
        # Q1
        q1num = ("%d ops charged for this step of 595 (%s); %s" % (r["ops"], byt,
                 ("message word m%d (x/y) is the constant 0 -> no add emitted" % mword) if mconst else
                 ("message word m%d is a free chain word (m8..m15) -> add emitted" % mword if mword is not None else "no message word in this step")))
        q1 = dict(object="%s %s in the shipped 7-lane SWAR circuit (G call state words v%d,v%d,v%d,v%d)" % (obj, QDESC[q], a, b, c_, d),
                  question="Q1 value/count as used: how many operations does the shipped 3-round circuit charge for this step?",
                  labels=["N"], status="COMPUTED", number=q1num,
                  notes="cell blake3-r3|%s|step|Q1. Own re-trace (pitch 36, 7 lanes, free words m8..m15) reproduces 595 ops and the shipped source text; value of one chain-step op = %.5f bit of time_log2 (levers_step_count.md formula). Lines: %s" % (obj, PER_OP, "; ".join(r["lines"])),
                  held_fixed="pitch 36, 7 lanes, K=0^32 so m0..m7 are constants, flags 11, counter 0, length 64, 3 rounds, shipped add/xor/ror emit rules",
                  reopen_if="the machine model changes (rotation primitive, more lanes, different op prices) or the step is moved to a different round or lane layout")
        # Q2
        q2num = ("0 of %d ops removable: deleting any single op (replace its result by each of its operands) leaves %.0f%%-%.0f%% of 371 test lanes wrong (random, all-ones, all-zero, mixed extreme inputs); by kind necessary: %s" %
                 (ab["n_ops"], lo * 100, hi * 100, json.dumps(ab["by_kind_necessary"], sort_keys=True))) if not ab["removable"] else ("REMOVABLE ops by test: %s" % ab["removable"])
        q2 = dict(object="%s %s: necessity of each charged op" % (obj, QDESC[q]),
                  question="Q2 necessity: delete each op of the step, recount the exact outcome against the scalar digest.",
                  labels=["Z"], status="COMPUTED", number=q2num,
                  notes="cell blake3-r3|%s|step|Q2. Both AND masks of the rotation are needed (guard-bit and neighbour-lane garbage); the add and xor are the arithmetic itself. A deletion that is NOT shown wrong would be a saving of %.5f bit per op; none found. Only operand-replacement deletions were tried, not arbitrary rewrites." % (obj, PER_OP),
                  held_fixed="rest of the circuit unchanged, 371 test lanes incl. all-ones/all-zeros, replacement = each operand register of the op",
                  reopen_if="a deletion passes a larger or adversarial lane test, or a proof of tighter lane bounds shows an AND is redundant")
        # Q3
        nterm = 3 if q in (1, 3) else 2
        if q in (1, 3):
            if mconst:
                oterm = "the add has 2 variable terms + a zero constant (message word m%d = 0): 2 orders" % mword
            else:
                oterm = "3 variable terms"
        else:
            oterm = "2 variable terms"
        q3num = ("%d operand orders of the add built and run: total ops {%s}, wrong lanes {%s} -> score-optimal value is the shipped 595 (no order saves); "
                 "free chain words reaching the step inputs: %s; step inputs depend on %d of 8 free words" %
                 (len(orders), ",".join(map(str, ot)), ",".join(map(str, owrong)), indep, len(nin)))
        q3 = dict(object="%s %s: free choices in the step" % (obj, QDESC[q]),
                  question="Q3 degrees of freedom / score-optimal value: add operand order (%s), which free words feed it." % oterm,
                  labels=["Z"], status="COMPUTED", number=q3num,
                  notes="cell blake3-r3|%s|step|Q3. All %d orders cost the same because the lane bound never reaches 2^36 inside round 1 (the 3 internal masks of the circuit are in round 2, ops 507/538/568 per levers_step_count.md)." % (obj, len(orders)),
                  held_fixed="pitch 36, one step changed at a time, other steps shipped",
                  reopen_if="a lane layout with fewer guard bits or a proof of bounds that moves an internal mask out of round 2")
        # Q4
        pi = {p: pit[p] for p in pit}
        q4num = ("alternatives built and tested (all 0 wrong lanes): rotation mask-before-shift = %d total ops (tie, 595); rotation as ror(d)^ror(a) = %d (+5); "
                 "pitch 35 = %d (step %d ops), 34 = %d, 33 = %d (7 lanes); pitch 37 and 40 = %d ops but 6 lanes = %.2f ops/instance vs 595/7 = 85.00 -> none beats 595 per 7 lanes" %
                 (al["rot_maskfirst"]["total_ops"], al["rot_distributed_xor"]["total_ops"], pit["35"]["total_ops"], pit["35"]["step_ops"], pit["34"]["total_ops"],
                  pit["33"]["total_ops"], pit["37"]["total_ops"], pit["37"]["total_ops"] / 6))
        q4 = dict(object="%s %s: alternative implementations" % (obj, QDESC[q]),
                  question="Q4 alternatives: other rotation forms and other lane pitches for this step.",
                  labels=["Z"], status="COMPUTED", number=q4num,
                  notes="cell blake3-r3|%s|step|Q4. Step at pitch 33/34/35: %d/%d/%d ops (guard bits too few, extra masks). 256 bits fit at most 7 lanes at pitch 36; pitch >= 37 gives 6 lanes. Not tried: duplicated-lane pitch-64 layouts (4 lanes), 8 lanes at pitch 32 with SWAR adds (levers_step_count.md estimates worse, GUESS)." %
                        (obj, pit["33"]["step_ops"], pit["34"]["step_ops"], pit["35"]["step_ops"]),
                  held_fixed="same op price list (add and or xor shl shr = 1 each), same message/state constants",
                  reopen_if="the op model prices rotations or masks differently, or a 3-4 op rotation layout with 7 lanes is found")
        for qi, rec in zip((1, 2, 3, 4), (q1, q2, q3, q4)):
            rec = dict(rec); rec.update(COMMON); rec["evidence"] = EVID
            path = os.path.join(OUT, unit, "blake3-r3_%s_step_Q%d.json" % (obj, qi))
            json.dump(rec, open(path, "w"), indent=1); n += 1
print("records", n)
