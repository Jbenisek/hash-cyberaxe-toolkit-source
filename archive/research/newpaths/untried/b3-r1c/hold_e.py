"""b3-r1c scout: which E1/E3 internal words can the late round-1-column words prescribe for free?

Relation system of gd.py plus E1 = G(Y1,Y6,Y11,Y12; w12,w5) and E3 = G(Y3,Y4,Y9,Y14; w15,w8)
for message A (Y3, Y11, w15 constants).  A target set H is free-holdable if a 9-word basis
containing H closes every word with 0 checks.  Exchange search as in hold.py (depth 2).
Optional: V13 (t_hi) unknown, to see what a free high counter word would add.
"""
import itertools, sys, time

BASE = [
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
    ("E1", ("Y1", "Y6", "Y11", "Y12"), ("w12", "w5"), ("Z1", "Z6", "Z11", "Z12")),
    ("E3", ("Y3", "Y4", "Y9", "Y14"), ("w15", "w8"), ("Z3", "Z4", "Z9", "Z14")),
]


def build(thi_free):
    VARS, REL = [], []

    def vid(n):
        if n not in VARS:
            VARS.append(n)
        return VARS.index(n)
    for nm, (a, b, c, d), (x, y), (A, B, C, D) in BASE:
        a1, b1, c1, d1 = (nm + "." + s for s in ("a1", "b1", "c1", "d1"))
        for r in ((a1, a, b, x), (d1, d, a1), (c1, c, d1), (b1, b, c1),
                  (A, a1, b1, y), (D, d1, A), (C, c1, D), (B, b1, C)):
            REL.append(tuple(vid(v) for v in r))
    const = ["V%d" % i for i in range(16) if i != 12 and not (thi_free and i == 13)]
    const += ["w4", "w13", "w14", "w15", "X3", "X7", "X11", "X15", "Y3", "Y11"]
    return VARS, REL, const


def make(thi_free):
    VARS, REL, CONST = build(thi_free)
    NV, NR = len(VARS), len(REL)
    OCC = [[] for _ in range(NV)]
    for ri, r in enumerate(REL):
        for v in r:
            OCC[v].append(ri)
    RELM = [sum(1 << v for v in r) for r in REL]
    FULL = (1 << NV) - 1
    K0 = sum(1 << VARS.index(c) for c in CONST)

    def close(known, used, new):
        checks, stack = 0, list(new)
        while stack:
            v = stack.pop()
            for ri in OCC[v]:
                if used >> ri & 1:
                    continue
                unk = RELM[ri] & ~known
                if unk == 0:
                    used |= 1 << ri; checks += 1
                elif unk & (unk - 1) == 0:
                    known |= unk; used |= 1 << ri; stack.append(unk.bit_length() - 1)
        return known, used, checks

    k0, u0, c0 = close(K0, 0, [v for v in range(NV) if K0 >> v & 1])
    dof = (NV - bin(K0).count("1")) - NR

    def is_basis(names):
        known, u = k0, u0
        for n in names:
            v = VARS.index(n)
            if known >> v & 1:
                return False
            known, u, ch = close(known | (1 << v), u, [v])
            if ch:
                return False
        return known == FULL

    others = [v for v in VARS if not (K0 >> VARS.index(v) & 1)]

    def holdable(H, B0, depth=2):
        need = dof - len(H)
        pool = [b for b in B0 if b not in H]
        oth = [o for o in others if o not in H]
        for T in itertools.combinations(pool, need):
            if is_basis(list(H) + list(T)):
                return list(H) + list(T)
        for dd in range(1, depth + 1):
            for T in itertools.combinations(pool, need - dd):
                for O in itertools.combinations(oth, dd):
                    if set(O) & set(T):
                        continue
                    if is_basis(list(H) + list(T) + list(O)):
                        return list(H) + list(T) + list(O)
        return None
    return is_basis, holdable, dof


if __name__ == "__main__":
    B0 = ["C0.d1", "D2.a1", "D2.b1", "S11", "S4", "X9", "w6", "Y4", "w0"]
    TARGETS = [("Y4", "E1.c1"), ("Y4", "E3.c1"), ("Y4", "E3.d1"), ("Y4", "E1.b1"), ("Y4", "E3.b1"),
               ("Y4", "E1.c1", "E3.c1"), ("Y4", "E1.c1", "E3.d1"), ("Y4", "E1.c1", "w8"),
               ("Y4", "E1.c1", "Y9"), ("Y4", "E1.c1", "Y1"), ("Y4", "E1.c1", "E1.b1"),
               ("Y4", "E3.c1", "E3.b1"), ("Y4", "E3.c1", "Y1")]
    for thi in (False, True):
        is_basis, holdable, dof = make(thi)
        b0 = B0 + (["V13"] if thi else [])
        print("t_hi %s: dof=%d; front-line basis%s is a basis: %s" % (
            "FREE (V13 unknown)" if thi else "= 0", dof, "+V13" if thi else "", is_basis(b0)))
        t0 = time.time()
        for H in TARGETS:
            b = holdable(H, b0, depth=2 if not thi else 1)
            print("   %-24s %s" % (",".join(H), ("FREE  basis=" + ",".join(b)) if b else "not found"))
            sys.stdout.flush()
        print("   time %.1fs" % (time.time() - t0))
