#!/usr/bin/env python3
"""Angle 8 test: the stage-1 (outer filter) pass share of research/impl/outer.py with the starting state h0..h7 in place
of the IV (non-first block: c-slot words stay IV0..IV3, flags 2). numpy, vectorised scalar path, exact outer.py tables.
Usage: python a8.py [--log2n 23] [--nh 64] [--seed 8]"""
import argparse, importlib.util, json, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUTER = os.path.join(HERE, "..", "..", "..", "impl", "outer.py")
spec = importlib.util.spec_from_file_location("outer", OUTER)
O = importlib.util.module_from_spec(spec); spec.loader.exec_module(O)
MASK, IV, ror, rol = O.MASK, O.IV, O.ror, O.rol
Sum, Neg, X, R, L = O.Sum, O.Neg, O.X, O.R, O.L


def lines_for(h, flags, W4=O.W4):
    'outer.LINES with the round-0 constants rebuilt from h (a/b slots) and IV0..IV3 (c slots), flags in column 3.'
    K = (h[2] + h[6]) & MASK
    K2A = (K + W4) & MASK                       # a1 of column 2 (a = h2, b = h6, m4 = W4 pinned)
    K2D = ror(K2A ^ O.LEN_A, 16)
    K2C = (IV[2] + K2D) & MASK                  # c slot: IV2
    K2B = ror(h[6] ^ K2C, 12)                   # b slot: h6
    sub = {
        "K3.a1": Sum((h[3] + h[7]) & MASK, "w6"),
        "K3.d1": R(X("K3.a1", flags), 16),
        "K3.c1": Sum(IV[3], "K3.d1"),
        "K3.b1": R(X(h[7], "K3.c1"), 12),
        "K1.d1": Sum("K1.c1", Neg(IV[1])),
        "w2": Sum("K1.a1", Neg(h[1]), Neg(h[5])),
        "K1.b1": R(X(h[5], "K1.c1"), 12),
        "S10": Sum(K2C, "S14"),
        "S2": X(L("S14", 8), K2D),
        "S6": R(X(K2B, "S10"), 7),
        "K0.c1": X(L("K0.b1", 12), h[4]),
        "K0.d1": Sum("K0.c1", Neg(IV[0])),
        "w5": Sum("S2", Neg(K2A), Neg(K2B)),
    }
    return [(n, sub.get(n, e)) for n, e in O.LINES], K2A


def slice_of(lines, targets=("Y9", "w8")):
    need, keep = set(targets), []
    for name, e in reversed(lines):
        if name in need:
            keep.append((name, e)); d = set(); O.deps(e, d); need |= d
    return list(reversed(keep))


def vev(e, v):
    if isinstance(e, int):
        return np.uint32(e)
    if isinstance(e, str):
        return v[e]
    k = e[0]
    if k == "sum":
        s = np.uint32(0)
        for t in e[1]:
            s = s - vev(t[1], v) if isinstance(t, tuple) and t[0] == "neg" else s + vev(t, v)
        return s
    if k == "xor":
        return vev(e[1], v) ^ vev(e[2], v)
    if k == "ror":
        x, r = vev(e[1], v), e[2] % 32
        return (x >> np.uint32(r)) | (x << np.uint32(32 - r)) if r else x
    raise ValueError(k)


def vlook(tabs, x):
    s = tabs[0][x & 255]
    for p in (1, 2, 3):
        s = tabs[p][s + ((x >> np.uint32(8 * p)) & 255)]
    return s


