"""Paired test: full-class omega hits vs joint passes on a random member sample.

Also: among the 16384 representatives, how many have an alive low-8 omega prefix.
"""
import random
import time
from math import sqrt, log2
import outer

MASK = outer.MASK
Y3 = outer.Y3
KCONST = outer.rol(outer.X15, 8)
FB = outer.CLASS_FREE
raw, t1, t2 = outer.build_tables()

def look(tables, x):
    s = tables[0][x & 255]
    s = tables[1][s + ((x >> 8) & 255)]
    s = tables[2][s + ((x >> 16) & 255)]
    return tables[3][s + ((x >> 24) & 255)]

# Alive low bytes of automaton 2 (S-masked t2): a first byte whose next state
# can still reach a nonzero final mask.
def alive_first_bytes(tables):
    n = [len(t) // 256 for t in tables]
    good = [False] * n[3]
    last = tables[3]
    for s in range(n[3]):
        base = s * 256
        for b in range(256):
            if last[base + b]:
                good[s] = True
                break
    for p in range(2, 0, -1):
        tab = tables[p]
        prev = [False] * (len(tables[p]) // 256)
        for s in range(len(prev)):
            base = s * 256
            for b in range(256):
                if good[tab[base + b] >> 8]:
                    prev[s] = True
                    break
        good = prev
    # stage 0, start state row at index = byte
    alive = []
    tab = tables[0]
    for b in range(256):
        nxt = tab[b] >> 8
        alive.append(1 if good[nxt] else 0)
    return alive

ALIVE = alive_first_bytes(t2)
print("alive low bytes", sum(ALIVE), "of 256")

Y4S = [0] * (1 << 19)
for num in range(1 << 19):
    w = 0
    for n, bit in enumerate(FB):
        if num >> n & 1:
            w |= 1 << bit
    Y4S[num] = ((outer.CLASS_VALUE | w) - Y3) & MASK

def omega(y4, six):
    B, C, D, A, S, U = six
    t1v = ((y4 << 7) | (y4 >> 25)) & MASK
    t1v ^= B
    t2v = (t1v - C) & MASK
    t3 = ((t2v << 8) | (t2v >> 24)) & MASK
    t3 ^= D
    t4 = (t3 - A) & MASK
    t5 = KCONST ^ t4
    t5 = ((t5 << 16) | (t5 >> 16)) & MASK
    t5 ^= S
    return (y4 + t5 + U) & MASK

def scan(six):
    h = pref = 0
    for num, y4 in enumerate(Y4S):
        w = omega(y4, six)
        if look(t2, w):
            h += 1
        if (num & 0x7C00) == 0 and ALIVE[w & 255]:
            pref += 1
    return h, pref

def six_of(eight7):
    v = outer.scalar_outer(list(eight7) + [0])
    B = v["C0.b1"]
    C = v["C0.c1"]
    D = v["C0.d1"]
    A = (B + v["w6"] + v["X4"] + v["w2"]) & MASK
    S = v["S15"]
    U = (Y3 - ((v["S0"] + v["S5"]) & MASK)) & MASK
    return (B, C, D, A, S, U)

def passes(eight7, nums):
    h = 0
    base = list(eight7) + [0]
    for num in nums:
        w = 0
        for b, bit in enumerate(FB):
            if num >> b & 1:
                w |= 1 << bit
        base[7] = w
        v = outer.scalar_outer(base)
        m2 = look(t2, v["omega"])
        if m2 and (look(t1, v["Y9"]) & m2):
            h += 1
    return h

import sys
rng = random.Random(int(sys.argv[1]))
# one random member sample, reused so contexts are comparable
SAMPLE_N = 1 << 15
sample = [rng.randrange(1 << 19) for _ in range(SAMPLE_N)]
pilot = [rng.randrange(1 << 19) for _ in range(1024)]
# expected passes
print("expected passes", SAMPLE_N * 18289159183466496 / 2**64)

CTX = int(sys.argv[2])
rows = []
t0 = time.time()
for c in range(CTX):
    eight7 = [rng.getrandbits(32) for _ in range(7)]
    six = six_of(eight7)
    h, pref = scan(six)
    hp = passes(eight7, sample)
    pil = sum(1 for n in pilot if look(t2, omega(Y4S[n], six)))
    rows.append((h, pref, hp, pil))
    print("c", c, "hits", h, "prefix_reps", pref, "passes", hp, "pilot", pil, flush=True)
print("sec", round(time.time() - t0, 3))

def corr(xs, ys):
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    dx = sqrt(sum((a - mx) ** 2 for a in xs))
    dy = sqrt(sum((b - my) ** 2 for b in ys))
    return (num / (dx * dy) if dx and dy else None), mx, my, (dx / sqrt(n - 1)), (dy / sqrt(n - 1))

hs = [r[0] for r in rows]
ps = [r[1] for r in rows]
qs = [r[2] for r in rows]
c_hp, mh, mp, sh, sp = corr(hs, qs)
c_hpref, _, mpref, _, spref = corr(hs, ps)
print("corr(hits, passes)", c_hp)
print("hit mean/sd", mh, sh, "pass mean/sd", mp, sp, "binomial_sd", sqrt(mp))
print("corr(hits, prefix_reps)", c_hpref, "prefix mean/sd", mpref, spref)
# if we kept the lower half by hits, what fraction of passes and of hits remain
order = sorted(range(CTX), key=lambda i: hs[i])
half = order[: CTX // 2]
print("low-half hit share", sum(hs[i] for i in half) / sum(hs))
print("low-half pass share", sum(qs[i] for i in half) / sum(qs))
print("low-half prefix share", sum(ps[i] for i in half) / sum(ps))
top = order[CTX // 2:]
R = (sum(qs[i] for i in top) / sum(qs)) / 0.5
print("top-half pass share", sum(qs[i] for i in top) / sum(qs), "R", R)
F, V = 0.597, 0.402
print("oracle work ratio", (F / R + V) / (F + V), "bits", -log2((F / R + V) / (F + V)))

pl = [r[3] for r in rows]
po = sorted(range(CTX), key=lambda i: pl[i])
ptop = po[CTX // 2:]
Rp = (sum(qs[i] for i in ptop) / sum(qs)) / 0.5
print("corr(pilot, passes)", corr(pl, qs)[0], "corr(pilot, hits)", corr(pl, hs)[0])
print("pilot top-half pass share", sum(qs[i] for i in ptop) / sum(qs), "Rp", Rp,
      "work ratio", (F / Rp + V) / (F + V), "bits", -log2((F / Rp + V) / (F + V)))
for q in (0.25, 0.125):
    k = max(1, int(CTX * q))
    tq = po[CTX - k:]
    Rq = (sum(qs[i] for i in tq) / sum(qs)) / q
    print("pilot keep", q, "R", Rq, "bits", -log2((F / Rq + V) / (F + V)))
