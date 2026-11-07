"""Minimum-weight carry-free colliding characteristic inside the period-K subspace, by SAT (cryptominisat XOR clauses).

Variables: message pattern bits (16 words x K).  Every addition operand pattern bit is an XOR of them; O = alpha|beta
per bit; the output fold is forced to zero; a sequential counter bounds the number of active OR-bits in the chosen
rounds.  Weight of an active bit = 32/K positions, minus 1 for the MSB pattern bit (31 mod K).
Usage: python pksat.py K bound rounds(1|01) out.cnf          -> writes CNF
       python pksat.py K decode rounds sol.txt               -> prints W0, W1 of a solver model
"""
import sys
import numpy as np

K = int(sys.argv[1])
ROT = (16, 12, 8, 7)
PERM = [2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8]
NIN = 16 * K


def ror(vec, r):
    return vec[[(j + r) % K for j in range(K)], :]


adds = []


def add(a, b, rnd):
    adds.append((a.copy(), b.copy(), rnd))
    return a ^ b


def G(a, b, c, d, x, y, rnd):
    t = add(a, b, rnd); a = add(t, x, rnd)
    d = ror(d ^ a, ROT[0]); c = add(c, d, rnd); b = ror(b ^ c, ROT[1])
    t = add(a, b, rnd); a = add(t, y, rnd)
    d = ror(d ^ a, ROT[2]); c = add(c, d, rnd); b = ror(b ^ c, ROT[3])
    return a, b, c, d


def msgword(i):
    m = np.zeros((K, NIN), dtype=np.uint8)
    for j in range(K):
        m[j, i * K + j] = 1
    return m


zero = np.zeros((K, NIN), dtype=np.uint8)
v = [zero.copy() for _ in range(16)]
m = [msgword(i) for i in range(16)]
for rnd in range(2):
    v[0], v[4], v[8], v[12] = G(v[0], v[4], v[8], v[12], m[0], m[1], rnd)
    v[1], v[5], v[9], v[13] = G(v[1], v[5], v[9], v[13], m[2], m[3], rnd)
    v[2], v[6], v[10], v[14] = G(v[2], v[6], v[10], v[14], m[4], m[5], rnd)
    v[3], v[7], v[11], v[15] = G(v[3], v[7], v[11], v[15], m[6], m[7], rnd)
    v[0], v[5], v[10], v[15] = G(v[0], v[5], v[10], v[15], m[8], m[9], rnd)
    v[1], v[6], v[11], v[12] = G(v[1], v[6], v[11], v[12], m[10], m[11], rnd)
    v[2], v[7], v[8], v[13] = G(v[2], v[7], v[8], v[13], m[12], m[13], rnd)
    v[3], v[4], v[9], v[14] = G(v[3], v[4], v[9], v[14], m[14], m[15], rnd)
    m = [m[PERM[i]] for i in range(16)]
out = np.vstack([v[i] ^ v[i + 8] for i in range(8)])
PER, MSB = 32 // K, 31 % K


def weights(x):
    w = [0, 0]
    for a_, b_, r in adds:
        pa = (a_ @ x) % 2
        pb = (b_ @ x) % 2
        o = pa | pb
        w[r] += PER * int(o.sum()) - int(o[MSB])
    return w


if sys.argv[2] == "decode":
    rounds = sys.argv[3]
    lits = " ".join(ln[2:] for ln in open(sys.argv[4]) if ln.startswith("v ")).split()
    val = {}
    for t in lits:
        if t.lstrip("-").isdigit():
            iv = int(t)
            if iv != 0:
                val[abs(iv)] = 1 if iv > 0 else 0
    x = np.array([val.get(i + 1, 0) for i in range(NIN)], dtype=np.uint8)
    assert ((out @ x) % 2 == 0).all(), "not colliding"
    w0, w1 = weights(x)
    pats = [sum(int(x[i * K + j]) << j for j in range(K)) for i in range(16)]
    print(f"K={K} decoded: W0={w0} W1={w1} W={w0 + w1}; message patterns {' '.join('%x' % p for p in pats)}")
    sys.exit(0)

bound = int(sys.argv[2])
rounds = sys.argv[3]
cls, xors = [], []
nv = NIN


def new():
    global nv
    nv += 1
    return nv


def lin(row):
    return [i + 1 for i in np.nonzero(row)[0]]


Os = []
for a_, b_, r in adds:
    if str(r) not in rounds:
        continue
    for j in range(K):
        la, lb = lin(a_[j]), lin(b_[j])
        if not la and not lb:
            continue
        o = new()
        A = B = None
        if la:
            A = new(); xors.append([-A] + la)
        if lb:
            B = new(); xors.append([-B] + lb)
        ins = [z for z in (A, B) if z]
        for z in ins:
            cls.append([-z, o])
        cls.append([-o] + ins)
        Os.append(o)
for row in out:
    l = lin(row)
    if l:
        xors.append([-l[0]] + l[1:])
cls.append(list(range(1, NIN + 1)))
# sequential counter (Sinz): sum(Os) <= bound
n, k = len(Os), bound
if k < n:
    s = [[new() for _ in range(k)] for _ in range(n)]
    cls.append([-Os[0], s[0][0]])
    for j in range(1, k):
        cls.append([-s[0][j]])
    for i in range(1, n):
        cls.append([-Os[i], s[i][0]])
        cls.append([-s[i - 1][0], s[i][0]])
        for j in range(1, k):
            cls.append([-Os[i], -s[i - 1][j - 1], s[i][j]])
            cls.append([-s[i - 1][j], s[i][j]])
        cls.append([-Os[i], -s[i - 1][k - 1]])
with open(sys.argv[4], "w") as f:
    f.write(f"p cnf {nv} {len(cls) + len(xors)}\n")
    for c in cls:
        f.write(" ".join(map(str, c)) + " 0\n")
    for x in xors:
        f.write("x" + " ".join(map(str, x)) + " 0\n")
print(f"K={K} rounds={rounds} active-bit bound {bound}: {len(Os)} OR-bits, {nv} vars, {len(cls)} clauses, {len(xors)} xors")
