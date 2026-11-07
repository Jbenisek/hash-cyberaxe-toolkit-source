"""b3-r1c scout: bit-level test of the C-layer lift with kissat.

Planted instance: a random legal 55/63 pair from model.build.  The solver gets the
constants, pins, w4, w13, w14=w15=0 and the 9 E-input words (Y1,Y6,Y12,w12,w5 | Y4,Y9,
Y14,w8) and must find the message words w0,w1,w2,w3,w6,w7,w9,w10,w11 and counter t.
Any solution is a pair with the same E inputs, hence the same residual.
Optional --give NAME,...: also fix those words (message words, S*, X*, or G mids
like K3.a1) to their planted values, to measure how the work scales with the GD peak.

Usage: python lift_sat.py SEED [--give a,b,..] [--time SECONDS]
Writes lift_SEED_<give>.cnf, runs `wsl kissat --time=N`, verifies any model found.
"""
import os, random, subprocess, sys, time
from model import build, rand_params, trace, PIN, W4, W13, IV, ref

HERE = os.path.dirname(os.path.abspath(__file__))


class CNF:
    def __init__(self):
        self.n = 1
        self.cl = [[1]]  # var 1 = TRUE
        self.T = 1

    def new(self):
        self.n += 1
        return self.n

    def const(self, v):
        return [self.T if (v >> i) & 1 else -self.T for i in range(32)]

    def word(self):
        return [self.new() for _ in range(32)]

    def _isc(self, l):
        return abs(l) == self.T

    def xor1(self, a, b):
        if self._isc(a) and self._isc(b):
            return self.T if (a > 0) != (b > 0) else -self.T
        if self._isc(a):
            return -b if a > 0 else b
        if self._isc(b):
            return -a if b > 0 else a
        z = self.new()
        self.cl += [[-z, a, b], [-z, -a, -b], [z, -a, b], [z, a, -b]]
        return z

    def xor(self, A, B):
        return [self.xor1(a, b) for a, b in zip(A, B)]

    def xor3(self, a, b, c):
        return self.xor1(self.xor1(a, b), c)

    def maj(self, a, b, c):
        cs = [l for l in (a, b, c) if self._isc(l)]
        if len(cs) >= 2:
            vals = [l > 0 for l in cs]
            if vals[0] == vals[1]:
                return self.T if vals[0] else -self.T
            rest = [l for l in (a, b, c) if not self._isc(l)]
            return rest[0] if rest else (self.T if sum(l > 0 for l in (a, b, c)) >= 2 else -self.T)
        if len(cs) == 1:
            k = cs[0]
            x, y = [l for l in (a, b, c) if not self._isc(l)]
            z = self.new()
            if k > 0:  # OR
                self.cl += [[-z, x, y], [z, -x], [z, -y]]
            else:  # AND
                self.cl += [[z, -x, -y], [-z, x], [-z, y]]
            return z
        z = self.new()
        self.cl += [[-z, a, b], [-z, a, c], [-z, b, c], [z, -a, -b], [z, -a, -c], [z, -b, -c]]
        return z

    def add(self, A, B):
        out, c = [], -self.T
        for i in range(32):
            out.append(self.xor3(A[i], B[i], c))
            if i < 31:
                c = self.maj(A[i], B[i], c)
        return out

    def eq(self, A, B):
        for a, b in zip(A, B):
            if self._isc(a) and self._isc(b):
                if (a > 0) != (b > 0):
                    self.cl.append([])  # contradiction
            else:
                self.cl += [[-a, b], [a, -b]]


def ror(W, n):
    return [W[(i + n) % 32] for i in range(32)]


def G(f, a, b, c, d, x, y, name, names):
    a1 = f.add(f.add(a, b), x); d1 = ror(f.xor(d, a1), 16); c1 = f.add(c, d1); b1 = ror(f.xor(b, c1), 12)
    a2 = f.add(f.add(a1, b1), y); d2 = ror(f.xor(d1, a2), 8); c2 = f.add(c1, d2); b2 = ror(f.xor(b1, c2), 7)
    for lab, w in zip(("a1", "b1", "c1", "d1"), (a1, b1, c1, d1)):
        names[name + "." + lab] = w
    return a2, b2, c2, d2


CALLS0 = [("K0", (0, 4, 8, 12), (0, 1)), ("K1", (1, 5, 9, 13), (2, 3)), ("K2", (2, 6, 10, 14), (4, 5)),
          ("K3", (3, 7, 11, 15), (6, 7)), ("D0", (0, 5, 10, 15), (8, 9)), ("D1", (1, 6, 11, 12), (10, 11)),
          ("D2", (2, 7, 8, 13), (12, 13)), ("D3", (3, 4, 9, 14), (14, 15))]
