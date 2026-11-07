"""Bit-level CNF for the family-sampler problem of toy 2-round BLAKE3 (word size w).

Given a target taken from a random message M0 (so a solution exists), find a message M with
  fixedA : E0/E2 inputs equal to M0's (Y0,Y5,Y10,Y15,Y2,Y7,Y8,Y13 and m1,m11,m9,m14)          (12w bits)
  plusA  : effective E0/E2 inputs equal: Y0+m1, Y5, Y10, Y15, m11, Y2+m9, Y7, Y8, Y13, m14       (10w bits)
  outhalfA: out0, out2, out5, out7 equal to M0's                                                  (4w bits)
  fixedB/plusB/outhalfB: the same for E1/E3 (out1,3,4,6)
Optional: --fix k  fixes k random message bits to M0's values (more fixed bits -> fewer solutions);
          --xor k  adds k random parity constraints over message bits (agreeing with M0) to pick a random member.
Writes DIMACS; --check <solver output> decodes the message and verifies with toyb3.
Usage: python cnfgen.py <variant> <w> <seed> <out.cnf> [--fix k] [--xor k] [--check sol.out]
"""
import random
import sys

sys.dont_write_bytecode = True
import toyb3 as T  # noqa: E402


class CNF:
    def __init__(self):
        self.n = 1                      # var 1 = TRUE
        self.cl = [[1]]

    def new(self):
        self.n += 1
        return self.n

    def const(self, val, w):
        return [1 if (val >> i) & 1 else -1 for i in range(w)]

    def word(self, w):
        return [self.new() for _ in range(w)]

    def xor2(self, a, b):
        if abs(a) == 1 and abs(b) == 1:
            return 1 if (a > 0) != (b > 0) else -1
        if abs(a) == 1:
            return -b if a > 0 else b
        if abs(b) == 1:
            return -a if b > 0 else a
        z = self.new()
        self.cl += [[-z, a, b], [-z, -a, -b], [z, -a, b], [z, a, -b]]
        return z

    def xor3(self, a, b, c):
        return self.xor2(self.xor2(a, b), c)

    def maj(self, a, b, c):
        z = self.new()
        self.cl += [[-a, -b, z], [-a, -c, z], [-b, -c, z], [a, b, -z], [a, c, -z], [b, c, -z]]
        return z

    def add(self, x, y):
        w = len(x)
        out, carry = [], -1
        for i in range(w):
            out.append(self.xor3(x[i], y[i], carry))
            if i < w - 1:
                carry = self.maj(x[i], y[i], carry) if carry != -1 else self.and2(x[i], y[i])
        return out

    def and2(self, a, b):
        if a == -1 or b == -1:
            return -1
        if a == 1:
            return b
        if b == 1:
            return a
        z = self.new()
        self.cl += [[-z, a], [-z, b], [z, -a, -b]]
        return z

    def xorw(self, x, y):
        return [self.xor2(a, b) for a, b in zip(x, y)]

    @staticmethod
    def rotr(x, r):
        w = len(x)
        return [x[(i + r) % w] for i in range(w)]

    def eq(self, x, y):
        for a, b in zip(x, y):
            if abs(b) == 1:
                self.cl.append([a if b > 0 else -a])
            elif abs(a) == 1:
                self.cl.append([b if a > 0 else -b])
            else:
                self.cl += [[-a, b], [a, -b]]

    def G(self, a, b, c, d, x, y, R):
        a = self.add(self.add(a, b), x)
        d = self.rotr(self.xorw(d, a), R[0])
        c = self.add(c, d)
        b = self.rotr(self.xorw(b, c), R[1])
        a = self.add(self.add(a, b), y)
        d = self.rotr(self.xorw(d, a), R[2])
        c = self.add(c, d)
        b = self.rotr(self.xorw(b, c), R[3])
        return a, b, c, d


def circuit(C, w, msgv, ecalls=()):
    """Round 0, round-1 columns, and only the round-1 diagonal calls listed in ecalls."""
    R = T.rots(w)
    v = [C.const(x, w) for x in T.init_state(w)]
    res = {}
    for r in range(2):
        s = msgv if r == 0 else [msgv[T.PERM[i]] for i in range(16)]
        for j, idx in enumerate(T.COLS):
            out = C.G(*(v[i] for i in idx), s[2 * j], s[2 * j + 1], R)
            for i, o in zip(idx, out):
                v[i] = o
        if r == 1:
            res["Y"] = v[:]
        for j, idx in enumerate(T.DIAG):
            if r == 1 and j not in ecalls:
                continue
            out = C.G(*(v[i] for i in idx), s[8 + 2 * j], s[9 + 2 * j], R)
            for i, o in zip(idx, out):
                v[i] = o
        if r == 0:
            res["Q"] = v[:]
    res["Z"] = v
    return res


