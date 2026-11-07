"""Ones'-complement lens on the front-line residual: train/test analysis.

Parts: TRAIN = data/rand rows [0, 2^19); TEST = rand rows [2^19, 2^20); CTX = data/ctx (2^18, context-structured);
STREAM = 2^28 fresh front-line pairs (oc_stream real, seed 0x4F4E4553434F4D50, never used for choosing hypotheses);
CTRLPY = 2^19 uniform final-state words (numpy) - calibration of the test machinery.
REFERENCE for every test = CONTROL STREAM: 2^28 pairs whose 16 final-state words of A and of B are uniform random
(oc_stream ctrl, seed 0x4F4E45534354524C), pushed through the same code path. A two-sample test against it asks
"does the real residual differ from what uniform digest words would give in this coordinate system?".
Hypotheses are chosen ONLY on TRAIN (Bonferroni over the family) and then re-tested on TEST, CTX and STREAM.
The surrogate S (residual from another row) is reported next to each flagged effect: if S shows the same effect,
the structure is the XOR residual's own distribution seen through the ones'-complement map, not new structure.
Writes analyze_out.txt, counts_*.npz, flagged.json.
"""
import sys
sys.dont_write_bytecode = True
import json, math, os, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import oclib as L

DATA = os.path.join(os.path.dirname(HERE), "data")
OUTF = open(os.path.join(HERE, "analyze_out.txt"), "w")
WN = (1, 3, 4, 6)


