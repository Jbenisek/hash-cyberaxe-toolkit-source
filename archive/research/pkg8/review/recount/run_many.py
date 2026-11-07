"""Many clusters through MY tracer: counts constant, lanes right, lane-sum bounds never broken.

    python -B run_many.py [clusters] [seed]
"""
import sys, os, json, random

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "program"))
import halfsearch_cluster as H
import mytrace as T

N = int(sys.argv[1]) if len(sys.argv) > 1 else 40
SEED = sys.argv[2] if len(sys.argv) > 2 else "recount"
LANES = H.LANES
BOUND = dict((n, b) for n, _o, _l, _s, b in H.TABLES["batch"])

rng = random.Random(SEED)
xmask = sum(1 << b for b in H.X_FLIP_BITS)
counts, maxlane, lanes_ok, lanes_bad, words, broken = {}, {}, 0, 0, 0, []
mixed_words = mixed_lanes = 0
x2dep = ("X2+w7", "-w2", "w0", "w12-S1-S6", "w3", "S5", "S12")
x2dep_reads = None

for _ in range(N):
    free6 = [rng.randrange(1 << 32) for _ in range(6)]
    x2_rep = rng.randrange(1 << 32) & ~xmask
    k_rep = rng.randrange(H.CLASS_SIZE)
    for b in H.E_FLIP_K:
        k_rep &= ~(1 << b)
    ref = H.cluster_reference(free6, x2_rep, k_rep)
    o = H.outer(list(free6))
    reps, kk = [], k_rep
    while len(reps) < LANES:
        if H.is_representative(kk):
            reps.append(H.class_member(kk))
        kk = (kk + 1) % H.CLASS_SIZE
    jobs = [([x2_rep] * LANES, reps, None)]
    for lane_t in H.PARTNER_WORDS:
        jobs.append(([ref[t]["x2"] for t in lane_t], [ref[t]["y4"] for t in lane_t], lane_t))
    for lane_x2, lane_y4, lane_t in jobs:
        c, row, vword = H.partner_word_memory(free6, x2_rep, lane_x2, lane_y4)
        tr, pa, p2, wl, fl, tk, fla, tka = T.my_batch(c, row, vword, 0)
        key = (tr.total(pa), tr.total(p2), tr.registers())
        counts[key] = counts.get(key, 0) + 1
        words += 1
        if len(set(lane_x2)) > 1:
            mixed_words += 1
            mixed_lanes += LANES
        if x2dep_reads is None:
            x2dep_reads = dict((n, sum(1 for v in tr.vals if v.tag == "ld:" + n)) for n in x2dep)
        for p, m in tr.maxlane.items():
            maxlane[p] = max(maxlane.get(p, 0), m)
            if BOUND[p] is not None and m >= BOUND[p] * 2 ** 32:
                broken.append((p, m / 2.0 ** 32, BOUND[p]))
        for i in range(LANES):
            exp = H.reference(H.middle(o, lane_x2[i]), lane_y4[i])
            good = (wl[i] == exp["word"] and fl[i] == int(exp["word"] != 0)
                    and exp["word"] == exp["word_from_digests"])
            if lane_t is not None:
                good = good and ((fla[i] == 0) == ref[lane_t[i]]["k8"])
            lanes_ok, lanes_bad = lanes_ok + int(good), lanes_bad + int(not good)

print(json.dumps({
    "clusters": N, "seed": SEED, "words through my tracer": words,
    "words with two X2 values": mixed_words, "lanes in those words": mixed_lanes,
    "distinct (stage A, stage 2, registers) triples": dict((str(k), v) for k, v in counts.items()),
    "lanes right": lanes_ok, "lanes wrong": lanes_bad,
    "lane-sum bound broken": broken,
    "largest lane seen per part (units of 2^32) vs declared bound":
        dict((p, [round(m / 2.0 ** 32, 4), BOUND[p]]) for p, m in maxlane.items()),
    "reads per word of each X2-dependent memory word": x2dep_reads,
}, indent=1))
