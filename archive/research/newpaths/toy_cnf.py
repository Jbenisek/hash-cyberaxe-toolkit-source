"""Toy 2-round BLAKE3 idea-1 family as CNF+XOR, for measuring how fast a SAT solver produces family members.

Word size w (additions mod 2^w, rotations floor(r*w/32) of (16,12,8,7), low w bits of the IV).  A reference message
defines the fixed targets: m1, m11, m9, m14 and the round-1 column outputs Y0,Y5,Y10,Y15,Y2,Y7,Y8,Y13 (the inputs of E0
and E2), so the family is non-empty; with --special the targets are instead chosen as special values (all zero) and m1,
m11, m9, m14 = 0, which may make the instance unsatisfiable (reported).
The free message bits (12 words) form the sampling set; cryptominisat5 --maxsol N then enumerates distinct members.
Usage: python toy_cnf.py <w> <seed> [--special] [--variant fixed|fixed13]  -> writes toy_w<w>_s<seed>[_sp].cnf
       python toy_cnf.py --verify <cnf> <solver output>   -> recomputes every enumerated member
"""
import random
import sys

IV32 = [0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19]
PERM = [2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8]
COLS = [(0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15)]
DIAG = [(0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14)]
HALF = {"fixed": ((0, 5, 10, 15, 2, 7, 8, 13), (1, 11, 9, 14)), "fixed13": ((1, 6, 11, 12, 3, 4, 9, 14), (12, 5, 15, 8))}


