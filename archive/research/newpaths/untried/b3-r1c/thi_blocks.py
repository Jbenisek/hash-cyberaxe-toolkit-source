"""b3-r1c scout: over the legal t_hi walk of one outer step, how many distinct values does
omega mod 2^k take (k = 9..20), and are they runs of consecutive t_hi?  Also: how many
distinct omega mod 2^9 over a front-line cluster (32 members differing in e1 bits 10..14)?
"""
import random, sys
from model import build, rand_params, trace, IV, M, PIN, rol

if __name__ == "__main__":
    rng = random.Random(9)
    for c in range(3):
        p = rand_params(rng)
        wA, tlo, wB = build(p)
        T = trace(wA, tlo, 55)
        Kd1, S0, S5, S15 = T["K1.d1"], T["S0"], T["S5"], T["S15"]
        Ca1, X4, X15, Y3, y = T["C0.a1"], T["X4"], PIN[15], T["Y3"], T["Y4"]
        oms = []
        P = rol(Kd1, 16) & ~((1 << 19) - 1) & M  # legal K1.a1 block: t_hi = K1.a1 ^ rol(K1.d1,16) < 2^19
        order = sys.argv[1] if len(sys.argv) > 1 else "thi"
        for j in range(1 << 19):
            thi = j if order == "thi" else ((P + j) ^ rol(Kd1, 16))  # "w2": walk K1.a1 (so w2) in order
            assert thi < (1 << 19)
            w2 = ((rol(Kd1, 16) ^ thi) - IV[1] - IV[5]) & M
            X0 = (Ca1 - X4 - w2) & M
            w8 = ((rol(rol(X15, 8) ^ X0, 16) ^ S15) - S0 - S5) & M
            oms.append((Y3 + y + w8) & M)
        row = []
        for k in (9, 12, 16, 17, 20):
            vals = [o & ((1 << k) - 1) for o in oms]
            runs = 1 + sum(vals[i] != vals[i - 1] for i in range(1, len(vals)))
            row.append("mod2^%d: %d values, %d runs" % (k, len(set(vals)), runs))
        print("outer step %d (t_hi walk, 2^19 steps): %s" % (c, "; ".join(row)))
        # front-line cluster for comparison: members y' = y with e1 = Y3 + y' bits 10..14 varied
        e1 = (Y3 + y) & M
        vals = set()
        for v in range(32):
            e1v = (e1 & ~(0x1F << 10)) | (v << 10)
            q = dict(p); q["y"] = (e1v - Y3) & M
            wq, tq, _ = build(q)
            vals.add((Y3 + q["y"] + wq[8]) & 511)
        print("    front-line cluster of 32 members (e1 bits 10..14): omega mod 2^9 takes %d values" % len(vals))
        sys.stdout.flush()
