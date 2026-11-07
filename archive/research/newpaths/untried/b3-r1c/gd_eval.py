"""b3-r1c scout: numeric closure. Given values for a basis (plus constants/pins), solve every
relation that has one unknown, in closure order, and check the rest.  Used to verify the
symbolic GD claims of gd.py / hold.py on the real compression (reference blake3.py).

Usage: python gd_eval.py basis   -> random values for the 9-word basis
                                     Y4,Y14,Y12,w12,w5,C0.d1,D2.b1,X9,w6 (hold3_out.txt)
       python gd_eval.py lift    -> planted pair; give the lift its 9 E words and the 5 GD
                                     words K3.a1,S3,S4,C0.c1,D2.c1 (gd_lift_out.txt); also
                                     a wrong D2.c1 to show the 4 checks reject it
"""
import random, sys
from model import build, rand_params, trace, PIN, W4, W13, W4B, IV, ref, ror, rol, M

CALLS = [
    ("K0", ("V0", "V4", "V8", "V12"), ("w0", "w1"), ("S0", "S4", "S8", "S12")),
    ("K1", ("V1", "V5", "V9", "V13"), ("w2", "w3"), ("S1", "S5", "S9", "S13")),
    ("K2", ("V2", "V6", "V10", "V14"), ("w4", "w5"), ("S2", "S6", "S10", "S14")),
    ("K3", ("V3", "V7", "V11", "V15"), ("w6", "w7"), ("S3", "S7", "S11", "S15")),
    ("D0", ("S0", "S5", "S10", "S15"), ("w8", "w9"), ("X0", "X5", "X10", "X15")),
    ("D1", ("S1", "S6", "S11", "S12"), ("w10", "w11"), ("X1", "X6", "X11", "X12")),
    ("D2", ("S2", "S7", "S8", "S13"), ("w12", "w13"), ("X2", "X7", "X8", "X13")),
    ("D3", ("S3", "S4", "S9", "S14"), ("w14", "w15"), ("X3", "X4", "X9", "X14")),
    ("C0", ("X0", "X4", "X8", "X12"), ("w2", "w6"), ("Y0", "Y4", "Y8", "Y12")),
    ("C1", ("X1", "X5", "X9", "X13"), ("w3", "w10"), ("Y1", "Y5", "Y9", "Y13")),
    ("C2", ("X2", "X6", "X10", "X14"), ("w7", "w0"), ("Y2", "Y6", "Y10", "Y14")),
]
REL = []  # ("add", out, [terms]) or ("rot", out, n, p, q): out = ror(p ^ q, n)
for nm, (a, b, c, d), (x, y), (A, B, C, D) in CALLS:
    a1, b1, c1, d1 = (nm + "." + s for s in ("a1", "b1", "c1", "d1"))
    REL += [("add", a1, [a, b, x]), ("rot", d1, 16, d, a1), ("add", c1, [c, d1]), ("rot", b1, 12, b, c1),
            ("add", A, [a1, b1, y]), ("rot", D, 8, d1, A), ("add", C, [c1, D]), ("rot", B, 7, b1, C)]


def words(r):
    return [r[1]] + r[2] if r[0] == "add" else [r[1], r[3], r[4]]


def solve(r, val, unk):
    if r[0] == "add":
        out, terms = r[1], r[2]
        if unk == out:
            return sum(val[t] for t in terms) & M
        return (val[out] - sum(val[t] for t in terms if t != unk)) & M
    _, out, n, p, q = r
    if unk == out:
        return ror(val[p] ^ val[q], n)
    other = q if unk == p else p
    return rol(val[out], n) ^ val[other]


def holds(r, val):
    if r[0] == "add":
        return val[r[1]] == sum(val[t] for t in r[2]) & M
    return val[r[1]] == ror(val[r[3]] ^ val[r[4]], r[2])


def consts():
    v = {"V%d" % i: x for i, x in enumerate(list(IV) + list(IV[:4]))}
    v.update({"V13": 0, "V14": 55, "V15": 3, "w4": W4, "w13": W13, "w14": 0, "w15": 0})
    v.update({"X%d" % i: PIN[i] for i in PIN})
    return v


def close(val, used=None):
    used = set() if used is None else used
    checks = []
    changed = True
    while changed:
        changed = False
        for i, r in enumerate(REL):
            if i in used:
                continue
            unk = [w for w in words(r) if w not in val]
            if len(unk) == 1:
                val[unk[0]] = solve(r, val, unk[0]); used.add(i); changed = True
            elif not unk:
                used.add(i); checks.append(holds(r, val)); changed = True
    return val, checks, used


def pair_from(val):
    w = [val["w%d" % i] for i in range(16)]
    t = val["V12"]
    wB = list(w); wB[4] = W4B; wB[5] = (w[5] + W4 - W4B) & M
    a = ref._compress(IV, w, t, 55, 3, 2)[:8]; b = ref._compress(IV, wB, t, 63, 3, 2)[:8]
    return w, t, [x ^ y for x, y in zip(a, b)]


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "basis"
    rng = random.Random(7)
    if mode == "basis":
        B = ["Y4", "Y14", "Y12", "w12", "w5", "C0.d1", "D2.b1", "X9", "w6"]
        ok, n = 0, 500
        for _ in range(n):
            val = consts()
            chosen = {b: rng.getrandbits(32) for b in B}
            val.update(chosen)
            val, checks, _ = close(val)
            w, t, res = pair_from(val)
            T = trace(w, t, 55)
            good = (len(checks) == 0 and (res[0] | res[2] | res[5] | res[7]) == 0
                    and all(T[k] == chosen[k] for k in ("Y4", "Y14", "Y12"))
                    and w[12] == chosen["w12"] and w[5] == chosen["w5"])
            ok += good
        print("basis %s: %d/%d random choices give a legal half-collision pair with the chosen "
              "Y4,Y14,Y12,w12,w5 (checks needed: 0)" % (",".join(B), ok, n))
    else:
        n, ok, rej = 200, 0, 0
        G5 = ["K3.a1", "S3", "S4", "C0.c1", "D2.c1"]
        E9 = ["Y1", "Y6", "Y12", "Y4", "Y9", "Y14"]
        for _ in range(n):
            wA, t, wB = build(rand_params(rng))
            T = trace(wA, t, 55)
            base = consts()
            base.update({k: T[k] for k in E9}); base.update({"w5": wA[5], "w8": wA[8], "w12": wA[12]})
            val = dict(base); val.update({g: T[g] for g in G5[:4]})
            val, checks, used = close(val)
            # D2.c1 is not determined by the first four: confirm, then give it
            fourth_open = "D2.c1" not in val
            val[("D2.c1")] = T["D2.c1"]
            val, checks2, _ = close(val, used)
            w, tt, res = pair_from(val)
            ok += fourth_open and all(checks + checks2) and w == list(wA) and tt == t
            bad = dict(base); bad.update({g: T[g] for g in G5[:4]}); bad["D2.c1"] = T["D2.c1"] ^ (1 << rng.randrange(32))
            bad, cb, _ = close(bad)
            rej += not all(cb)
        print("lift: %d/%d planted pairs recovered from the 9 E words + 5 GD words (checks after the 4th "
              "and 5th guess: %d and %d), one-bit-wrong D2.c1 rejected %d/%d" % (
                  ok, n, len(checks), len(checks2), rej, n))