def params(w):
    rots = [r * w // 32 for r in (16, 12, 8, 7)]
    mask = (1 << w) - 1
    iv = [x & mask for x in IV32]
    return rots, mask, iv


def ref_y(w, msg):
    """Reference compression up to the round-1 column outputs."""
    rots, mask, iv = params(w)
    rr = lambda x, r: ((x >> r) | (x << (w - r))) & mask if r else x
    v = iv[:] + iv[:4] + [0, 0, 2 * w, 11 & mask]
    order = list(range(16))
    y = None
    for rnd in range(2):
        s = [msg[order[i]] for i in range(16)]
        for j, (a, b, c, d) in enumerate(COLS + DIAG):
            if rnd == 1 and j >= 4:
                break
            x, yy = s[2 * j], s[2 * j + 1]
            va, vb, vc, vd = v[a], v[b], v[c], v[d]
            va = (va + vb + x) & mask; vd = rr(vd ^ va, rots[0]); vc = (vc + vd) & mask; vb = rr(vb ^ vc, rots[1])
            va = (va + vb + yy) & mask; vd = rr(vd ^ va, rots[2]); vc = (vc + vd) & mask; vb = rr(vb ^ vc, rots[3])
            v[a], v[b], v[c], v[d] = va, vb, vc, vd
        if rnd == 1:
            y = v[:]
        order = [order[p] for p in PERM]
    return y


class CNF:
    def __init__(self):
        self.n = 0
        self.cl = []
        self.xors = []

    def var(self):
        self.n += 1
        return self.n

    def word(self, w):
        return [self.var() for _ in range(w)]

    def const_word(self, val, w):
        bits = self.word(w)
        for i, b in enumerate(bits):
            self.cl.append([b if (val >> i) & 1 else -b])
        return bits

    def xor_eq(self, lits, parity):
        """xor of variables == parity"""
        lits = list(lits)
        if not parity:
            lits[0] = -lits[0]
        self.xors.append(lits)

    def add(self, p, q, w):
        z = self.word(w)
        c = None
        for i in range(w):
            if c is None:
                self.xor_eq([z[i], p[i], q[i]], 0)
            else:
                self.xor_eq([z[i], p[i], q[i], c], 0)
            if i < w - 1:
                k = self.var()
                a, b = p[i], q[i]
                if c is None:          # k = a & b
                    self.cl += [[-k, a], [-k, b], [k, -a, -b]]
                else:                  # k = maj(a, b, c)
                    self.cl += [[-k, a, b], [-k, a, c], [-k, b, c], [k, -a, -b], [k, -a, -c], [k, -b, -c]]
                c = k
        return z

    def rotxor(self, p, q, r, w):
        z = self.word(w)
        for i in range(w):
            j = (i + r) % w
            self.xor_eq([z[i], p[j], q[j]], 0)
        return z


def build(w, seed, special, variant):
    rots, mask, iv = params(w)
    rng = random.Random(seed)
    ref = [rng.getrandbits(w) for _ in range(16)]
    yref = ref_y(w, ref)
    ywords, mwords = HALF[variant]
    if special:
        targets = {i: 0 for i in ywords}
        fixed_m = {i: 0 for i in mwords}
    else:
        targets = {i: yref[i] for i in ywords}
        fixed_m = {i: ref[i] for i in mwords}
    f = CNF()
    msg = [f.const_word(fixed_m[i], w) if i in fixed_m else f.word(w) for i in range(16)]
    init = iv[:] + iv[:4] + [0, 0, (2 * w) & mask, 11 & mask]
    v = [f.const_word(x, w) for x in init]
    order = list(range(16))
    for rnd in range(2):
        s = [msg[order[i]] for i in range(16)]
        for j, (a, b, c, d) in enumerate(COLS + DIAG):
            if rnd == 1 and j >= 4:
                break
            x, yy = s[2 * j], s[2 * j + 1]
            va, vb, vc, vd = v[a], v[b], v[c], v[d]
            va = f.add(f.add(va, vb, w), x, w); vd = f.rotxor(vd, va, rots[0], w)
            vc = f.add(vc, vd, w); vb = f.rotxor(vb, vc, rots[1], w)
            va = f.add(f.add(va, vb, w), yy, w); vd = f.rotxor(vd, va, rots[2], w)
            vc = f.add(vc, vd, w); vb = f.rotxor(vb, vc, rots[3], w)
            v[a], v[b], v[c], v[d] = va, vb, vc, vd
        order = [order[p] for p in PERM]
    for i, val in targets.items():
        for k, b in enumerate(v[i]):
            f.cl.append([b if (val >> k) & 1 else -b])
    free = [b for i in range(16) if i not in fixed_m for b in msg[i]]
    meta = {"w": w, "seed": seed, "special": special, "variant": variant, "msgvars": msg, "fixed_m": fixed_m,
            "targets": targets}
    return f, free, meta


def write(w, seed, special, variant):
    f, free, meta = build(w, seed, special, variant)
    fn = f"toy_{variant}_w{w}_s{seed}{'_sp' if special else ''}.cnf"
    with open(fn, "w") as fh:
        fh.write(f"p cnf {f.n} {len(f.cl) + len(f.xors)}\n")
        fh.write("c ind " + " ".join(map(str, free)) + " 0\n")
        for c in f.cl:
            fh.write(" ".join(map(str, c)) + " 0\n")
        for x in f.xors:
            fh.write("x" + " ".join(map(str, x)) + " 0\n")
    print(fn, f.n, "vars", len(f.cl), "clauses", len(f.xors), "xors", len(free), "free bits")


def verify(cnf, out):
    parts = cnf.replace(".cnf", "").split("_")
    variant, w, seed = parts[1], int(parts[2][1:]), int(parts[3][1:])
    special = cnf.endswith("_sp.cnf")
    _, _, meta = build(w, seed, special, variant)
    sols, cur = [], set()
    for line in open(out):
        if line.startswith("v "):
            for t in line[2:].split():
                t = int(t)
                if t == 0:
                    sols.append(cur)
                    cur = set()
                elif t > 0:
                    cur.add(t)
    good, msgs = 0, set()
    for s in sols:
        msg = [sum(1 << k for k, b in enumerate(word) if b in s) for word in meta["msgvars"]]
        y = ref_y(w, msg)
        ok = all(y[i] == val for i, val in meta["targets"].items()) and all(msg[i] == val for i, val in meta["fixed_m"].items())
        good += ok
        msgs.add(tuple(msg))
    print(f"{cnf}: {len(sols)} solutions, {good} verified, {len(msgs)} distinct messages")


if __name__ == "__main__":
    if sys.argv[1] == "--verify":
        verify(sys.argv[2], sys.argv[3])
    else:
        special = "--special" in sys.argv
        variant = sys.argv[sys.argv.index("--variant") + 1] if "--variant" in sys.argv else "fixed"
        write(int(sys.argv[1]), int(sys.argv[2]), special, variant)
