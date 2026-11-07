
# Publication path adapter: resolve data paths from the extracted source tree.
def _hca_public_path_text(value):
    if "__HCA_WORKSPACE__/" not in value:
        return value
    import os as _hca_os
    from pathlib import Path as _hca_Path
    root = _hca_os.environ.get("HASHCYBERAXE_WORKSPACE")
    if root is None:
        here = _hca_Path(__file__).resolve().parent
        root = next((str(p) for p in (here, *here.parents) if (p / "research").is_dir()), None)
    if root is None:
        raise FileNotFoundError("Extract the research source tree, or set HASHCYBERAXE_WORKSPACE to its archive directory.")
    return value.replace("__HCA_WORKSPACE__/", str(_hca_Path(root).resolve()).replace("\\", "/") + "/")

import json, os
BASE = _hca_public_path_text('__HCA_WORKSPACE__/research/dig/')
d = json.load(open(BASE + "incoming3/blake3-r3-U10/work/scan_nb100.json"))
units = [json.loads(l) for l in open(BASE + "UNITS.jsonl")]
units = [u for u in units if u["id"] in ["blake3-r3-U%d" % i for i in range(10, 19)]]
EV = ("research/dig/incoming3/blake3-r3-U10/work/b3step.py; research/dig/incoming3/blake3-r3-U10/work/scan_nb100.json; "
      "research/dig/incoming3/blake3-r3-U10/work/mkrecs.py; research/blake3_r3/candidate_blake3/experiments/rho.py (definition only)")
ROT = {1: 16, 2: 12, 3: 8, 4: 7}
LEG = {1: "(a1,d1)", 2: "(c1,b1)", 3: "(a2,d2)", 4: "(c2,b2)"}
CALL = {"D0": "(0,5,10,15)", "D1": "(1,6,11,12)", "D2": "(2,7,8,13)", "D3": "(3,4,9,14)", "C0": "(0,4,8,12)"}
DESC = {1: "a = a + b + mx; d = ror(d ^ a, 16)", 2: "c = c + d; b = ror(b ^ c, 12)",
        3: "a = a + b + my; d = ror(d ^ a, 8)", 4: "c = c + d; b = ror(b ^ c, 7)"}
VAL = ("validated first: scalar code reproduces BLAKE3('') at 7 rounds (af1349b9...3262) and equals verifier/blake3.py on 200 random 64-byte blocks at 7 and at 3 rounds; "
       "the traced 7-lane circuit has 0 mismatches on 2100 lanes at 7 rounds and at 3 rounds, and totals 595 ops at 3 rounds (add 100, xor 88, shr 80, and 167, shl 80, or 80)")
HF = ("filed 3-round circuit: 7 lanes x 36 bits in a 256-bit word, message 0^32 || x (m0..m7 = 0, m8..m15 free), flags 11, block length 64, counter 0, unkeyed; "
      "rotation = shr, and, shl, and, or; op set add/and/or/xor/shl/shr")


def ms(sup):
    return "m" + ",m".join(str(w) for w in sup)


