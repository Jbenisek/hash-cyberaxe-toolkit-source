# formula_check.py -- verify_literature_1
# Checks the claim: Dong et al. 2021 (ePrint 2021/427) sec. 6, eq. 9/10, with w=32, h=8, t=4
# gives best 2^64 when DoF+, DoF-, m >= 4 words.
# All sizes in WORDS (log base 2^w), w = 32. Grid step 1/16 word = 2 bits.
import numpy as np

w, h = 32, 8
step = 1.0 / 16
g = np.arange(0, 8 + 1e-9, step)

def literal(t, Dmax=8.0):
    # (A) the claim's formula, no validity conditions: h/2 - min{D+ - t/2, D- - t/2, m - t/2, t/2}
    best = None
    for Dp in g[g <= Dmax]:
        for Dm in g[g <= Dmax]:
            m = t  # m <= t, larger m only helps
            e = h / 2 - min(Dp - t / 2, Dm - t / 2, m - t / 2, t / 2)
            if best is None or e < best[0] - 1e-12:
                best = (e, Dp, Dm, m)
    return best

def honest(t, Dmax=8.0):
    # (B) same per-episode accounting as their eq. 8, but the number of episodes N >= 1
    # (log N >= 0) and an episode may use sub-lists a <= DoF+, b <= DoF- (any size).
    # preimages: N + a + b - t >= (h-t)/2 ; cost: N + max(a, b, a+b-m, a+b-t), m = t,
    # plus the floor (h-t)/2 (one compression per preimage, hash-table insert).
    a = g[g <= Dmax][:, None, None]
    b = g[g <= Dmax][None, :, None]
    N = g[None, None, :]
    m = t
    P = N + a + b - t
    ok = P >= (h - t) / 2 - 1e-12
    cost = N + np.maximum(np.maximum(a, b), a + b - m)
    cost = np.maximum(cost, (h - t) / 2)
    cost = np.where(ok, cost, np.inf)
    i = np.unravel_index(np.argmin(cost), cost.shape)
    return float(cost[i]), float(g[i[0]]), float(g[i[1]]), float(g[i[2]])

print("w=32 h=8. Exponents in words; bits = 32*words.")
for t in [4.0]:
    e, Dp, Dm, m = literal(t)
    print(f"(A) literal formula, t={t}: min exponent {e} words = {e*w:.1f} bits at DoF+={Dp} DoF-={Dm} m={m}")
    # what the literal formula says at DoF=4 and DoF=3
    for D in (3.0, 4.0):
        e2 = h / 2 - min(D - t / 2, D - t / 2, t - t / 2, t / 2)
        Ne = (h - t) / 2 - (2 * D - t)   # log of their episode count
        print(f"    literal at DoF+=DoF-={D}, m=4: {e2} words = {e2*w:.0f} bits;"
              f" their episode count (2^w)^{Ne} {'< 1: formula out of range' if Ne < 0 else '>= 1 ok'};"
              f" paper's own condition lambda < h/2=4 {'violated' if D >= h/2 else 'ok'}")
    for Dmax in (3.0, 4.0, 8.0):
        e, a, b, N = honest(t, Dmax)
        print(f"(B) episodes >= 1, sub-lists allowed, DoF+-<= {Dmax}: min {e} words = {e*w:.1f} bits"
              f" (a={a}, b={b}, logN={N})")

print("(D) t sweep under (B), DoF up to 8 words:")
for t in [1.0, 2.0, 8/3, 3.0, 4.0, 5.0]:
    e, a, b, N = honest(t)
    print(f"    t={t:.3f}: {e:.4f} words = {e*w:.1f} bits (a={a}, b={b}, logN={N})")

print("(E) our model, c checks at a two-list join, 2^64 members needed: list exponent")
for c in range(0, 6):
    lists = 1 + c / 2
    print(f"    c={c}: lists 2^{lists*w:.0f} each; total >= max(2^{lists*w+1:.0f} list elements, 2^64 compressions)")
