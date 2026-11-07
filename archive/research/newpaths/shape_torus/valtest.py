"""Validate bitgd seeds against brute force on small rings (w=16)."""
import random, sys
sys.dont_write_bytecode = True
from bitgd import BitSystem, rots

def ror(x, r, w):
    m = (1 << w) - 1
    return ((x >> r) | (x << (w - r))) & m if r else x

w = 16; m = (1 << w) - 1; R = rots(w)
rng = random.Random(5)
# ring 1: u = ROR_R2(q ^ A); T = q + u
eqs = [("X:d2", ("u", "q", "A")), ("X:c1", ("T", "q", "u"))]
bs = BitSystem(eqs, {"q", "u"}, w)
s, plan, sids = bs.solve_multiwindow(rng)
bad = 0
for t in range(30):
    q, A = rng.randrange(1 << w), rng.randrange(1 << w)
    u = ror(q ^ A, R[2], w); T = (q + u) & m
    sols, passes = bs.roots(sids, {"q": q, "u": u, "A": A, "T": T})
    got = sorted(x["q"] for x in sols)
    brute = sorted(x for x in range(1 << w) if (x + ror(x ^ A, R[2], w)) & m == T)
    bad += got != brute
print(f"ring q+ROR{R[2]}(q^A)=T, w={w}: seeds {s}, 30 instances, mismatches {bad}")
# ring 2: s = ROR_R1(b ^ r); z = r + D; s ^ z = K
eqs = [("X:b1", ("s", "b", "r")), ("X:c1", ("z", "r", "D")), ("out", ("s", "z"))]
bs = BitSystem(eqs, {"r", "s", "z"}, w)
s, plan, sids = bs.solve_multiwindow(rng)
bad = 0; tot = 0
for t in range(30):
    r, b, D = (rng.randrange(1 << w) for _ in range(3))
    sv = ror(b ^ r, R[1], w); z = (r + D) & m; K = sv ^ z
    sols, passes = bs.roots(sids, {"r": r, "s": sv, "z": z, "b": b, "D": D})
    got = sorted(x["r"] for x in sols)
    brute = sorted(x for x in range(1 << w) if ror(b ^ x, R[1], w) ^ ((x + D) & m) == K)
    bad += got != brute; tot += len(brute)
print(f"ring ROR{R[1]}(b^r)^(r+D)=K, w={w}: seeds {s} plan {plan}, 30 instances, mismatches {bad}, mean roots {tot/30:.2f}")
# ring 3: K0 4-word ring: a1 unknown; d1 = ROR_R0(d ^ a1); c1 = c + d1; b1 = ROR_R1(b ^ c1); a2 = a1 + b1 + y (a2, y known)
for w in (16, 32):
    m = (1 << w) - 1; R = rots(w)
    eqs = [("K:a2", ("a2", "a1", "b1", "y")), ("K:b1", ("b1", "b", "c1")), ("K:c1", ("c1", "c", "d1")), ("K:d1", ("d1", "d", "a1"))]
    bs = BitSystem(eqs, {"a1", "b1", "c1", "d1"}, w)
    s, plan, sids = bs.solve_multiwindow(random.Random(9), tries=200)
    bad = 0; tot = 0; found_ref = 0
    for t in range(20 if w == 16 else 5):
        a1, b, c, d, y = (rng.randrange(1 << w) for _ in range(5))
        d1 = ror(d ^ a1, R[0], w); c1 = (c + d1) & m; b1 = ror(b ^ c1, R[1], w); a2 = (a1 + b1 + y) & m
        sols, passes = bs.roots(sids, {"a1": a1, "b1": b1, "c1": c1, "d1": d1, "a2": a2, "b": b, "c": c, "d": d, "y": y})
        got = sorted(x["a1"] for x in sols)
        found_ref += a1 in got
        if w == 16:
            def f(x):
                dd = ror(d ^ x, R[0], w); cc = (c + dd) & m; bb = ror(b ^ cc, R[1], w)
                return (x + bb + y) & m == a2
            brute = sorted(x for x in range(1 << w) if f(x))
            bad += got != brute; tot += len(brute)
    print(f"K0 ring a2 = a1 + ROR(b ^ (c + ROR(d ^ a1))) + y, w={w}: seeds {s}, reference root found {found_ref}, brute mismatches {bad}")
# ring 4: E0/E2 out ring: ROR_R3(B1 ^ T2 ^ a) ^ ROR_R2(D1 ^ a) = T5
for w in (16, 32):
    m = (1 << w) - 1; R = rots(w)
    eqs = [("E0:b2", ("b2", "b1", "c2")), ("E2:d2", ("d2", "d1", "a2")), ("out2", ("a2", "c2")), ("out5", ("b2", "d2"))]
    bs = BitSystem(eqs, {"b2", "d2", "a2", "c2"}, w)
    s, plan, sids = bs.solve_multiwindow(random.Random(9), tries=200)
    print(f"E0/E2 output ring w={w}: seeds {s} plan {plan}")
