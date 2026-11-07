"""b3-r1c scout: t_hi as an inner walk (no filter).

For a front-line outer step (context + member y, t_hi = 0), walk t_hi over its whole legal
range [0, 2^19) (reference: messages < 2^61 bytes, so the chunk counter t < 2^51).  K1's mid
is fixed by S9, S13, so w2 = (rol(K1.d1,16) ^ t_hi) - IV1 - IV5 runs over an interval of 2^19;
X0 = C0.a1 - X4 - w2 keeps C0.a1, so C0 is unchanged; D1 is unchanged.  Changed per step:
w2, w3, D0 (w8, w9, X5, X10), C1 (Y1, Y9) and C2's first half.
Checks a sample of steps on the reference compression; reports omega = Y3 + y + w8 structure.
"""
import random, sys, time
from model import build, rand_params, trace, ref, IV, M, W4, W4B, PIN, ror, rol

if __name__ == "__main__":
    rng = random.Random(5)
    nctx = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    t0 = time.time()
    for c in range(nctx):
        wA, tlo, wB = build(rand_params(rng))
        T = trace(wA, tlo, 55)
        Kd1 = T["K1.d1"]; Kb1 = T["K1.b1"]; S1, S5, S0, S10, S15 = T["S1"], T["S5"], T["S0"], T["S10"], T["S15"]
        Ca1, X4, X15 = T["C0.a1"], T["X4"], PIN[15]
        Y3, y = T["Y3"], T["Y4"]
        om9 = {}
        om_all = set()
        bad = 0
        for thi in range(1 << 19):
            Ka1 = rol(Kd1, 16) ^ thi
            w2 = (Ka1 - IV[1] - IV[5]) & M
            X0 = (Ca1 - X4 - w2) & M
            Dd1 = rol(X15, 8) ^ X0
            Da1 = rol(Dd1, 16) ^ S15
            w8 = (Da1 - S0 - S5) & M
            om = (Y3 + y + w8) & M
            om9[om & 511] = om9.get(om & 511, 0) + 1
            if thi % 4099 == 0:  # verify on the reference
                Dc1 = (S10 + Dd1) & M; Db1 = ror(S5 ^ Dc1, 12)
                w = list(wA); w[2] = w2; w[3] = (S1 - Ka1 - Kb1) & M; w[8] = w8; w[9] = (X0 - Da1 - Db1) & M
                wb = list(w); wb[4] = W4B; wb[5] = (w[5] + W4 - W4B) & M
                t = (thi << 32) | tlo
                a = ref._compress(IV, w, t, 55, 3, 2)[:8]; b = ref._compress(IV, wb, t, 63, 3, 2)[:8]
                r = [p ^ q for p, q in zip(a, b)]
                T2 = trace(w, t, 55)
                same_c0 = all(T2["Y%d" % i] == T["Y%d" % i] for i in (0, 4, 8, 12))
                same_d1 = all(T2["X%d" % i] == T["X%d" % i] for i in (1, 6, 11, 12))
                bad += not ((r[0] | r[2] | r[5] | r[7]) == 0 and same_c0 and same_d1 and T2["X0"] == X0)
        sizes = sorted(om9.values(), reverse=True)
        print("context %d: 2^19 legal t_hi steps; reference check on %d steps, failures %d; "
              "distinct omega mod 2^9 = %d, block sizes %s" % (
                  c, (1 << 19) // 4099 + 1, bad, len(om9), sizes[:10]))
        sys.stdout.flush()
    print("time %.0fs" % (time.time() - t0))
