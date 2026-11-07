"""Bit-level guess-and-determine for the idea-1 systems (main session, Pivot, 2026-10-08; owner's "bigger cube" idea).

The word-level model (gd_order.py) treats each 32-bit word as one unit and needs exactly 4 checks (128 bits) per family
member for the fixed variant.  Here every word is split into its 32 bits, and every modular addition gets its carry
bits.  Structural rules only (no value-dependent shortcuts):
  - xor equations (sum bits, rotated-xor bits, fixed output xors): any one unknown bit is solved from the others;
  - carries: k[i+1] = maj(p[i], q[i], k[i]) is known once its three inputs are known (forward only); k[0] = 0.
A three-term addition z = p + q + x uses an intermediate word t = p + q.
checks (in bits) = guessed bits - family freedom in bits.  A member then costs about 2^checks trials.
Usage: python bit_gd.py <fixed|fixed13|outhalf|outhalf13> <runs> [seed]
"""
import random
import sys

from gd_order import build

W = 32
ROT = {"d1": 16, "b1": 12, "d2": 8, "b2": 7}


class Model:
    def __init__(self):
        self.vid = {}
        self.names = []
        self.xor_eqs = []       # lists of var ids, xor of all = constant
        self.maj_eqs = []       # (out, [in1, in2, in3])
        self.const = set()

    def v(self, name):
        if name not in self.vid:
            self.vid[name] = len(self.names)
            self.names.append(name)
        return self.vid[name]

    def bit(self, word, i):
        return self.v(f"{word}#{i}")

    def add(self, z, p, q):
        """z = p + q with carry word."""
        k = f"k({z})"
        self.const.add(self.bit(k, 0))
        for i in range(W):
            self.xor_eqs.append([self.bit(z, i), self.bit(p, i), self.bit(q, i), self.bit(k, i)])
            if i < W - 1:
                self.maj_eqs.append((self.bit(k, i + 1), [self.bit(p, i), self.bit(q, i), self.bit(k, i)]))

    def rotxor(self, z, p, q, r):
        for i in range(W):
            j = (i + r) % W
            self.xor_eqs.append([self.bit(z, i), self.bit(p, j), self.bit(q, j)])


def build_bits(variant):
    eqs, const, vars_ = build(variant, "len64")
    m = Model()
    for name, vs in eqs:
        if name.startswith("out"):
            for i in range(W):
                m.xor_eqs.append([m.bit(vs[0], i), m.bit(vs[1], i)])
            continue
        role = name.split(":")[1]
        if role in ("a1", "a2"):
            z, p, q, x = vs
            t = f"t({z})"
            m.add(t, p, q)
            m.add(z, t, x)
        elif role in ("c1", "c2"):
            z, p, q = vs
            m.add(z, p, q)
        else:
            z, p, q = vs
            m.rotxor(z, p, q, ROT[role])
    for wname in const:
        for i in range(W):
            if f"{wname}#{i}" in m.vid:
                m.const.add(m.vid[f"{wname}#{i}"])
    freedom_bits = W * (len(vars_) - len(eqs))
    return m, freedom_bits


def run(m, rng):
    n = len(m.names)
    known = bytearray(n)
    for c in m.const:
        known[c] = 1
    occ_x = [[] for _ in range(n)]
    for e, vs in enumerate(m.xor_eqs):
        for v in vs:
            occ_x[v].append(e)
    occ_m = [[] for _ in range(n)]
    for e, (out, ins) in enumerate(m.maj_eqs):
        for v in ins:
            occ_m[v].append(e)
    unk_x = [sum(1 for v in vs if not known[v]) for vs in m.xor_eqs]
    unk_m = [sum(1 for v in ins if not known[v]) for _, ins in m.maj_eqs]
    queue = []

    def learn(v):
        if known[v]:
            return
        known[v] = 1
        queue.append(v)

    def drain():
        while queue:
            v = queue.pop()
            for e in occ_x[v]:
                unk_x[e] -= 1
                if unk_x[e] == 1:
                    for u in m.xor_eqs[e]:
                        if not known[u]:
                            learn(u)
                            break
            for e in occ_m[v]:
                unk_m[e] -= 1
                if unk_m[e] == 0:
                    learn(m.maj_eqs[e][0])

    # constants may already trigger solves
    for e, vs in enumerate(m.xor_eqs):
        if unk_x[e] == 1:
            for u in vs:
                if not known[u]:
                    learn(u)
    for e, (out, ins) in enumerate(m.maj_eqs):
        if unk_m[e] == 0:
            learn(out)
    drain()
    guesses = 0
    while True:
        unknown = [v for v in range(n) if not known[v]]
        if not unknown:
            break
        # candidates: unknown bits in xor equations with exactly two unknowns, and inputs of carries that are one short
        cand = {}
        for e, vs in enumerate(m.xor_eqs):
            if unk_x[e] == 2:
                for u in vs:
                    if not known[u]:
                        cand[u] = cand.get(u, 0) + 1
        for e, (out, ins) in enumerate(m.maj_eqs):
            if unk_m[e] == 1 and not known[out]:
                for u in ins:
                    if not known[u]:
                        cand[u] = cand.get(u, 0) + 2
        if not cand:
            g = rng.choice(unknown)
        else:
            best = max(cand.values())
            pool = [u for u, c in cand.items() if c >= best - rng.choice((0, 0, 1))]
            g = rng.choice(pool)
        guesses += 1
        learn(g)
        drain()
    return guesses


def main():
    variant = sys.argv[1] if len(sys.argv) > 1 else "fixed"
    runs = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    m, freedom = build_bits(variant)
    rng = random.Random(seed)
    res = sorted(run(m, rng) for _ in range(runs))
    print(f"{variant}: {len(m.names)} bit variables, {len(m.xor_eqs)} xor eqs, {len(m.maj_eqs)} carries; "
          f"freedom {freedom} bits; guessed bits best {res[0]} median {res[len(res)//2]} -> "
          f"checks best {res[0] - freedom} bits (word level: 128)")


if __name__ == "__main__":
    main()