def run(sl, n, rng, tabs1, tabs2, chunk=1 << 21):
    passes = e = 0
    for off in range(0, n, chunk):
        m = min(chunk, n - off)
        w = rng.integers(0, 1 << 32, size=(8, m), dtype=np.uint64).astype(np.uint32)
        v = dict(zip(O.OUTER_WORDS, w[:7]))
        e1 = np.uint32(O.CLASS_VALUE) | (w[7] & np.uint32(O.FREE_MASK))
        v["Y4"] = e1 - np.uint32(O.Y3)
        for name, ex in sl:
            v[name] = vev(ex, v)
        omega = np.uint32(O.Y3) + v["Y4"] + v["w8"]
        m2 = vlook(tabs2, omega)
        x = vlook(tabs1, v["Y9"]) & m2
        e += int(np.count_nonzero(m2)); passes += int(np.count_nonzero(x))
    return passes, e


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log2n", type=int, default=23); ap.add_argument("--nh", type=int, default=64)
    ap.add_argument("--seed", type=int, default=8)
    a = ap.parse_args()
    t0 = time.time()
    # 1. identity check: lines_for(IV, 3) is outer.LINES exactly
    li, K2A = lines_for(IV, O.CTR_FLAGS)
    assert li == O.LINES and K2A == O.K2A, "lines_for(IV,3) != outer.LINES"
    assert slice_of(O.LINES) == O.slice_lines()
    # which h words reach Y9 / w8
    sl = slice_of(li)
    print("slice to Y9 and w8:", len(sl), "lines:", " ".join(n for n, _ in sl))
    # 2. scalar cross-check of the vector path on 1000 random steps (IV, flags 3)
    rng = np.random.default_rng(a.seed)
    w = rng.integers(0, 1 << 32, size=(8, 1000), dtype=np.uint64).astype(np.uint32)
    v = dict(zip(O.OUTER_WORDS, w[:7])); v["Y4"] = (np.uint32(O.CLASS_VALUE) | (w[7] & np.uint32(O.FREE_MASK))) - np.uint32(O.Y3)
    for name, ex in sl:
        v[name] = vev(ex, v)
    bad = 0
    for i in range(1000):
        s = O.scalar_outer([int(w[k, i]) for k in range(8)])
        bad += s["Y9"] != int(v["Y9"][i]) or s["w8"] != int(v["w8"][i])
    print("vector vs outer.scalar_outer mismatches (1000 steps):", bad); assert bad == 0
    raw, t1, t2 = O.build_tables()
    tabs1 = [np.array(t, dtype=np.uint32) for t in t1]; tabs2 = [np.array(t, dtype=np.uint32) for t in t2]
    # table check against scalar look on 2000 words
    xs = rng.integers(0, 1 << 32, size=2000, dtype=np.uint64).astype(np.uint32)
    tb = sum(int(vlook(tabs1, xs)[i]) != O.look(t1, int(xs[i])) or int(vlook(tabs2, xs)[i]) != O.look(t2, int(xs[i]))
             for i in range(2000))
    print("vector vs outer.look mismatches (2000 words):", tb); assert tb == 0
    exact_pass, exact_e = O.SHARE / 2**64, O.E_COUNT / 2**32
    n = 1 << a.log2n
    bit3_iv = ((O.W4 + IV[2] + IV[6]) >> 3) & 1
    cases = [("IV flags3", list(IV), 3), ("IV flags2", list(IV), 2)]
    hr = np.random.default_rng(a.seed + 1000)
    flipped = 0
    for j in range(a.nh):
        h = [int(x) for x in hr.integers(0, 1 << 32, size=8, dtype=np.uint64)]
        if ((O.W4 + h[2] + h[6]) >> 3) & 1 != bit3_iv:   # keep W4B - W4 = +8 (same round-1 instance as the IV)
            h[2] ^= 8; flipped += 1
        cases.append((f"h{j:02d}", h, 2))
    print(f"N = 2^{a.log2n} steps per case; exact pass share {exact_pass:.6e}, E share {exact_e:.6f}; "
          f"h2 bit 3 flipped in {flipped} of {a.nh} draws to keep W4B = W4 + 8")
    rows = []
    for ci, (name, h, fl) in enumerate(cases):
        li, _ = lines_for(h, fl)
        sl = slice_of(li)
        p, e = run(sl, n, np.random.default_rng([a.seed, ci]), tabs1, tabs2)
        r, re_ = p / n / exact_pass, e / n / exact_e
        z = (p - n * exact_pass) / (n * exact_pass * (1 - exact_pass)) ** 0.5
        rows.append(dict(name=name, h=["%08x" % x for x in h], flags=fl, passes=p, e=e, ratio=r, e_ratio=re_, z=z))
        print(f"{name:10s} passes {p:7d} ratio {r:.4f} z {z:+.2f}  E {e:8d} ratio {re_:.4f}", flush=True)
    rs = np.array([r["ratio"] for r in rows[2:]]); zs = np.array([r["z"] for r in rows[2:]])
    es = np.array([r["e_ratio"] for r in rows[2:]])
    summ = dict(n=n, nh=a.nh, ratio_min=rs.min(), ratio_max=rs.max(), ratio_mean=rs.mean(), ratio_sd=rs.std(ddof=1),
                spread_pct=100 * (rs.max() - rs.min()) / rs.mean(), z_sd=zs.std(ddof=1), z_chi2=float((zs ** 2).sum()),
                e_ratio_min=es.min(), e_ratio_max=es.max(), iv3=rows[0]["ratio"], iv2=rows[1]["ratio"],
                expected_sd_binomial=1 / (n * exact_pass) ** 0.5, seconds=time.time() - t0)
    print(json.dumps(summ, indent=1))
    with open(os.path.join(HERE, "a8_result.json"), "w") as f:
        json.dump(dict(summary=summ, rows=rows), f, indent=1)


if __name__ == "__main__":
    main()