EIN = {0: ((0, 5, 10, 15), (1, 11)), 2: ((2, 7, 8, 13), (9, 14)), 1: ((1, 6, 11, 12), (12, 5)), 3: ((3, 4, 9, 14), (15, 8))}
HALF = {"A": (0, 2), "B": (1, 3)}
OUTW = {"A": (0, 2, 5, 7), "B": (1, 3, 4, 6)}


def generate(variant, w, seed, fixbits=0, nxor=0):
    rng = random.Random(seed)
    mask = (1 << w) - 1
    m0 = [rng.getrandbits(w) for _ in range(16)]
    t0 = T.trace(m0, w)
    C = CNF()
    msgv = [C.word(w) for _ in range(16)]
    base, h = variant[:-1], variant[-1]
    res = circuit(C, w, msgv, HALF[h] if base == "outhalf" else ())
    Y, Z = res["Y"], res["Z"]
    for j in HALF[h]:
        yi, (xi, yy) = EIN[j]
        if base == "fixed":
            for i in yi:
                C.eq(Y[i], C.const(t0["Y"][i], w))
            C.eq(msgv[xi], C.const(m0[xi], w))
            C.eq(msgv[yy], C.const(m0[yy], w))
        elif base == "plus":
            s = C.add(Y[yi[0]], msgv[xi])
            C.eq(s, C.const((t0["Y"][yi[0]] + m0[xi]) & mask, w))
            for i in yi[1:]:
                C.eq(Y[i], C.const(t0["Y"][i], w))
            C.eq(msgv[yy], C.const(m0[yy], w))
    if base == "outhalf":
        for i in OUTW[h]:
            C.eq(C.xorw(Z[i], Z[i + 8]), C.const(t0["out"][i], w))
    bits = [(k, b) for k in range(16) for b in range(w)]
    for k, b in rng.sample(bits, fixbits):
        C.cl.append([msgv[k][b] if (m0[k] >> b) & 1 else -msgv[k][b]])
    for _ in range(nxor):
        sub = [kb for kb in bits if rng.random() < 0.5]
        par = sum((m0[k] >> b) & 1 for k, b in sub) & 1
        lit = -1
        for k, b in sub:
            lit = C.xor2(lit, msgv[k][b])
        C.cl.append([lit if par else -lit])
    return C, msgv, m0, t0


def check(variant, w, m0, t0, msg):
    t = T.trace(msg, w)
    mask = (1 << w) - 1
    base, h = variant[:-1], variant[-1]
    ok = True
    for j in HALF[h]:
        yi, (xi, yy) = EIN[j]
        if base == "fixed":
            ok &= all(t["Y"][i] == t0["Y"][i] for i in yi) and msg[xi] == m0[xi] and msg[yy] == m0[yy]
        elif base == "plus":
            ok &= ((t["Y"][yi[0]] + msg[xi]) & mask) == ((t0["Y"][yi[0]] + m0[xi]) & mask)
            ok &= all(t["Y"][i] == t0["Y"][i] for i in yi[1:]) and msg[yy] == m0[yy]
    if base in ("fixed", "plus", "outhalf"):
        ok &= all(t["out"][i] == t0["out"][i] for i in OUTW[h])
    return ok, msg != m0


def main():
    variant, w, seed, fn = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    fixb = int(sys.argv[sys.argv.index("--fix") + 1]) if "--fix" in sys.argv else 0
    nx = int(sys.argv[sys.argv.index("--xor") + 1]) if "--xor" in sys.argv else 0
    C, msgv, m0, t0 = generate(variant, w, seed, fixb, nx)
    if "--check" in sys.argv:
        solf = sys.argv[sys.argv.index("--check") + 1]
        true = set()
        status = "?"
        for line in open(solf):
            if line.startswith("s "):
                status = line.strip()
            if line.startswith("v "):
                true.update(int(x) for x in line[2:].split() if int(x) > 0)
        if "UNSAT" in status or not true:
            print(f"check {fn}: {status}")
            return
        msg = [sum(1 << b for b in range(w) if msgv[k][b] in true) for k in range(16)]
        ok, new = check(variant, w, m0, t0, msg)
        print(f"check {fn}: {status} verified={ok} differs_from_seed_message={new}")
        return
    with open(fn, "w") as fh:
        fh.write(f"p cnf {C.n} {len(C.cl)}\n")
        for c in C.cl:
            fh.write(" ".join(map(str, c)) + " 0\n")
    print(f"{fn}: vars {C.n} clauses {len(C.cl)}")


if __name__ == "__main__":
    main()
