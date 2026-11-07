"""RECOUNT driver: my own counts of every piece, beside the package's. Research only.

    python -B run_recount.py
"""
import sys, os, json, random

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "program"))
import halfsearch_cluster as H
import mytrace as T

LANES = H.LANES
PKG = {"stage A": 47, "stage 2": 135, "gate core": 9, "dispatch": 29, "delta kernel": 5,
       "broadcast": 7, "mixed-middle cache": 258, "table build": 74, "middle step": 134,
       "outer step": 260}
# the bounds TABLES declares for the largest lane of any sum in each part, in units of 2^32
BOUND = dict((name, b) for name, _o, _l, _s, b in H.TABLES["batch"])
BOUND_T = dict((name, b) for name, _o, _l, _s, b in H.TABLES["table build"])
BOUND_M = dict((name, b) for name, _o, _l, _s, b in H.TABLES["middle step"])

rng = random.Random("recount")
out = {}

# ------------------------------------------------------------------ a cluster, its words and values
free6 = [rng.randrange(1 << 32) for _ in range(6)]
xmask = sum(1 << b for b in H.X_FLIP_BITS)
x2_rep = rng.randrange(1 << 32) & ~xmask
k_rep = rng.randrange(H.CLASS_SIZE)
for b in H.E_FLIP_K:
    k_rep &= ~(1 << b)
ref = H.cluster_reference(free6, x2_rep, k_rep)
o = H.outer(list(free6))

# a representative word: seven representative members, all at the representative X2
reps, kk = [], k_rep
while len(reps) < LANES:
    if H.is_representative(kk):
        reps.append(H.class_member(kk))
    kk = (kk + 1) % H.CLASS_SIZE
words = [("representative", [x2_rep] * LANES, reps, None)]
for wi, lane_t in enumerate(H.PARTNER_WORDS):
    words.append(("neighbour word %d" % wi, [ref[t]["x2"] for t in lane_t],
                  [ref[t]["y4"] for t in lane_t], lane_t))

rows = []
for name, lane_x2, lane_y4, lane_t in words:
    c, row, vword = H.partner_word_memory(free6, x2_rep, lane_x2, lane_y4)
    tr, pa, p2, wlanes, flags, taken, flags_a, taken_a = T.my_batch(c, row, vword, 0)
    sa, s2 = tr.total(pa), tr.total(p2)
    # values: every lane against the program's independent reference on that lane's own X2 and member
    ok = bad = 0
    for i in range(LANES):
        v_lane = H.middle(o, lane_x2[i])
        exp = H.reference(v_lane, lane_y4[i])
        good = (wlanes[i] == exp["word"] and flags[i] == int(exp["word"] != 0)
                and exp["word"] == exp["word_from_digests"])
        if lane_t is not None:                     # stage-A flag against the scalar rule for a neighbour
            good = good and ((flags_a[i] == 0) == ref[lane_t[i]]["k8"])
        ok, bad = ok + int(good), bad + int(not good)
    overflow = [(p, m / 2.0 ** 32, BOUND[p]) for p, m in tr.maxlane.items()
                if BOUND[p] is not None and m >= BOUND[p] * 2 ** 32]
    rows.append({"piece": name, "distinct X2 in lanes": len(set(lane_x2)),
                 "stage A": sa, "stage 2": s2, "registers": tr.registers(),
                 "lanes right": ok, "lanes wrong": bad,
                 "rotation mask loads": tr.rot_mask_loads,
                 "lane-sum bound broken": overflow,
                 "max lane (units of 2^32)": dict((p, round(m / 2.0 ** 32, 4)) for p, m in tr.maxlane.items())})
out["batch words"] = rows

