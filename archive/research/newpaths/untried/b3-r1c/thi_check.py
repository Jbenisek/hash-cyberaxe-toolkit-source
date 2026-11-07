"""b3-r1c scout: numeric check of the t_hi basis from hold_e_out.txt.

Basis {Y4, E1.c1, w8, C0.d1, D2.a1, D2.b1, S11, S4, X9, w6} with the 64-bit counter's high
word V13 = t_hi derived.  Verifies the pair on the reference compression (counter
t = t_hi*2^32 + t_lo) and measures how often t_hi is legal: the reference rejects inputs of
2^61 bytes or more, so the last chunk counter t < 2^51, i.e. t_hi < 2^19.
"""
import random, sys, time
import gd_eval as ge
from model import IV, ref, M, W4, W4B, trace

Y3A, Y11A = 0x8127C181, 0x7AF77F38
ge.CALLS.append(("E1", ("Y1", "Y6", "Y11", "Y12"), ("w12", "w5"), ("Z1", "Z6", "Z11", "Z12")))
ge.CALLS.append(("E3", ("Y3", "Y4", "Y9", "Y14"), ("w15", "w8"), ("Z3", "Z4", "Z9", "Z14")))
for nm, (a, b, c, d), (x, y), (A, B, C, D) in ge.CALLS[-2:]:
    a1, b1, c1, d1 = (nm + "." + s for s in ("a1", "b1", "c1", "d1"))
    ge.REL += [("add", a1, [a, b, x]), ("rot", d1, 16, d, a1), ("add", c1, [c, d1]), ("rot", b1, 12, b, c1),
               ("add", A, [a1, b1, y]), ("rot", D, 8, d1, A), ("add", C, [c1, D]), ("rot", B, 7, b1, C)]

B = ["Y4", "E1.c1", "w8", "C0.d1", "D2.a1", "D2.b1", "S11", "S4", "X9", "w6"]
if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
    rng = random.Random(11)
    ok, legal, top = 0, 0, [0] * 16
    t0 = time.time()
    for i in range(n):
        val = ge.consts()
        del val["V13"]
        val.update({"Y3": Y3A, "Y11": Y11A})
        ch = {b: rng.getrandbits(32) for b in B}
        val.update(ch)
        val, checks, _ = ge.close(val)
        thi, tlo = val["V13"], val["V12"]
        t = (thi << 32) | tlo
        w = [val["w%d" % k] for k in range(16)]
        wB = list(w); wB[4] = W4B; wB[5] = (w[5] + W4 - W4B) & M
        if i < 300:
            a = ref._compress(IV, w, t, 55, 3, 2)[:8]; b = ref._compress(IV, wB, t, 63, 3, 2)[:8]
            r = [x ^ y for x, y in zip(a, b)]
            T = trace(w, t, 55)
            ok += (not checks and (r[0] | r[2] | r[5] | r[7]) == 0 and T["Y4"] == ch["Y4"]
                   and T["E1.c1"] == ch["E1.c1"] and w[8] == ch["w8"])
        legal += thi < (1 << 19)
        top[thi >> 28] += 1
    e = n / 16.0
    chi2 = sum((c - e) ** 2 / e for c in top)
    print("basis %s (t_hi derived): %d/300 verified on the reference (half-collision, chosen Y4, E1.c1, w8)"
          % (",".join(B), ok))
    print("t_hi legal (< 2^19): %d of %d (expected n*2^-13 = %.2f if uniform); top-4-bit chi2 = %.1f (15 df)  %.0fs"
          % (legal, n, n / 8192.0, chi2, time.time() - t0))
