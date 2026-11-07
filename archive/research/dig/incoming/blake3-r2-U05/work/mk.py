
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

import json, sys
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/dig'))
import add_cell
EV = "research/dig/incoming/blake3-r2-U05/work/u05.py; research/dig/incoming/blake3-r2-U05/work/u05_stdout.txt; research/dig/incoming/blake3-r2-U05/work/u05_out.json"
quarters = {1: ("a1,d1", "(a,b,d,mx)->(a1,d1)", "Y2,Y13 (a,d inputs) and m9 (mx)"),
            2: ("c1,b1", "(c,d1,b)->(c1,b1)", "Y8 (c), Y2/Y7 via b,d1 chain"),
            3: ("a2,d2", "(a1,b1,d1,my)->(a2,d2)", "intermediates a1,b1,d1 and m14 (my)"),
            4: ("c2,b2", "(c1,d2,b1)->(c2,b2)", "intermediates c1,d2,b1")}
q2hit = {1: "6320/150000 only when the message word mx (m9) is among the injected inputs (the a-diff cancelled by an m9 diff, an in-call absorption); 0/150000 for state words only",
         2: "0/150000 (no message word enters q2)",
         3: "6232/150000 only when the message word my (m14) is among the injected inputs (a1 diff cancelled by an m14 diff); 0/150000 for state words only",
         4: "0/150000 (no message word enters q4)"}
recs = []
for k in (1, 2, 3, 4):
    qn, fm, src = quarters[k]
    cid = "blake3-r2|E2.q%d|step|Q2" % k
    recs.append((cid, {
        "hash": "blake3-r2", "row_i": None, "row_j": None,
        "object": "E2.q%d (%s) zero difference, relaxed with E0 left zero" % (k, qn),
        "question": "Necessity: if the zero difference of E2 quarter-step q%d is relaxed (nonzero input difference injected), does the digest event (words 0,2,5,7 equal across the pair) survive? [universe cell %s]" % (k, cid),
        "labels": ["0"], "status": "COMPUTED",
        "number": "event mass with E0 zero and equal m9,m14 after relaxing E2.q%d = 0 exactly (G is a bijection, outputs equal forces inputs equal); measured %s" % (k, q2hit[k]),
        "source": "our workflow: scan-once", "own_test": True, "evidence": EV,
        "date": "2026-10-12", "lever": False, "gain_bits": None,
        "notes": "Universe cell %s. Validated first: our 2-round compress equals verifier/blake3.py on 2000/2000 inputs; G inverse round trip 100000/100000; Fact P reproduced from the pkgCK constants (C3 b,d equal, a,c = 8127c181/7edf3e7e and 7af77f38/850000c3); Lemma L round 0 identical 2000/2000; round-1 baseline with pins gives digest equal on exactly words 0,2,5,7 in 20000/20000. Quarter-step map %s. Toy width 3 and 4 exhaustive: G is a bijection on all states. Sources of a difference at this step: %s; every legal message-word source also activates all of C0-C3 and E0-E3 (see Q4 record), so the relaxation is not free-standing. Outcome: zero difference here is necessary while E0 stays zero; the only relaxation is the crossed one with E0 (Q4). No gain." % (cid, fm, src)}))
q4txt = {1: "q1 outputs (a1,d1) are intermediate; they reach the digest only through q3/q4",
         2: "q2 outputs (c1,b1) are intermediate; they reach the digest only through q3/q4",
         3: "q3 outputs (a2,d2) are digest inputs: Z2 (pairs with E0.c2 in word 2) and Z13 (pairs with E0.b2 in word 5)",
         4: "q4 outputs (c2,b2) are digest inputs: Z8 (pairs with E0.a2 in word 0) and Z7 (pairs with E0.d2 in word 7)"}
for k in (1, 2, 3, 4):
    qn, fm, src = quarters[k]
    cid = "blake3-r2|E2.q%d|step|Q4" % k
    recs.append((cid, {
        "hash": "blake3-r2", "row_i": None, "row_j": None,
        "object": "E2.q%d (%s) alternative difference patterns reaching digest words 0,2,5,7 equal" % (k, qn),
        "question": "Alternative nonzero difference patterns at E2 quarter-step q%d that still give digest words 0,2,5,7 equal, and whether a legal source can feed them. [universe cell %s]" % (k, cid),
        "labels": ["0", "Z"], "status": "LOCAL_ONLY",
        "number": "alternatives exist only crossed with E0: 2^384 input-pair configurations of (E0,E2) have the event (exact by bijection), verified by inversion 20000/20000; generic cost 4 x 32 = 128 bits (per-bit agreement 15.99 of 32); E0 zero + E2 nonzero = 0; clean-state in-call absorption 0/500000 (+0/500000 structured); all 16 legal message-word sources activate E0 and E2 in 600/600 trials with 0 of 8 digest words equal (baseline 4 of 8)",
        "source": "our workflow: scan-once", "own_test": True, "evidence": EV,
        "date": "2026-10-12", "lever": False, "gain_bits": None,
        "notes": "Universe cell %s. %s. Positive control: pick E2 output pair and an E0 output pair whose XOR differences are the crossed copy (E2.a~E0.c, E2.b~E0.d, E2.c~E0.a, E2.d~E0.b), invert both calls: digest words 0,2,5,7 equal with both calls active. Absorption supports at one G call (outputs equal, messages differ): a-diff by dmx; d-diff by (dmx,-dmx); a+d by dmy or both (K2 pattern); never from an equal-input clean state. Sources: with the Lemma L baseline and pin emulation (Y7,Y15 of the second run set equal after C3) an extra legal difference at any message word 0..15 (w15 low 24 bits, 63-byte side) activates C0-C3 or enough of the chain that E0 and E2 are active in every trial (600 each), digest words 0,2,5,7 then differ: matches door 22 residual claim (256 bits generic) as our own measurement; the unpinned Lemma L baseline also has E0,E2 active (only the C3 pin makes them zero). LOCAL_ONLY: the legal-source part is a 600-trial simulation with pin emulation, not a pinned full-path construction (round-0 inversion to hit X3,X7,X11,X15 not built); not a proof that no cancelling chain exists through round 0. Window: this record covers E2 inputs from the two-round compression of 55/63-byte pairs. No gain." % (cid, q4txt[k])}))
import os
for cid, r in recs:
    fn = os.path.join(_hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming/blake3-r2-U05'), cid.replace('|', '_') + '.json')
    json.dump(r, open(fn, 'w'), indent=1)
    err = add_cell.validate(json.load(open(fn)), add_cell.load())
    print(os.path.basename(fn), err)