# ------------------------------------------------------------------ the other pieces
gc = dict((n, H.rep(v)) for n, v in H.FIXED.items())
gc["not bit 32"] = H.ONES * (H.LANE ^ 1 << 32)
gc["gate V"], gc["gate all"], gc["gate carry"] = H.rep(H.GATE_V), H.rep(H.GATE_ALL), H.rep((-H.GATE_ALL) & H.MASK)
tr, gf = T.my_gate(gc, H.rep(ref[0]["z"]))
out["gate core"] = {"mine": tr.total(), "pkg": PKG["gate core"], "registers": tr.registers(),
                    "parts": tr.breakdown(),
                    "gate flags = gate_pass_z": [bool(x) for x in gf] == [H.gate_pass_z(ref[0]["z"])] * 7}

dc = dict(gc); dc["zero"] = 0
for i in range(LANES):
    dc["lane %d" % i] = 1 << (H.LANE_BITS * i + 32)
gword = sum((1 if gf[i] else 0) << (H.LANE_BITS * i + 32) for i in range(LANES))
tr, sel = T.my_dispatch(dc, gword)
out["dispatch (7-lane selector)"] = {"mine": tr.total(), "pkg": PKG["dispatch"], "parts": tr.breakdown()}

kc = dict((n, H.rep(v)) for n, v in H.FIXED.items())
kc["U word"] = H.pack(H.rol(H.class_member(k_rep), 7) for _ in range(LANES))
kc["D word"] = 0
kc["scalar"] = H.rol(H.class_member(k_rep), 7)
out["Y4-delta kernel"] = {"mine": T.my_delta(kc).total(), "pkg": PKG["delta kernel"]}
out["lane broadcast"] = {"mine": T.my_broadcast(kc).total(), "pkg": PKG["broadcast"]}
cc = dict(("L%d" % p, 0) for p in range(6)); cc["fieldA"] = cc["fieldB"] = 0
trc = T.my_cache(cc)
out["mixed-middle cache per group"] = {"mine": trc.total(), "pkg": PKG["mixed-middle cache"],
                                       "parts": trc.breakdown()}

# member table and middle step, on a real memory
c0 = H.memory(list(free6) + [free6[5]])
m0 = H.Machine(); H.outer_step(m0, c0)         # VALUES only: fill memory (their counter, not mine, ignored)
trt = T.my_table_build(c0, H.list_words(0)[0], 0)
out["table build (per list word)"] = {"mine": trt.total(), "pkg": PKG["table build"],
                                      "parts": trt.breakdown(),
                                      "max lane": dict((p, round(m / 2.0 ** 32, 4)) for p, m in trt.maxlane.items())}
c1 = H.memory(list(free6) + [free6[5]])
m1 = H.Machine(); H.outer_step(m1, c1)
trm = T.my_middle_step(c1)
out["middle step (per X2 value)"] = {"mine": trm.total(), "pkg": PKG["middle step"],
                                     "parts": trm.breakdown()}

# ------------------------------------------------------------------ the split of stage 2
c, row, vword = H.partner_word_memory(free6, x2_rep, [x2_rep] * LANES, reps)
tr, pa, p2, *_ = T.my_batch(c, row, vword, 0)
per_part = dict((p, tr.total([p])) for p in p2)
PREFIX_IN_E1 = 2 + 6 + 1 + 1 + 4      # a1 (2 ops,1 load) d1 (xor+rot=6,1 load) c1 (1,1) c1b (1,1)
split_prefix = sum(per_part[p] for p in p2 if p not in ("E1, A and B", "E1 test", "restore")) + PREFIX_IN_E1
split_tail = (per_part["E1, A and B"] - PREFIX_IN_E1) + per_part["E1 test"] + per_part["restore"]
p_lane = 105.0 / 16384.0
p_word = 1.0 - (1.0 - p_lane) ** 7
out["stage 2 split"] = {"per part": per_part, "stage 2 total": sum(per_part.values()),
                        "prefix": split_prefix, "tail (no restore extra)": split_tail,
                        "test (RESULTS.md, not recounted here)": 12,
                        "tail + 3 restore-live": split_tail + 3,
                        "P(lane passes cheap test)": p_lane,
                        "P(word of 7 lanes passes)": p_word,
                        "per entered word, test 12, tail+3": split_prefix + 12 + (split_tail + 3) * p_word}

print(json.dumps(out, indent=1, default=str))
