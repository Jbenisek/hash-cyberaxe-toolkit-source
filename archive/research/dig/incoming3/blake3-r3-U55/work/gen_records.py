"""Write the cell records for units blake3-r3-U55..U63 (one JSON per cell) from the result files of our own tests.  Own code."""
import json, os, re, math, sys
HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, *[".."] * 5))
INC = os.path.join(WS, "research", "dig", "incoming3")
U61 = os.path.join(INC, "blake3-r3-U61", "work")
U55 = os.path.join(INC, "blake3-r3-U55", "work")
UNITS = ["blake3-r3-U%d" % i for i in range(55, 64)]

units = {}
for line in open(os.path.join(WS, "research", "dig", "UNITS.jsonl"), encoding="utf-8"):
    u = json.loads(line)
    if u["id"] in UNITS:
        units[u["id"]] = u
univ = {}
for line in open(os.path.join(WS, "research", "dig", "UNIVERSE.jsonl"), encoding="utf-8"):
    if '"blake3-r3"' in line:
        u = json.loads(line)
        univ[u["id"]] = u

reads = json.load(open(os.path.join(U55, "msg_reads.json")))
words = json.load(open(os.path.join(U55, "words.json")))
init_ops = json.load(open(os.path.join(U61, "init_ops.json")))
lev = json.load(open(os.path.join(U61, "lever_demo.json")))

def parse_kv(path, key):
    out = []
    for ln in open(path):
        if ln.startswith(key):
            ln = ln.replace("ratio_to_2^e*sqrt(pi 2^32/2)", "ratio")
            out.append(dict(re.findall(r"(\S+?)=(\S+)", ln)))
    return out

pin = parse_kv(os.path.join(U55, "pin_all.txt"), "pin analogue")
tag = parse_kv(os.path.join(U61, "tag_all.txt"), "tag n=")
RATIO = "ratio"

SRC = "our workflow: dig-scan-b3r3"
DATE = "2026-10-12"
LOOP_SHARE, L = 0.9944, 595 + 4 + 3 / 16
S7 = " (7 lanes x 36-bit pitch, filed Tracer rules, 595 ops per batch of 7)"

def tgain(ops):
    return math.log2(1 - LOOP_SHARE * (595 - ops) / L)

def put(unit, cid, **kw):
    u = univ[cid]
    rec = dict(hash="blake3-r3", row_i=None, row_j=None, object=kw.pop("object", u["label"]), question=kw.pop("question"),
               labels=kw.pop("labels"), status=kw.pop("status"), number=kw.pop("number"), source=SRC, own_test=True,
               evidence=kw.pop("evidence"), date=DATE, lever=kw.pop("lever", False), gain_bits=kw.pop("gain_bits", None),
               notes=kw.pop("notes", ""), held_fixed=kw.pop("held_fixed"), reopen_if=kw.pop("reopen_if"), topic=cid)
    if "gain_basis" in kw:
        rec["gain_basis"] = kw.pop("gain_basis")
    assert not kw, kw
    rec["notes"] = ("universe cell %s. " % cid) + rec["notes"]
    d = os.path.join(INC, unit)
    os.makedirs(d, exist_ok=True)
    fn = cid.replace("|", "_") + ".json"
    json.dump(rec, open(os.path.join(d, fn), "w", encoding="utf-8"), indent=1)
    return rec

P = "research/dig/incoming3/"
LIB = P + "blake3-r3-U55/work/b3r3lib.py"
VAL = "validation: b3r3lib.py selftest (7-round official vectors for empty input and [0]; organizer verifier/blake3.py at 3 and 7 rounds on 600 random 0^32||x; trace total 595 and per-kind counts = filed rho.py PH/PH_BY)"
HF_MSG = "target 0^32||x (m0..m7 = 0, m8..m15 chain words, identity embedding), standard IV/counter 0/length 64/flags 11, 3 rounds, filed circuit rules" + S7 + "; all other reads unchanged"

count = {}

