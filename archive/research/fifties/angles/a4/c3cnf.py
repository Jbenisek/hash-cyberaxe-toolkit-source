#!/usr/bin/env python3
"""c3cnf.py - CNF for round-1 C3 keeping Y7 and Y15 equal for every length of {55, 63, L3} on the six pin words.

Base message: length 55 with m4 = W4.  Partner of length L: m4_L = ((W4 + K) xor (55 xor L)) - K, K = IV2 + IV6
(exact K2 cancellation, research/impl/outer.py line 40).  C3 = G(X3, X7, X11, X15, m4, W13) (round 1, column 3).
Conditions: b and d outputs (Y7, Y15) of C3 equal for m4 = W4 and m4 = m4_L, for L = 63 and L = L3.
Format constraints: W13 top byte 0 (byte 55 is padding of the 55-byte block); L3 = 47 also needs W13 = 0 (bytes 52..55).
Usage: c3cnf.py gen L3 OUT.cnf [--keep63]   |   c3cnf.py check L3 KISSAT_OUT
  --keep63: also force the (55,63) differences dY3 = fff8ffff and dY11 = fff77ffb of the current pins.
"""
import sys

M = 0xFFFFFFFF
IV = (0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19)
K = (IV[2] + IV[6]) & M
BASE = 55
PINS = ("X3", "X7", "X11", "X15", "W4", "W13")


def ror(v, n):
    return ((v >> n) | (v << (32 - n))) & M


def G(a, b, c, d, x, y):
    a = (a + b + x) & M; d = ror(d ^ a, 16); c = (c + d) & M; b = ror(b ^ c, 12)
    a = (a + b + y) & M; d = ror(d ^ a, 8); c = (c + d) & M; b = ror(b ^ c, 7)
    return a, b, c, d


def m4_of(w4, L):
    return ((((w4 + K) & M) ^ BASE ^ L) - K) & M


class CNF:
    def __init__(self):
        self.n = 0
        self.cl = []

    def var(self):
        self.n += 1
        return self.n

    def word(self):
        return [self.var() for _ in range(32)]

    def xor2(self, a, b):
        if isinstance(a, bool) and isinstance(b, bool):
            return a != b
        if isinstance(a, bool):
            return -b if a else b
        if isinstance(b, bool):
            return -a if b else a
        z = self.var()
        self.cl += [[-z, a, b], [-z, -a, -b], [z, -a, b], [z, a, -b]]
        return z

    def and2(self, a, b):
        if isinstance(a, bool):
            return b if a else False
        if isinstance(b, bool):
            return a if b else False
        z = self.var()
        self.cl += [[-z, a], [-z, b], [z, -a, -b]]
        return z

    def or2(self, a, b):
        if isinstance(a, bool):
            return True if a else b
        if isinstance(b, bool):
            return True if b else a
        z = self.var()
        self.cl += [[z, -a], [z, -b], [-z, a, b]]
        return z

    def maj(self, a, b, c):
        consts = [v for v in (a, b, c) if isinstance(v, bool)]
        if consts:
            lits = [v for v in (a, b, c) if not isinstance(v, bool)]
            if len(consts) >= 2:
                if consts[0] == consts[1]:
                    return consts[0]
                return lits[0] if lits else consts[2]
            return self.or2(*lits) if consts[0] else self.and2(*lits)
        z = self.var()
        self.cl += [[-z, a, b], [-z, a, c], [-z, b, c], [z, -a, -b], [z, -a, -c], [z, -b, -c]]
        return z

    def add(self, x, y):
        out, c = [], False
        for i in range(32):
            out.append(self.xor2(self.xor2(x[i], y[i]), c))
            if i < 31:
                c = self.maj(x[i], y[i], c)
        return out

    def xorw(self, x, y):
        return [self.xor2(a, b) for a, b in zip(x, y)]

    def eq(self, x, y):
        for a, b in zip(x, y):
            if isinstance(a, bool) and isinstance(b, bool):
                if a != b:
                    self.cl.append([])
            elif isinstance(a, bool):
                self.cl.append([b] if a else [-b])
            elif isinstance(b, bool):
                self.cl.append([a] if b else [-a])
            else:
                self.cl += [[a, -b], [-a, b]]


def const(v):
    return [bool(v >> i & 1) for i in range(32)]


def rorw(x, n):
    return [x[(i + n) % 32] for i in range(32)]