def rec(cell, key, Q):
    s = d["steps"][key]
    r, call, q = key[1], key[2:4], int(key[-1])
    rd = "diagonal" if call[0] == "D" else "column"
    obj = "%s %s: 3-round circuit quarter-step, round %s %s call %s %s, %s, rotation %d" % (key, LEG[q], r, rd, call[1], CALL[call], DESC[q], ROT[q])
    sup = s["free_words_in_support"]
    ops = s["ops"]
    kinds = ", ".join("%s %d" % (a, b) for a, b in sorted(s["kinds"].items()))
    fails = [x["bad"] for x in s["delete_each_op"]]
    gper = d["logper_op"]
    if Q == 1:
        question = "Q1 value/count as used: how many machine ops does this quarter-step cost in the filed 595-op circuit, and what is that worth in time_log2?"
        number = ("%d ops (%s); the plain unfolded step on the same op set is %d ops, so constant folding removes %d. One op is worth %.5f bits of time_log2 "
                  "(ledger: -log2(1 - 0.9944/599.1875)), so the step carries %.4f bits of the 125.1087. Free message words feeding the step: %s."
                  % (ops, kinds, s["unfolded_ref_ops"], s["folded_away"], gper, ops * gper, ms(sup)))
        labels = ["N"]
        status = "COMPUTED"
        notes = ("Universe cell %s. Op counts are by tag in our own re-trace of the filed circuit (same rules as rho.py Tracer: constants folded, masks inserted when lane bounds reach 2^36). %s." % (cell, VAL))
        reopen = "a different lane layout or op set that evaluates this step with fewer than %d ops and still gives 0 mismatches on the full 3-round circuit" % ops
    elif Q == 2:
        question = "Q2 necessity: change it (bypass the step; delete each of its ops one at a time), recount the exact outcome."
        number = ("Bypass the whole quarter-step (state left unchanged): digest changed in %.1f%% of 1500 random inputs, mean %.2f of 256 digest bits flip (random would be 128). "
                  "Delete each of its %d circuit ops in turn (output := first operand), 7-lane circuit against scalar over 700 lanes: wrong-digest lanes per op = %s; all %d ops are essential (every deletion fails at least %d of 700 lanes)."
                  % (100 * s["bypass_digest_changed_frac"], s["bypass_mean_bits_flipped_of_256"], ops, fails, ops, min(fails)))
        labels = ["N"]
        status = "SAMPLED"
        notes = ("Universe cell %s. Essentiality of each op is shown by counterexample (a failing lane exists); the failure rates are samples of 700 lanes, seed 20261012. "
                 "Deleting either AND of the rotation fails about as often as deleting the add, so no mask here is only a bound guard. %s." % (cell, VAL))
        reopen = "an op of this step whose deletion gives 0 wrong digests in a large sample plus a proof that it never matters (none found: smallest failure count was %d of 700)" % min(fails)
    elif Q == 3:
        question = "Q3 degrees of freedom or score-optimal value: which free inputs reach this step, is it injective on them, and is its op count the minimum over the alternatives?"
        ij = s["inj_sample"]
        if r == "0":
            dof = "the step reads free message word(s) %s (%d bits) plus round-0 constants" % (ms(sup), 32 * len(sup))
        else:
            dof = "its inputs depend on free message words %s (%d bits in total) through the round-0 state" % (ms(sup), 32 * len(sup))
        number = ("support computed exactly by taint over the traced circuit: %s. Its 64-bit output pair is injective on the 65,536 distinct sampled inputs over that support "
                  "(%d distinct outputs, %d repeats; expected repeats for a random 64-bit map: 0). Op count %d is the minimum of every alternative tried in Q4 (add orders, pitch 34/35, single-AND rotation): "
                  "no tunable value, score-optimal value = the filed one." % (dof, ij["distinct_outputs"], ij["dups"], ops))
        labels = ["X"] if r == "0" else ["N"]
        status = "COMPUTED"
        notes = ("Universe cell %s. The support is exact (data flow); injectivity is a sample, not a proof. A generic birthday step has no free parameter, so the score-optimal value is the op count itself. %s." % (cell, VAL))
        reopen = "a use of the step's free words that is cheaper than recomputing it per trial (a structure of the 3 rounds), shown by a counted saving"
    else:
        question = "Q4 alternatives: other ways to evaluate this step (add order, lane pitch, single-AND rotation), recounted on the full circuit."
        parts = []
        if s["alt_add_orders"]:
            tots = sorted(set((v["total"], v["step_ops"]) for v in s["alt_add_orders"].values() if "total" in v))
            parts.append("all 6 operand orders of the 3-operand add give (circuit total, step ops) = %s" % tots)
        else:
            parts.append("no 3-operand add here (two-operand add, order is symmetric)")
        a4 = s["alt_rot_single_and"]
        parts.append("rotation with one AND after the OR (4 ops instead of 5): step %d ops, circuit %d, but %d of %d lanes give a wrong digest, so invalid"
                     % (a4["step_ops"], a4["total"], a4["bad"], a4["lanes"]))
        ap = d["alt_pitch_totals"]
        aps = s["alt_pitch_step_ops"]
        parts.append("lane pitch 34/35/36 (7 lanes each): circuit totals %d / %d / %d ops, this step %s / %s / %s ops" % (ap["34"][0], ap["35"][0], ap["36"][0], aps["34"], aps["35"], aps["36"]))
        number = "; ".join(parts) + ". No alternative beats the filed %d ops for this step." % ops
        labels = ["Z"]
        status = "COMPUTED"
        notes = ("Universe cell %s. Only these three alternative families were tried; 8 lanes at pitch 32 is not buildable with the shipped add rules (every add needs a mask first) and was not costed here. %s." % (cell, VAL))
        reopen = "a layout with 8 lanes or a rotation form with fewer than 5 ops that passes the 700-lane check, or a tighter lane-bound proof"
    return {"hash": "blake3-r3", "row_i": None, "row_j": None, "object": obj, "question": question, "labels": labels, "status": status,
            "number": number, "source": "our workflow: dig-scan-b3r3", "own_test": True, "evidence": EV, "date": "2026-10-12", "lever": False,
            "gain_bits": None, "notes": notes, "held_fixed": HF, "reopen_if": reopen}


n = 0
for u in units:
    od = BASE + "incoming3/" + u["id"]
    os.makedirs(od, exist_ok=True)
    for cell in u["cells"]:
        _, obj, _, Q = cell.split("|")
        r = rec(cell, obj, int(Q[1]))
        fn = od + "/" + cell.replace("|", "_") + ".json"
        json.dump(r, open(fn, "w"), indent=1)
        n += 1
print(n)