# ------------------------------------------------------------------ MSG cells (U57-U60)
for uid in ("blake3-r3-U57", "blake3-r3-U58", "blake3-r3-U59", "blake3-r3-U60"):
    for cid in units[uid]["cells"]:
        key = cid.split("|")[1][4:]            # R0C0.x
        v = reads[key]
        w = v["word"]
        hit = [i for i, c in enumerate(v["digest_words_hit"]) if c]
        if not v["var"]:
            role = "m%d is a zero key word of the target prefix 0^32 (constant 0)" % w
            eff = ("the read adds the constant 0, which the filed Tracer skips (marginal ops of the read 0: replacing it by constant 0 leaves the total at 595)")
            if v["call_ops"] == 0:
                eff += "; this is a round-0 column call whose state and both message words are constants, so the whole call is folded at build time (0 ops)"
            labels = ["0"]
        else:
            role = "m%d is a chain word (digest word %d fed back by the identity embedding), variable in every lane" % (w, w - 8)
            eff = "marginal ops of the read = %d (circuit total %d with the read replaced by constant 0, filed 595)" % (-v["drop_delta"], v["drop_total"])
            if v["round"] == 0:
                eff += "; in round 0 the call's state is still constant, so the first variable read turns a folded call into a live one" if v["pos"] == "x" else ""
            labels = ["X"]
        num = ("Read %s: %s. Value as used: word index m%d (index checked by running the scalar compression with marker words 100..115 and recording the schedule: m%d at round %d, call %s, position %s). "
               "%s. Statement ops (the a+b%s%s add statement) %d; ops of the whole call %d of 595. "
               "Own sampled check, one xor-perturbation of only this read on %d random chain inputs: on average %.2f of 8 digest words and %.1f of 256 digest bits change (minimum %d words); digest words that changed in every trial: %s."
               % (key, role, w, w, v["round"], v["call"], v["pos"], eff[0].upper() + eff[1:], "" if v["pos"] == "x" else " (second add)", "", v["read_ops"], v["call_ops"],
                  v["trials"], v["mean_words_changed"], v["mean_bits_changed"], v["min_words_changed"],
                  ",".join(map(str, [i for i, c in enumerate(v["digest_words_hit"]) if c == v["trials"]])) or "none"))
        rec = put(units[uid]["id"], cid, question="Q1 value/count as used at this read", labels=labels, status="COMPUTED", number=num,
                  evidence=P + "blake3-r3-U55/work/msg_reads.py; " + P + "blake3-r3-U55/work/msg_reads.json; " + LIB,
                  notes="exact trace counts (COMPUTED); the perturbation counts are sampled (400 trials, fixed seed). " + VAL,
                  held_fixed=HF_MSG, reopen_if=("the machine rule charged an add of constant 0 (then the zero-key reads would cost), or the evaluation order of the add chain (a+b)+x changed so that the read could be folded into a constant earlier"
                                                 if not v["var"] else "a lane layout or add order in which this read could be combined with a constant before the variable state words (a cheaper position for the chain word), or a different embedding of the digest into m8..m15"))
        count[uid] = count.get(uid, 0) + 1

# ------------------------------------------------------------------ chain word cells (U55, U56)
def getpin(p, e, mode):
    for d in pin:
        if int(d["p"]) == p and int(d["e"]) == e and int(d["mode"]) == mode:
            return d
    return None