def Gw(f, a, b, c, d, x, y):
    a = f.add(f.add(a, b), x); d = rorw(f.xorw(d, a), 16); c = f.add(c, d); b = rorw(f.xorw(b, c), 12)
    a = f.add(f.add(a, b), y); d = rorw(f.xorw(d, a), 8); c = f.add(c, d); b = rorw(f.xorw(b, c), 7)
    return a, b, c, d


def gen(L3, out, keep63, lens=None):
    """lens: the length set (first is the reference; W4 stays the 55-side parameter). Default {55, 63, L3}."""
    f = CNF()
    P = {p: f.word() for p in PINS}
    t = f.add(P["W4"], const(K))
    lens = lens or (55, 63, L3)

    def c3(L):
        tL = [(not b) if isinstance(b, bool) and (BASE ^ L) >> i & 1 else
              (-b if (BASE ^ L) >> i & 1 else b) for i, b in enumerate(t)]
        m4L = P["W4"] if L == BASE else f.add(tL, const((-K) & M))
        return Gw(f, P["X3"], P["X7"], P["X11"], P["X15"], m4L, P["W13"])
    base = c3(lens[0])
    for L in lens[1:]:
        y = c3(L)
        f.eq(base[1], y[1]); f.eq(base[3], y[3])
        if keep63 and L == 63 and lens[0] == 55:
            f.eq(f.add(base[0], const(0xFFF8FFFF)), y[0])
            f.eq(f.add(base[2], const(0xFFF77FFB)), y[2])
    if "--notop" not in sys.argv:
        for i in range(24, 32):
            f.cl.append([-P["W13"][i]])
    if 47 in lens and "--notop" not in sys.argv:
        for i in range(32):
            f.cl.append([-P["W13"][i]])
    if "--fixpins" in sys.argv:   # sanity: the documented pins (outer.py lines 38-39)
        cur = dict(X3=0x29D4FA98, X7=0xBEE3AF28, X11=0x44036000, X15=0x40C58500, W4=0x97475638, W13=0x0007C006)
        for p in PINS:
            for i in range(32):
                f.cl.append([P[p][i] if cur[p] >> i & 1 else -P[p][i]])
    with open(out, "w") as fh:
        fh.write("c pins %s\n" % " ".join("%s:%d" % (p, P[p][0]) for p in PINS))
        fh.write("p cnf %d %d\n" % (f.n, len(f.cl)))
        for c in f.cl:
            fh.write(" ".join(map(str, c)) + " 0\n")
    print("L3=%d vars=%d clauses=%d keep63=%s -> %s" % (L3, f.n, len(f.cl), keep63, out))


def check(L3, kout, cnf):
    first = {}
    for tok in open(cnf).readline().split()[2:]:
        p, v = tok.split(":"); first[p] = int(v)
    status, vals = None, {}
    for line in open(kout):
        if line.startswith("s "):
            status = line[2:].strip()
        elif line.startswith("v "):
            for v in map(int, line[2:].split()):
                if v:
                    vals[abs(v)] = v > 0
    print("L3=%d status=%s" % (L3, status))
    if status != "SATISFIABLE":
        return
    pins = {p: sum(int(vals.get(first[p] + i, False)) << i for i in range(32)) for p in PINS}
    print("pins " + " ".join("%s=%08x" % (p, pins[p]) for p in PINS))
    ys = {}
    for L in (BASE, 63, L3):
        ys[L] = G(pins["X3"], pins["X7"], pins["X11"], pins["X15"], m4_of(pins["W4"], L), pins["W13"])
        print("L=%d m4=%08x Y3=%08x Y7=%08x Y11=%08x Y15=%08x" % ((L, m4_of(pins["W4"], L)) + ys[L]))
    ok = all(ys[L][1] == ys[BASE][1] and ys[L][3] == ys[BASE][3] for L in (63, L3))
    print("verified Y7,Y15 equal for all three lengths:", ok)
    for A, B in ((BASE, 63), (L3, 63), (BASE, L3)):
        print("pair (%d,%d): dY3=%08x dY11=%08x" % (A, B, (ys[B][0] - ys[A][0]) & M, (ys[B][2] - ys[A][2]) & M))


if __name__ == "__main__":
    if sys.argv[1] == "gen":
        gen(int(sys.argv[2]), sys.argv[3], "--keep63" in sys.argv)
    elif sys.argv[1] == "genset":   # genset 55,59 OUT [--notop]
        gen(0, sys.argv[3], False, tuple(int(x) for x in sys.argv[2].split(",")))
    else:
        check(int(sys.argv[2]), sys.argv[3], sys.argv[4])