CALLS1 = [("C0", (0, 4, 8, 12), (2, 6)), ("C1", (1, 5, 9, 13), (3, 10)), ("C2", (2, 6, 10, 14), (7, 0))]
UNKNOWN = ["w0", "w1", "w2", "w3", "w6", "w7", "w9", "w10", "w11"]
EIN = {"Y1": "Y1", "Y6": "Y6", "Y12": "Y12", "Y4": "Y4", "Y9": "Y9", "Y14": "Y14"}


def encode(wA, t, give):
    T = trace(wA, t, 55)
    f = CNF()
    names = {}
    w = {}
    for i in range(16):
        if ("w%d" % i) in UNKNOWN:
            w[i] = f.word()
        else:
            w[i] = f.const(wA[i])
        names["w%d" % i] = w[i]
    tw = f.word(); names["t"] = tw
    v = [f.const(x) for x in IV] + [f.const(x) for x in IV[:4]] + [tw, f.const(0), f.const(55), f.const(3)]
    for nm, idx, sl in CALLS0:
        o = G(f, *(v[i] for i in idx), w[sl[0]], w[sl[1]], nm, names)
        for i, val in zip(idx, o):
            v[i] = val
        if nm == "K3":
            for i in range(16):
                names["S%d" % i] = v[i]
    for i in range(16):
        names["X%d" % i] = v[i]
    for i in PIN:
        f.eq(v[i], f.const(PIN[i]))
    for nm, idx, sl in CALLS1:
        o = G(f, *(v[i] for i in idx), w[sl[0]], w[sl[1]], nm, names)
        for i, val in zip(idx, o):
            v[i] = val
    for i in range(16):
        if i % 4 != 3:
            names["Y%d" % i] = v[i]
    for k in EIN:
        f.eq(names[k], f.const(T[k]))
    planted = {}
    for g in give:
        val = t if g == "t" else (wA[int(g[1:])] if g.startswith("w") else T[g])
        f.eq(names[g], f.const(val))
        planted[g] = val
    return f, names, T


def main():
    seed = int(sys.argv[1])
    give = []
    tl = 60
    if "--give" in sys.argv:
        give = [x for x in sys.argv[sys.argv.index("--give") + 1].split(",") if x]
    if "--time" in sys.argv:
        tl = int(sys.argv[sys.argv.index("--time") + 1])
    rng = random.Random(seed)
    p = rand_params(rng)
    wA, t, wB = build(p)
    f, names, T = encode(wA, t, give)
    tag = "lift_%d_%s" % (seed, "-".join(g.replace(".", "") for g in give) or "none")
    path = os.path.join(HERE, tag + ".cnf")
    with open(path, "w") as fh:
        fh.write("p cnf %d %d\n" % (f.n, len(f.cl)))
        for c in f.cl:
            fh.write(" ".join(map(str, c)) + " 0\n")
    wpath = 'historical-sources/' + path[3:].replace("\\", "/")
    t0 = time.time()
    r = subprocess.run(["wsl", "-e", "kissat", "--time=%d" % tl, "-q", wpath],
                       capture_output=True, text=True)
    dt = time.time() - t0
    os.remove(path)
    status = "UNKNOWN"
    model = {}
    for line in r.stdout.splitlines():
        if line.startswith("s "):
            status = line[2:].strip()
        elif line.startswith("v "):
            for lit in line[2:].split():
                l = int(lit)
                if l:
                    model[abs(l)] = l > 0
    msg = ""
    if status == "SATISFIABLE":
        def val(W):
            x = 0
            for i, l in enumerate(W):
                bit = (l > 0) if abs(l) == 1 else (model.get(abs(l), False) == (l > 0))
                x |= bit << i
            return x
        w2 = [val(names["w%d" % i]) for i in range(16)]
        t2 = val(names["t"])
        T2 = trace(w2, t2, 55)
        same_e = all(T2[k] == T[k] for k in EIN) and all(w2[i] == wA[i] for i in (5, 8, 12))
        wB2 = list(w2); wB2[4] = wB[4]; wB2[5] = (w2[5] - 8) & 0xFFFFFFFF
        a = ref._compress(IV, w2, t2, 55, 3, 2)[:8]; b = ref._compress(IV, wB2, t2, 63, 3, 2)[:8]
        res = [x ^ y for x, y in zip(a, b)]
        a0 = ref._compress(IV, wA, t, 55, 3, 2)[:8]; b0 = ref._compress(IV, wB, t, 63, 3, 2)[:8]
        res0 = [x ^ y for x, y in zip(a0, b0)]
        msg = "verified: E-inputs equal %s, half-collision %s, residual equal to planted %s, same message %s" % (
            same_e, (res[0] | res[2] | res[5] | res[7]) == 0, res == res0, w2 == list(wA) and t2 == t)
    print("seed=%d give=[%s] vars=%d clauses=%d kissat --time=%d: %s in %.1fs %s" % (
        seed, ",".join(give), f.n, len(f.cl), tl, status, dt, msg))


if __name__ == "__main__":
    main()