for uid, ws in (("blake3-r3-U55", (12, 13)), ("blake3-r3-U56", (14, 15))):
    for w in ws:
        p = w - 8
        info = words["m%d" % w]
        rs = [(k, reads[k]) for k in info["reads"]]
        rtxt = "; ".join("%s (%s)" % (k, "marginal %d ops" % -r["drop_delta"]) for k, r in rs)
        bias = words["digest_bit_bias"]["w%d" % p]
        cid = "blake3-r3|m%d|msgword|Q1" % w
        put(uid, cid, question="Q1 value/count as used", labels=["X"], status="COMPUTED",
            number=("m%d is chain word %d: digest word %d fed back unchanged (identity embedding into m8..m15); free, 32 bits, variable in every lane. Used 3 times: %s; marginal ops sum %d of 595 "
                    "(each read counted with the other reads kept; a read that starts a round-0 call costs more because it unfolds a constant call). Digest word %d as the source of m%d: bit bias over 200000 random chain inputs, 32 bits, max |z| = %.2f (limit for 32 tests about 3.3)."
                    % (w, w - 8, p, rtxt, sum(-r["drop_delta"] for k, r in rs), p, w, bias["max_abs_z"])),
            evidence=P + "blake3-r3-U55/work/msg_reads.json; " + P + "blake3-r3-U55/work/words.py; " + P + "blake3-r3-U55/work/words.json; " + LIB,
            notes="exact trace counts; bit bias sampled (fixed seed). " + VAL, held_fixed=HF_MSG,
            reopen_if="a reading of the machine rule or a lane layout that charges these three reads differently, or a measured bias of digest word %d on the full 256-bit chain (T2 of the filed entry covered 42 projections)" % p)
        cid = "blake3-r3|m%d|msgword|Q2" % w
        pc, pz = info["pin_const_ops"], info["pin_zero_ops"]
        b0r = getpin(4, 0, 0); b0i = getpin(4, 0, 1)
        def rr(pp, e, mode, base):
            d = getpin(pp, e, mode)
            return float(d["mean_evals"]) / (2 ** e * float(base["mean_evals"])), float(d["se"]) * (float(d["mean_evals"]) / (2 ** e * float(base["mean_evals"]))) / max(float(d["ratio"]), 1e-9)
        w4 = ", ".join("word %d %.2f+-%.2f" % (pp, rr(pp, 4, 0, b0r)[0], rr(pp, 4, 0, b0r)[1]) for pp in (4, 5, 6, 7))
        i4, i4s = rr(4, 4, 1, b0i); n8, n8s = rr(4, 8, 0, b0r); i8, i8s = rr(4, 8, 1, b0i)
        mine = rr(p, 4, 0, b0r)
        put(uid, cid, question="Q2 necessity: pin the word (stop feeding digest word %d back), recount the outcome" % p, labels=["K"], status="SAMPLED",
            number=("Pinning m%d to a constant cuts the circuit from 595 to %d ops (nonzero constant) or %d ops (zero): at best %.4f bits of time (filed loop share 99.44 percent, 599.19 ops per batch with filter and loop control). "
                    "But the fed-back state then has 224 bits against a 256-bit tag; a rho collision of the 224-bit state is a full digest collision with probability 2^-32, so the cost is multiplied by 2^((256-224)/2) = 2^16 (random-function law). "
                    "Own test of the law on the real 3-round function, small analogue (state = 32 bits in m8, m9..m15 pinned, a fresh pinned constant drawn for every trajectory, tag = 32 state bits + e low bits of digest word p, the word that would feed m12..m15; cost = mean evaluations until two different inputs share the tag): "
                    "cost(e) / (2^e * cost(0)), cost(0) = %.0f evaluations (1000 runs, ratio %.3f to the random-mapping value sqrt(pi 2^32/2)): at e=4, 100 runs each, %s (this word %d: %.2f+-%.2f); ideal-function control at e=4 %.2f+-%.2f; at e=8 (12 runs, word 4) real %.2f+-%.2f, control %.2f+-%.2f. "
                    "So the cost grows as 2^e with the dropped bits (all within -26 to +17 percent; word 6 at 0.73 is about 3.9 sigma low in this 100-run sample: a possible small correlation between the low bits of digest word 6 and state collisions, not followed up; it would be a gain only if it survived at 256 bits, which this analogue cannot say). "
                    "Net effect of pinning at width 256: +16 bits of time against -%.4f: closed (K)."
                    % (w, pc, pz, -tgain(pz), float(b0r["mean_evals"]), float(b0r["ratio"]), w4, p, mine[0], mine[1], i4, i4s, n8, n8s, i8, i8s, -tgain(pz))),
            evidence=P + "blake3-r3-U55/work/pintest.c; " + P + "blake3-r3-U55/work/pin_run.sh; " + P + "blake3-r3-U55/work/pin_all.txt; " + P + "blake3-r3-U55/work/words.json",
            notes="the 2^16 factor at width 256 is the random-function formula checked at e=4 and e=8 (not run at 256). Method note: a first version restarted on ONE fixed function and found the same failing state-collision pair again and again (122 to 1753 trajectories per success at e=4 instead of 16; e=0 cost 0.70 of the random-mapping value for that fixed function), the known single-functional-graph effect (the filed note's earlier 0.70-1.65 ratios); the numbers above are from the corrected version (fresh pinned constant per trajectory). " + VAL,
            held_fixed="3-round digest of 0^32||x with m9..m15 pinned to fixed constants (m9 re-drawn per trajectory); tag width 32+e; plain table, no distinguished points; identity feed of digest word 0 into m8; other state constants standard",
            reopen_if="a way to recover the 32 lost tag bits without 2^32 state collisions (a structure tying digest word %d to the fed-back words, e.g. the word-6 deviation confirmed at larger samples), or a cost model that charges the 16 saved ops more than 16 bits" % p)
        cid = "blake3-r3|m%d|msgword|Q3" % w
        put(uid, cid, question="Q3 degrees of freedom (exact count) and score-optimal value", labels=["N"], status="COMPUTED",
            number=("32 bits: m%d is a free chain word, all 2^32 values occur as digest word %d (identity embedding of a 256-bit chain, 8 words = 256 bits of freedom in total; counted by construction, bias sample in Q1 shows no gap). "
                    "Score-optimal value: none, the word is a lane variable so the circuit has 595 ops for every value (a constant would be 576..595 ops but costs 2^16 in time, Q2). "
                    "Freedom beyond the 8 chain words is not needed: widening to all 16 words variable gives %d ops (+%d, +%.3f bits)." % (w, p, words["all16_ops"], words["all16_ops"] - 595, math.log2(words["all16_ops"] / 595))),
            evidence=P + "blake3-r3-U55/work/words.py; " + P + "blake3-r3-U55/work/words.json; " + LIB, notes=VAL,
            held_fixed=HF_MSG, reopen_if="a cheaper way to use extra freedom (m0..m7) than +135 ops, e.g. a chain that makes the 8 round-0 column calls cheaper rather than costlier")
        cid = "blake3-r3|m%d|msgword|Q4" % w
        ff = words["fewer_free_ops"]
        put(uid, cid, question="Q4 alternatives: other embeddings, other free sets", labels=["Z"], status="COMPUTED",
            number=("Embedding alternatives: all 8! = 40320 assignments of digest words to m8..m15 give 595 ops in 40320 of 40320 (exact trace; every chain word is a lane variable of bound 2^32-1, so an assignment only renames input registers). "
                    "Free-set alternatives (ops, fed-back width): m8..m15 595 (256 bits), m8..m14 %d (224), m8..m13 %d (192), m8..m11 %d (128), m8..m9 %d (64); each missing word costs 2^16 in time (Q2), all 16 words free %d ops. "
                    "No alternative is cheaper in score." % (ff["free_m8..m14"], ff["free_m8..m13"], ff["free_m8..m11"], ff["free_m8..m9"], words["all16_ops"])),
            evidence=P + "blake3-r3-U55/work/words.py; " + P + "blake3-r3-U55/work/words.json; " + LIB, notes=VAL,
            held_fixed=HF_MSG + "; the search is the plain birthday chain of the filed entry", reopen_if="an embedding that is not a renaming and removes work (for example a digest word that already equals a message-read sum), or a non-injective embedding with a counted collision-rate gain")
        count[uid] = count.get(uid, 0) + 4