def say(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    OUTF.write(s + "\n")
    OUTF.flush()


def load(setn):
    dig = np.fromfile(os.path.join(DATA, setn, "dig.u32"), "<u4").reshape(-1, 8)
    eo = np.fromfile(os.path.join(DATA, setn, "eout.u32"), "<u4").reshape(-1, 16)
    em = np.fromfile(os.path.join(DATA, setn, "emid.u32"), "<u4").reshape(-1, 16)
    res = np.fromfile(os.path.join(DATA, setn, "res.u32"), "<u4").reshape(-1, 4)
    dA, dB = dig[:, 0:4], dig[:, 4:8]
    # word order (1,3,4,6): E1 part a2,c2,d2,b2 (cols 0,2,3,1 / B +4); E3 part g2,e2,f2,h2 (cols 10,8,9,11 / B +4)
    xA, xB = eo[:, [0, 2, 3, 1]], eo[:, [4, 6, 7, 5]]
    yA, yB = eo[:, [10, 8, 9, 11]], eo[:, [14, 12, 13, 15]]
    assert np.array_equal(dA, xA ^ yA) and np.array_equal(dB, xB ^ yB) and np.array_equal(res, dA ^ dB)
    return dict(dA=dA, dB=dB, xA=xA, xB=xB, yA=yA, yB=yB, eo=eo, em=em, R=res)


def sub(d, a, b):
    return {k: v[a:b] for k, v in d.items()}


def fmt_adv(t):
    if not np.isfinite(t["eff"]):
        return "%8s" % ("-inf" if t["eff"] < 0 else "inf")
    return "%+7.4f+-%.4f" % (t["eff"], t["se"]) if np.isfinite(t.get("se", np.inf)) else "%+7.3f" % t["eff"]


def main():
    t0 = time.time()
    rng = np.random.default_rng(0x4F4E4553)
    say("ones'-complement lens, analyze.py", time.strftime("%Y-%m-%d %H:%M:%S"))
    rand, ctx = load("rand"), load("ctx")
    say("COMPUTED: digest word = E1part ^ E3part and R = dA ^ dB hold on every stored row (rand %d, ctx %d)"
        % (len(rand["dA"]), len(ctx["dA"])))
    H = len(rand["dA"]) // 2
    parts = {"TRAIN": sub(rand, 0, H), "TEST": sub(rand, H, 2 * H), "CTX": ctx}
    u = rng.integers(0, 2 ** 32, size=(H, 16), dtype=np.uint64).astype(np.uint32)
    xA, xB, yA, yB = u[:, 0:4], u[:, 4:8], u[:, 8:12], u[:, 12:16]
    parts["CTRLPY"] = dict(dA=xA ^ yA, dB=xB ^ yB, xA=xA, xB=xB, yA=yA, yB=yB, R=(xA ^ yA) ^ (xB ^ yB))

    # ---- 0. streamer reproduction check ----
    Cc = L.split_flat(np.fromfile(os.path.join(HERE, "check_real_65536.bin"), "<u8"))
    p = sub(rand, 1, 65537)
    Cp = L.counts_from(L.quantities(p["dA"], p["dB"], p["xA"], p["xB"], p["yA"], p["yB"], rng))
    keys = [k for k, _ in L.layout() if k[0] in "DRE"]
    bad = [k for k in keys if not np.array_equal(Cc[k], Cp[k])]
    say("COMPUTED streamer check: oc_stream real (gen.c seed, 1 thread; row 0 is its warm-up) vs numpy on data/rand rows "
        "1..65536: %d of %d D/R/E count blocks differ" % (len(bad), len(keys)))

    # ---- counts ----
    C = {}
    Qtrain = None
    for name, d in parts.items():
        Qv = L.quantities(d["dA"], d["dB"], d["xA"], d["xB"], d["yA"], d["yB"], rng)
        if name == "TRAIN":
            Qtrain = Qv
        C[name] = L.counts_from(Qv)
        np.savez_compressed(os.path.join(HERE, "counts_%s.npz" % name), flat=L.to_flat(C[name]))
    C["STREAM"] = L.split_flat(np.fromfile(os.path.join(HERE, "stream_real_2p28.bin"), "<u8"))
    REF = L.split_flat(np.fromfile(os.path.join(HERE, "stream_ctrl_2p28.bin"), "<u8"))
    T = {name: L.evaluate2(C[name], REF) for name in C}

    fam = [k for k in T["TRAIN"] if k[0] in L.TESTED_QS]
    F = len(fam)
    thr = 0.01 / F
    say("\n== 1. Family: %d two-sample tests vs the CONTROL STREAM (2^28) on D, R, E: per-word residues mod %s; cell 0 "
        "of each; period-4/period-8 subgroup membership; divisibility pattern by 3,5,17,257,65537; cosets of <2> and <16> "
        "in (Z/p)* for p=17,257,65537; joint 4-word residue vectors mod 3,5,15,17 (+ their zero cell). Bonferroni p < %.2e"
        % (F, ",".join(map(str, L.MODS)), thr))
    for name in ("TRAIN", "TEST", "CTX", "STREAM", "CTRLPY"):
        ps = np.array([T[name][k]["p"] for k in fam])
        pss = np.array([T[name][k]["p"] for k in T[name] if k[0] == "S"])
        say("  %-6s N=%10d  below Bonferroni: %3d  below 0.01: %4d (null ~%.1f)  min p %.2e | surrogate S: below Bonf %d, min p %.2e"
            % (name, int(C[name]["N"][0]), int((ps < thr).sum()), int((ps < 0.01).sum()), 0.01 * F, ps.min(),
               int((pss < thr).sum()), pss.min()))

    flagged = sorted([k for k in fam if T["TRAIN"][k]["p"] < thr], key=lambda k: T["TRAIN"][k]["p"])
    say("\n== 2. Flagged on TRAIN: %d. Re-tests (pass = p < 0.01 and, for cell-0 tests, the same sign). eff = KL bits/row "
        "for chi tests, log2 advantage of cell 0 for zero tests; S eff = the surrogate's effect on the same test." % len(flagged))
    say("  %-22s %9s %9s %9s %9s | %9s %9s %9s | %9s %9s | verdict" % ("test", "TRAIN p", "TEST p", "CTX p", "STREAM p",
                                                                    "TRAIN eff", "TEST eff", "STRM eff", "S TEST", "S STREAM"))
    rows = []
    for k in flagged:
        r = {n: T[n][k] for n in ("TRAIN", "TEST", "CTX", "STREAM")}
        sk = "S" + k[1:]
        sgn = np.sign(r["TRAIN"]["stat"])
        ok = {n: bool(r[n]["p"] < 0.01 and (r[n]["kind"] == "chi" or np.sign(r[n]["stat"]) == sgn)) for n in ("TEST", "CTX", "STREAM")}
        verdict = "CONFIRMED" if all(ok.values()) else "not confirmed (%s)" % ",".join(n for n in ok if not ok[n])
        s1, s2 = ("%9.3g" % T["TEST"][sk]["eff"], "%9.3g" % T["STREAM"][sk]["eff"]) if k[0] == "D" else ("%9s" % "n/a", "%9s" % "n/a")
        say("  %-22s %9.2e %9.2e %9.2e %9.2e | %9.3g %9.3g %9.3g | %s %s | %s" % (
            k, r["TRAIN"]["p"], r["TEST"]["p"], r["CTX"]["p"], r["STREAM"]["p"], r["TRAIN"]["eff"], r["TEST"]["eff"],
            r["STREAM"]["eff"], s1, s2, verdict))
        rows.append(dict(id=k, p={n: r[n]["p"] for n in r}, eff={n: r[n]["eff"] for n in r},
                         s_eff={"TEST": T["TEST"][sk]["eff"], "STREAM": T["STREAM"][sk]["eff"]}, verdict=verdict))
    json.dump(dict(reference="control stream 2^28", threshold=thr, family=F, flagged=rows),
              open(os.path.join(HERE, "flagged.json"), "w"), indent=1)
    say("  Tests significant on STREAM (Bonferroni) that were NOT flagged on TRAIN (descriptive only, not confirmations):")
    extra = sorted([k for k in fam if T["STREAM"][k]["p"] < thr and k not in flagged], key=lambda k: T["STREAM"][k]["p"])
    for k in extra[:30]:
        sk = "S" + k[1:]
        sx = " | S STREAM eff %.3g p %.2e" % (T["STREAM"][sk]["eff"], T["STREAM"][sk]["p"]) if k[0] == "D" else ""
        say("    %-22s STREAM p %.2e eff %.3g | TRAIN p %.2e%s" % (k, T["STREAM"][k]["p"], T["STREAM"][k]["eff"], T["TRAIN"][k]["p"], sx))
    if len(extra) > 30:
        say("    ... %d more" % (len(extra) - 30))

    # ---- 3. concentration at zero ----
    say("\n== 3. Does the residual lean toward 0 in ones'-complement coordinates? Cell-0 advantage log2(P_real/P_ctrl) "
        "+- 1 s.e., STREAM (2^28) vs CONTROL STREAM (2^28)")
    for q in ("D", "S", "R"):
        say("  %s (%s)" % (q, {"D": "oc(dA)-oc(dB)", "S": "surrogate", "R": "XOR residual read in Z/M"}[q]))
        for w in range(4):
            say("    word %d: %s" % (WN[w], "  ".join("m%d %s" % (m, fmt_adv(T["STREAM"]["%s.w%d.m%d.zero" % (q, w, m)]))
                                                    for m in (3, 5, 15, 17, 255, 257, 65535, 65537))))
        say("    joint 4-word zero cell: %s" % "  ".join("m%d %s (c0 %d)" % (m, fmt_adv(T["STREAM"]["%s.joint.m%d.zero" % (q, m)]),
                                                                        T["STREAM"]["%s.joint.m%d.zero" % (q, m)]["c0"]) for m in L.JMODS))
    tot = sum(T["STREAM"]["D.joint.m%d.zero" % m]["eff"] for m in (15, 17))
    say("  D joint cell 0 mod 15 and mod 17 (independent CRT components, 15.6 + 16.3 = 31.9 bits of condition): total advantage %+.3f bits" % tot)

    # XOR baseline
    bits = lambda R: ((R[:, :, None] >> np.arange(32, dtype=np.uint32)) & 1).reshape(len(R), 128)
    btr = bits(parts["TRAIN"]["R"])
    top = np.argsort(-(1.0 - btr.mean(0)))[:16]
    say("  XOR baseline (same data): the 16 bits of R with largest P(0) on TRAIN (word.bit): %s"
        % ",".join("%d.%d" % (WN[i // 32], i % 32) for i in top))
    for name in ("TRAIN", "TEST", "CTX", "CTRLPY"):
        b = bits(parts[name]["R"])
        c0 = int((b[:, top].sum(1) == 0).sum())
        mu = len(b) / 2 ** 16
        say("    %-6s P(all 16 = 0): %d rows vs %.1f uniform -> advantage %+.3f bits on a 16-bit condition"
            % (name, c0, mu, math.log2(c0 / mu) if c0 else float("-inf")))

    # magnitude (Archimedean / metric view): signed ones'-complement distance of D from 0
    say("  Metric view: bit length of |D| = min(D, M-D) (ones'-complement distance from 0); chi-square vs CTRLPY and "
        "P(|D| < 2^24) advantage")
    def blen(v):
        a = np.minimum(v, L.M - v)
        out = np.zeros(len(a), dtype=np.int64)
        nz = a > 0
        out[nz] = np.floor(np.log2(a[nz].astype(np.float64))).astype(np.int64) + 1
        return out
    Qc = L.quantities(parts["CTRLPY"]["dA"], parts["CTRLPY"]["dB"], parts["CTRLPY"]["xA"], parts["CTRLPY"]["xB"],
                      parts["CTRLPY"]["yA"], parts["CTRLPY"]["yB"], rng)
    for name in ("TRAIN", "TEST"):
        d = parts[name]
        Qv = Qtrain if name == "TRAIN" else L.quantities(d["dA"], d["dB"], d["xA"], d["xB"], d["yA"], d["yB"], rng)
        s = []
        for w in range(4):
            hb = np.bincount(blen(Qv["D"][:, w]), minlength=33)
            hc = np.bincount(blen(Qc["D"][:, w]), minlength=33)
            c, p_, df, kl = L.chi2_two(hb, hc)
            a0, b0 = int(hb[:25].sum()), int(hc[:25].sum())
            s.append("w%d chi p %.2g, P(|D|<2^24) %d vs %d (adv %+.2f)" % (WN[w], p_, a0, b0, math.log2(a0 / b0) if a0 and b0 else float("nan")))
        say("    %-5s %s" % (name, "; ".join(s)))

    # ---- 4. entropy profiles in three views ----
    say("\n== 4. Renyi-2 entropy (bits, from collisions) of A-B differences in three views: XOR a^b | mod 2^32 a-b | "
        "ones' a-b mod 2^32-1.  N = %d per part; reliable up to ~32 bits; 'top' = most common value and its frequency" % H)

    def views(a, b):
        return {"xor": (a ^ b).astype(np.int64), "mod": ((a.astype(np.int64) - b.astype(np.int64)) & 0xFFFFFFFF), "ones": L.ocsub(a, b)}

    for name in ("TRAIN", "TEST"):
        d = parts[name]
        say("  [%s]" % name)
        for lbl, arr in (("half-G ", d["em"]), ("output ", d["eo"])):
            for g, base in (("E1", 0), ("E3", 8)):
                nm = "abcd" if g == "E1" else "efgh"
                for i in range(4):
                    a, b = arr[:, base + i], arr[:, base + 4 + i]
                    out = []
                    for vn, v in views(a, b).items():
                        Hh, nd, tv, tf = L.h2(v)
                        out.append("%s %6s (%6d distinct, top %08x %.4f)" % (vn, "%.2f" % Hh if Hh else "const" if nd == 1 else "high", nd, tv, tf))
                    say("    %s %s %s%s: %s" % (lbl, g, nm[i], "1" if lbl[0] == "h" else "2", " | ".join(out)))
        Qv = Qtrain if name == "TRAIN" else L.quantities(d["dA"], d["dB"], d["xA"], d["xB"], d["yA"], d["yB"], rng)
        for w in range(4):
            out = []
            for vn, v in views(d["dA"][:, w], d["dB"][:, w]).items():
                Hh, nd, tv, tf = L.h2(v)
                out.append("%s %s" % (vn, "%.2f" % Hh if Hh else "high"))
            Hh, nd, tv, tf = L.h2(Qv["E"][:, w])
            out.append("eps %s" % ("%.2f" % Hh if Hh else "high"))
            say("    residual word %d: %s" % (WN[w], " | ".join(out)))
    d = parts["CTRLPY"]
    out = []
    for vn, v in views(d["dA"][:, 0], d["dB"][:, 0]).items():
        Hh, nd, tv, tf = L.h2(v)
        out.append("%s %s" % (vn, "%.2f" % Hh if Hh else "high"))
    Hh, nd, tv, tf = L.h2(Qc["E"][:, 0])
    out.append("eps %s" % ("%.2f" % Hh if Hh else "high"))
    say("  [CTRLPY] uniform words, residual word 1: %s" % " | ".join(out))

    # ---- 5. split test ----
    say("\n== 5. Split test: D = oc_diff(E1 part) + oc_diff(E3 part) + eps (mod 2^32-1). DERIVED identity "
        "eps = -2[(x&y) - (x'&y')] since x^y = x + y - 2(x&y).")
    G = ((parts["TRAIN"]["xA"] & parts["TRAIN"]["yA"]).astype(np.int64) - (parts["TRAIN"]["xB"] & parts["TRAIN"]["yB"]).astype(np.int64))
    say("  COMPUTED identity on TRAIN: %s" % bool(np.array_equal((-2 * G) % L.M, Qtrain["E"])))
    for name in ("TRAIN", "TEST", "STREAM"):
        z = []
        for w in range(4):
            ps = "  ".join("m%d p %.2g" % (m, T[name]["E.w%d.m%d.chi" % (w, m)]["p"]) for m in (3, 5, 15, 17, 255))
            z.append("w%d: %s" % (WN[w], ps))
        say("  %-6s eps residues vs control eps: %s" % (name, " || ".join(z)))
    for name in ("TRAIN", "TEST"):
        d = parts[name]
        Qv = Qtrain if name == "TRAIN" else L.quantities(d["dA"], d["dB"], d["xA"], d["xB"], d["yA"], d["yB"], rng)
        say("  %-6s P(eps = 0) per word: %s   (eps = 0 would make D = E1 part + E3 part exactly)"
            % (name, " ".join("%.2e" % (Qv["E"][:, w] == 0).mean() for w in range(4))))
    # ---- 6. multiplicative relations between words: same rotation orbit (spiral) and ratio cosets ----
    say("\n== 6. Multiplicative relations between residual words. In Z/(2^32-1), x -> 2x is rotate-left-1, so the orbit "
        "{+-2^r x} is the word's rotations and complements ('spiral' orbit). Test 1: rows where D_j = +-2^r D_i for some r "
        "(uniform rate ~2^-26 per pair). Test 2: coset of the ratio D_j/D_i in (Z/p)*/<2> and /<16>, two-sample vs CTRLPY.")

    def neck(v):
        v = v.astype(np.uint64) & np.uint64(0xFFFFFFFF)
        best = v.copy()
        for r in range(1, 32):
            x = ((v << np.uint64(r)) | (v >> np.uint64(32 - r))) & np.uint64(0xFFFFFFFF)
            np.minimum(best, x, out=best)
        return best

    def pmneck(v):
        v = v.astype(np.int64)
        neg = np.where(v == 0, 0, L.M - v)
        return np.minimum(neck(v), neck(neg))

    pairs = [(i, j) for i in range(4) for j in range(i + 1, 4)]
    for name in ("TRAIN", "TEST", "CTRLPY"):
        d = parts[name]
        Qv = Qtrain if name == "TRAIN" else (Qc if name == "CTRLPY" else L.quantities(d["dA"], d["dB"], d["xA"], d["xB"], d["yA"], d["yB"], rng))
        nk = [pmneck(Qv["D"][:, w]) for w in range(4)]
        hits = ["%d-%d:%d" % (WN[i], WN[j], int((nk[i] == nk[j]).sum())) for i, j in pairs]
        say("  %-6s rows with D_j = +-2^r D_i: %s" % (name, " ".join(hits)))
    # positive control: inside E1, d2 = ROR(d1 ^ a2, 8) with d1 common, so oc_diff(d2) = 2^24 oc_diff(a2) whenever d1 has
    # no bit where a2 differs; the test must see this
    for name in ("TRAIN",):
        eo = parts[name]["eo"]
        da2, dd2 = L.ocsub(eo[:, 0], eo[:, 4]), L.ocsub(eo[:, 3], eo[:, 7])
        exact = int(((dd2 * pow(2, 8, L.M)) % L.M == da2).sum())
        same = int((pmneck(da2) == pmneck(dd2)).sum())
        say("  positive control (E1 a2 vs d2 ones' differences, %s): exact d2 = 2^-8 a2 in %d rows, same +-orbit in %d rows of %d"
            % (name, exact, same, len(da2)))
    # ratio cosets
    RT = {}
    for name in ("TRAIN", "TEST", "CTRLPY"):
        d = parts[name]
        Qv = Qtrain if name == "TRAIN" else (Qc if name == "CTRLPY" else L.quantities(d["dA"], d["dB"], d["xA"], d["xB"], d["yA"], d["yB"], rng))
        for (i, j) in pairs:
            for p_, g in L.COSETS:
                a, b = Qv["D"][:, i] % p_, Qv["D"][:, j] % p_
                ok = (a != 0) & (b != 0)
                idx = L.coset_index(p_, g)
                cls = (L.DLOG[p_][b[ok]] - L.DLOG[p_][a[ok]]) % idx
                RT[(name, i, j, p_, g)] = np.bincount(cls, minlength=idx)
    fam6 = [(i, j, p_, g) for (i, j) in pairs for p_, g in L.COSETS]
    thr6 = 0.01 / len(fam6)
    for name in ("TRAIN", "TEST"):
        res6 = []
        for key in fam6:
            c, p_, df, kl = L.chi2_two(RT[(name,) + key], RT[("CTRLPY",) + key])
            res6.append((p_, key, kl))
        res6.sort()
        nb = sum(1 for r in res6 if r[0] < thr6)
        say("  %-6s ratio-coset tests: %d, below Bonferroni %.1e: %d; smallest p %.2e (%s)" % (
            name, len(fam6), thr6, nb, res6[0][0], "words %d/%d mod %d coset of <%d>" % (WN[res6[0][1][0]], WN[res6[0][1][1]], res6[0][1][2], res6[0][1][3])))
    say("\ndone in %.1f s" % (time.time() - t0))


if __name__ == "__main__":
    main()