# ------------------------------------------------------------------ INIT cells (U61-U63)
STD = [0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19]
STDV = STD + STD[:4]
base = [d for d in tag if int(d["idx"]) == -1][0]
for uid in ("blake3-r3-U61", "blake3-r3-U62", "blake3-r3-U63"):
    for cid in units[uid]["cells"]:
        i = int(cid.split("|")[1][6:])
        q = cid.split("|")[3]
        kind = "h" if i < 8 else "IV"
        sc = lev["scan"][str(i)]
        io = init_ops[str(i)]
        td = [d for d in tag if int(d["idx"]) == i][0]
        std = STDV[i]
        nsol = {int(s): v["count"] for s, v in sc["sites"].items()}
        hist = {int(k): v for k, v in sc["hist"].items()}
        nz = sum(v for k, v in hist.items() if k >= 1)
        two = [k for k in hist if k >= 2]
        names = {int(r["site"]): r["name"] for r in lev["demo"][str(i)]}
        solutions = "; ".join("%s: %d value%s (first 0x%08x)" % (names[s], c, "" if c == 1 else "s", lev["scan"][str(i)]["sites"][str(s)]["first"][0]) for s, c in sorted(nsol.items()))
        HF = ("all other initial-state words standard (h = IV, v8..v11 = IV[0..3], counter 0, length 64, flags 11), m0..m7 = 0, 3 rounds, filed circuit rules (595 ops), chain m8..m15 free; word v%d varied alone" % i)
        EV = P + "blake3-r3-U61/work/site_scan.c; " + P + "blake3-r3-U61/work/scan_all.txt; " + P + "blake3-r3-U61/work/lever_demo.py; " + P + "blake3-r3-U61/work/lever_demo.json; " + P + "blake3-r3-U55/work/b3r3lib.py"
        if q == "Q2":
            num = ("Not necessary for the attack, necessary for the target. Replacing v%d = 0x%08x by the random constant 0x%08x: (a) circuit: %d random replacement values give %d..%d ops (595 for all; an op is saved only if a derived constant hits 0, probability about 2^-32 per site); "
                   "(b) tag collision test on the real 3-round chain, n=32, 1000 runs: mean/pred = %.3f +- %.3f (standard state %.3f +- %.3f), random-mapping law kept; "
                   "(c) the %s colliding pairs found under the modified state also collide in the 32-bit tag under the standard state in %s of %s cases (expected 2^-32 each). "
                   "So the cost of the search does not depend on the value, but the pair only collides for the specified function: the target fixes v%d = 0x%08x%s."
                   % (i, std, int(td["val"], 16), io["n"], io["min"], io["max"], float(td["ratio"]), float(td["se"]), float(base["ratio"]), float(base["se"]), td["pairs"], td["also_collide_under_standard_state"], td["pairs"], i, std,
                      " (h of the first block of a chunk)" if i < 8 else " (IV[%d], a constant of every compression, also in keyed mode)" % (i - 8)))
            put(uid, cid, question="Q2 necessity: replace the value, recount the exact outcome", labels=["N"], status="SAMPLED", number=num,
                evidence=P + "blake3-r3-U61/work/tagtest.c; " + P + "blake3-r3-U61/work/tag_run.sh; " + P + "blake3-r3-U61/work/tag_all.txt; " + P + "blake3-r3-U61/work/init_ops.py; " + P + "blake3-r3-U61/work/init_ops.json; " + P + "blake3-r3-U55/work/b3r3lib.py",
                notes="n=32 tag from digest word %d (and %d); 3 rounds; fixed seed; pair check uses the standard-state function on the same two inputs. " % (int(td["word"]), (int(td["word"]) + 1) & 7) + VAL,
                held_fixed=HF, reopen_if="a pair that collides under both the standard and a modified state more often than 2^-32, or a value of v%d that changes the 595-op count by a non-zero-hit mechanism" % i)
        elif q == "Q3":
            b = sc["best_n"]
            dem = [r for r in lev["demo"][str(i)] if len(r["zero_sites"]) == b]
            rows = lev["demo"][str(i)]
            bo = min([r["ops"] for r in rows] or [595])
            best_txt = ("best value 0x%08x (%s) has %d zero site%s and %d circuit ops with it plugged into the Tracer (exact trace)" % (sc["best_v"], [r["name"] for r in rows if r["value"] == sc["best_v"]][0] if [r for r in rows if r["value"] == sc["best_v"]] else "n/a", b, "" if b == 1 else "s", min([r["ops"] for r in rows if r["value"] == sc["best_v"]] or [595]))) if b > 0 else "no value gives a zero site"
            if rows:
                best_txt += "; the value with the fewest ops over all listed solutions is %d ops" % bo
            num = ("0 bits at the target: v%d = 0x%08x is fixed by the specification%s (1 admissible value of 2^32). Score-optimal value, exhaustive over all 2^32 values of v%d with the rest standard: "
                   "the circuit skips an operation exactly when a post-column constant p (round-0 column calls read the zero key words, so they fold) is 0 at one of 16 sites (4 per diagonal call); v%d (column %d) reaches 5 of them. "
                   "Zero-site histogram over 2^32 values %s; per site: %s. %s. A zero site saves 1 op (add and xor sites, and the D0 sum) or 2 ops (the x-add sums of D1, D2, D3: the smaller lane bound also drops a later mask), i.e. %.4f or %.4f bits of time (filed loop share 99.44 percent), checked on every listed solution with the Tracer. "
                   "The standard value has no zero site (595 ops)."
                   % (i, std, " (h = IV for the first block of a chunk)" if i < 8 else " (IV[%d], a constant of every compression)" % (i - 8), i, i, sc["col"], json.dumps({str(k): v for k, v in sorted(hist.items()) if k > 0} | {"0": hist.get(0)}), solutions or "none", best_txt, -tgain(594), -tgain(593)))
            put(uid, cid, question="Q3 degrees of freedom and score-optimal value", labels=["0"], status="COMPUTED", number=num, evidence=EV,
                notes="exhaustive scan of 2^32 values (one core, nice 10, about 41 s); the formulas for the 16 sites were checked against the Tracer log on 200 states (site_check.py); every listed solution was plugged into the Tracer and gave 593 or 594 ops. " + VAL,
                held_fixed=HF + "; flags 11 (single-block message)", reopen_if=("a target that lets the chaining value be chosen (multi-block chunk, Q4) - then these values are reachable at a price of 2^32 first-block compressions per zero site" if i < 8 else "never for a standard BLAKE3 target: IV[%d] is a constant of every compression" % (i - 8)))
        else:
            g = lev["gain"]; cb = lev["combos"]
            if i < 8:
                is_rep = (i == 0)
                num = ("Alternative to h[%d] = IV[%d]: the first block of a longer chunk, h = chaining value of an earlier block (colliding messages P||0^32||x and P||0^32||y share the first block P: 128 bytes, last-block flags CHUNK_END|ROOT = 10, counter 0, length 64; same circuit, v15 = 10 instead of 11). "
                       "A random CV leaves the circuit at 595 ops (Q2). A CV for which a post-column constant is 0 saves 1 or 2 ops per zero site (Q3); each zero site is a 32-bit event of a random CV, so it costs about 2^32 first-block compressions (3 rounds, 1 unit each) and k sites about 2^(32k), found by random trying (upper bound: any of the 16 sites would do). "
                       "Exact Tracer counts for real per-word solutions of the scans combined in different columns (all other words standard): at most 1 site %d ops, 2 sites %d ops, 3 sites %d ops (a 4th site is not available in different columns in the found pool). "
                       "Gain on the filed 125.1087 (main loop 99.44 percent of the total, 599.19 ops per batch with filter and loop control): 1 site %.5f, 2 sites %.5f, 3 sites %.5f bits; pre-search 2^32 / 2^64 / 2^96 units = +%.1e bits at 3 sites (2^96 against 2^125.11); 4 sites would need 2^128 units (net %+.2f bits). v%d takes part in %d of the 16 sites (%s)."
                       % (i, i, cb["1"]["ops"], cb["2"]["ops"], cb["3"]["ops"], g["1"]["delta_time_log2"], g["2"]["delta_time_log2"], g["3"]["delta_time_log2"], g["3"]["pre_search_relative_bits"], g["4"]["net"], i, len(nsol), ", ".join(names[s] for s in sorted(nsol)) or "no solution in 2^32 values (so v%d alone zeroes no site; a pair of words in the same column could)" % i))
                lever = bool(is_rep)
                extra = {"gain_basis": "T"} if lever else {}
                put(uid, cid, question="Q4 alternatives to the value (multi-block chunk CV)", labels=["N", "E"] if lever else ["N"], status="COMPUTED", number=num, evidence=EV + "; " + P + "blake3-r3-U61/work/lever_demo_out.txt",
                    lever=lever, gain_bits=(-g["3"]["delta_time_log2"] if lever else None), **extra,
                    notes=(("same lever as the one recorded on INIT.v0 Q4 (about one zero site per 2^32 first-block tries, up to 3 sites); this cell holds the per-word solution counts. ") if not lever else
                           ("LEVER CANDIDATE, small: -%.4f bits of time (shown as positive gain_bits) with 3 zero sites (590 ops instead of 595), -%.4f with 2. It needs a 128-byte message with a prefix block P whose CV hits the zero sites (2^96 first-block compressions, 2^-29 of the total) and a judge that accepts a two-block message for the blake3-r3 target. "
                            "The ops are exact for the Tracer with real per-word solutions plugged in; the 2^96 search was NOT run and no CV was built; the v15 = 10 state was not scanned (solutions per site are Poisson with mean 1 in either case). Door 37 priced a fresh CV at 0.007-0.1 bit (earlier outside figure, not re-derived here)." % (-g["3"]["delta_time_log2"], -g["2"]["delta_time_log2"]))) + " " + VAL,
                    held_fixed=HF + "; v15 = 11 in the scan",
                    reopen_if="a cheaper way to produce a CV with a given post-column constant at 0 than 2^32 tries per site (a structured first block), more sites at once from words of one column, or a ruling that accepts the two-block message")
            else:
                num = ("No alternative: v%d = IV[%d] is the constant of every BLAKE3 compression (chunk, parent, keyed or not); the specification has no input that changes it. "
                       "For the record, the exhaustive scan shows what a free choice would be worth: %s (a zero site saves 1 or 2 ops of 595, %.4f or %.4f bits). Not selectable, so no lever."
                       % (i, i - 8, ("zero sites reachable: " + solutions) if solutions else "no value of v%d zeroes any site" % i, -tgain(594), -tgain(593)))
                put(uid, cid, question="Q4 alternatives to the value", labels=["Z"], status="COMPUTED", number=num, evidence=EV,
                    notes="the scan treats v%d as if it were free, only to size the loss from the fixed constant. " % i + VAL,
                    held_fixed=HF, reopen_if="a different BLAKE3 variant or target profile that lets IV[%d] vary" % (i - 8))
        count[uid] = count.get(uid, 0) + 1
print(count, sum(count.values()))
