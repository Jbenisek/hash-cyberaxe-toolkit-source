"""Bit-level guess-and-determine for a ring subsystem (shape_torus, 2026-10-08).

Each 32-bit word is itself a ring Z/w of bits: a rotation is a shift around that ring, an addition is a carry
chain that runs one way (bit 0 -> bit w-1) and so CUTS the bit ring at bit 0.  A word-level ring closure
f(c) = c can be solved by seeding s bits and running around the bit ring; s is what this module estimates.

Input: word-level primitive equations (name, words) in the gd_order.py format, the set of UNKNOWN words
(everything else is known), word size w.  Roles (from the equation name):
  X:a1 / X:a2  out = in1 + in2 + in3       X:c1 / X:c2  out = in1 + in2
  X:d1 R0, X:b1 R1, X:d2 R2, X:b2 R3       out = ROR_R(in1 ^ in2)
  outN                                     w0 ^ w1 = const
Bit variables: word bits, carry bits, temp-word bits.  Bit equations:
  linear (xor of <= 4 bits = known): solves any one unknown;  carry c[i+1] = MAJ(x_i, y_i, c_i): forward only.
Seeds = guessed bits.  Propagation is exact (each step determines one bit uniquely from known ones), so
"seed s bits, propagate, test the unused equations" enumerates every root with 2^s passes.   [DERIVED]
"""
import random

ROT32 = (16, 12, 8, 7)
ROLE_ROT = {"d1": 0, "b1": 1, "d2": 2, "b2": 3}


def rots(w):
    return tuple((r * w) // 32 for r in ROT32)


class BitSystem:
    def __init__(self, eqs, unknown, w):
        self.w = w
        R = rots(w)
        self.var_id = {}
        self.known0 = set()
        self.lin = []      # list of lists of var ids
        self.carry = []    # (out, [in ids])
        self.word_bits = {}
        self.ntmp = 0
        self.pseudo = {}   # tag -> (kind, words) ; K = sum of known addends, T = xor of the two words of an out eq
        self.unknown = set(unknown)

        def wb(word):
            if word not in self.word_bits:
                ids = []
                for i in range(w):
                    ids.append(self._new((word, i)))
                self.word_bits[word] = ids
                if word not in unknown:
                    self.known0.update(ids)
            return self.word_bits[word]

        def known_word(tag):
            ids = [self._new((tag, i)) for i in range(w)]
            self.known0.update(ids)
            return ids

        def add2(x, y, z):
            # z = x + y, bit vectors of ids
            c = [None] * w
            c[0] = self._new(("c0", len(self.carry), self.ntmp))
            self.known0.add(c[0])
            self.ntmp += 1
            for i in range(1, w):
                c[i] = self._new(("c", self.ntmp, i))
            self.ntmp += 1
            for i in range(w):
                self.lin.append([z[i], x[i], y[i], c[i]])
                if i + 1 < w:
                    self.carry.append((c[i + 1], [x[i], y[i], c[i]]))

        for name, vs in eqs:
            if ":" in name:
                role = name.split(":")[1]
            else:
                role = "out"
            if role in ("a1", "a2", "c1", "c2"):
                out, ins = vs[0], list(vs[1:])
                uins = [u for u in ins if u in unknown]
                kins = [u for u in ins if u not in unknown]
                terms = [wb(u) for u in uins]
                if kins:
                    terms.append(known_word(("K", name)))
                    self.pseudo[("K", name)] = ("K", kins)
                o = wb(out)
                if len(terms) == 1:
                    for i in range(w):
                        self.lin.append([o[i], terms[0][i]])
                else:
                    acc = terms[0]
                    for t in terms[1:-1]:
                        tmp = [self._new(("t", self.ntmp, i)) for i in range(w)]
                        self.ntmp += 1
                        add2(acc, t, tmp)
                        acc = tmp
                    add2(acc, terms[-1], o)
            elif role in ROLE_ROT:
                r = R[ROLE_ROT[role]]
                o, a, b = wb(vs[0]), wb(vs[1]), wb(vs[2])
                for i in range(w):
                    j = (i + r) % w
                    self.lin.append([o[i], a[j], b[j]])
            elif role == "out":
                a, b = wb(vs[0]), wb(vs[1])
                kk = known_word(("T", name))
                self.pseudo[("T", name)] = ("T", [vs[0], vs[1]])
                for i in range(w):
                    self.lin.append([a[i], b[i], kk[i]])
            else:
                raise ValueError(name)
        n = len(self.var_id)
        self.n = n
        self.occ_lin = [[] for _ in range(n)]
        for k, e in enumerate(self.lin):
            for v in e:
                self.occ_lin[v].append(k)
        self.occ_car = [[] for _ in range(n)]
        for k, (o, ins) in enumerate(self.carry):
            for v in ins:
                self.occ_car[v].append(k)

    def _new(self, key):
        if key not in self.var_id:
            self.var_id[key] = len(self.var_id)
        return self.var_id[key]

    def propagate(self, known, newly):
        """known: bytearray; newly: list of ids just set.  Returns list of all ids set (including newly)."""
        stack = list(newly)
        setl = list(newly)
        while stack:
            v = stack.pop()
            for k in self.occ_lin[v]:
                e = self.lin[k]
                unk = [u for u in e if not known[u]]
                if len(unk) == 1:
                    u = unk[0]
                    known[u] = 1
                    stack.append(u)
                    setl.append(u)
            for k in self.occ_car[v]:
                o, ins = self.carry[k]
                if not known[o] and all(known[u] for u in ins):
                    known[o] = 1
                    stack.append(o)
                    setl.append(o)
        return setl

    def start(self):
        known = bytearray(self.n)
        init = list(self.known0)
        for v in init:
            known[v] = 1
        # full sweep once
        changed = True
        while changed:
            changed = False
            for e in self.lin:
                unk = [u for u in e if not known[u]]
                if len(unk) == 1:
                    known[unk[0]] = 1
                    changed = True
            for o, ins in self.carry:
                if not known[o] and all(known[u] for u in ins):
                    known[o] = 1
                    changed = True
        return known

    def word_unknown_bits(self, known):
        out = []
        for word, ids in self.word_bits.items():
            for i, v in enumerate(ids):
                if not known[v]:
                    out.append(v)
        return out

    def solve_greedy(self, rng, lookahead=True, pool_words=None):
        """Greedy seeding; returns list of seed ids.  Candidates: unknown word bits (optionally only some words)."""
        known = self.start()
        seeds = []
        while True:
            cand = []
            for word, ids in self.word_bits.items():
                if pool_words is not None and word not in pool_words:
                    continue
                for v in ids:
                    if not known[v]:
                        cand.append(v)
            if not cand:
                # carries/temps left?
                rest = [v for v in range(self.n) if not known[v]]
                if not rest:
                    return seeds
                cand = rest
            if lookahead:
                best, bestg = [], -1
                sample = cand if len(cand) <= 400 else rng.sample(cand, 400)
                for v in sample:
                    kn = bytearray(known)
                    kn[v] = 1
                    g = len(self.propagate(kn, [v]))
                    if g > bestg:
                        best, bestg = [v], g
                    elif g == bestg:
                        best.append(v)
                v = rng.choice(best)
            else:
                v = rng.choice(cand)
            known[v] = 1
            seeds.append(v)
            self.propagate(known, [v])

    def solve_windows(self, words=None):
        """Seed contiguous bits of one word starting at each position; returns (s, word, start)."""
        best = None
        for word, ids in self.word_bits.items():
            if words is not None and word not in words:
                continue
            base = self.start()
            if all(base[v] for v in ids):
                continue
            for st in range(self.w):
                known = bytearray(base)
                s = 0
                for k in range(self.w):
                    v = ids[(st + k) % self.w]
                    if known[v]:
                        continue
                    known[v] = 1
                    s += 1
                    self.propagate(known, [v])
                    if all(known):
                        break
                if all(known) and (best is None or s < best[0]):
                    best = (s, word, st)
        return best

    def solve_multiwindow(self, rng, tries=200, words=None):
        """Random restarts of: pick a word with unknown bits and a start bit, seed upward (skipping known bits)
        until that word is fully known; repeat.  Start bit: random, or the lowest unknown bit, or just above
        a known run.  Returns (s, [(word, start, nseeded), ...]) of the best run."""
        base = self.start()
        best = None
        wl = [wd for wd in self.word_bits if words is None or wd in words]
        for _ in range(tries):
            known = bytearray(base)
            plan, s, sids = [], 0, []
            while not all(known):
                open_words = [wd for wd in wl if not all(known[v] for v in self.word_bits[wd])]
                if not open_words:
                    break
                wd = rng.choice(open_words)
                ids = self.word_bits[wd]
                unk = [i for i in range(self.w) if not known[ids[i]]]
                mode = rng.random()
                if mode < 0.4:
                    st = rng.choice(unk)
                elif mode < 0.7:
                    st = unk[0]
                else:
                    runs = [i for i in unk if known[ids[(i - 1) % self.w]]]
                    st = rng.choice(runs) if runs else rng.choice(unk)
                k0 = s
                for k in range(self.w):
                    v = ids[(st + k) % self.w]
                    if known[v]:
                        continue
                    known[v] = 1
                    s += 1
                    sids.append(v)
                    self.propagate(known, [v])
                    if best is not None and s >= best[0]:
                        break
                    # stop this window early if propagation has started to run on its own
                    if all(known[x] for x in ids):
                        break
                plan.append((wd, st, s - k0))
                if best is not None and s >= best[0]:
                    break
            if all(known) and (best is None or s < best[0]):
                best = (s, plan, sids)
        return best

    def complete(self, seeds):
        known = self.start()
        for v in seeds:
            known[v] = 1
        self.propagate(known, list(seeds))
        return all(known)

    def minimize(self, seed_words, rng, rounds=3, order="random"):
        """Start from all bits of seed_words (a word-level cut set, which always determines everything) and
        drop seeds one at a time while the rest still determines everything.  Returns the smallest seed list."""
        start = [v for wd in seed_words for v in self.word_bits[wd]]
        assert self.complete(start), "word-level cut does not determine the block"
        best = list(start)
        for _ in range(rounds):
            cur = list(start)
            seq = list(cur)
            if order == "random":
                rng.shuffle(seq)
            elif order == "high":
                key = {v: k for k, v in enumerate(cur)}
                seq.sort(key=lambda v: -(key[v] % self.w) + rng.random())
            for v in seq:
                trial = [u for u in cur if u != v]
                if self.complete(trial):
                    cur = trial
            if len(cur) < len(best):
                best = cur
        return best

    def roots(self, seeds, ref):
        """Valued run: ref = dict word -> value of a reference solution (all words of the subsystem).
        Known words take their ref values; enumerate all 2^len(seeds) seed values, propagate, check every
        equation.  Returns (list of root dicts over unknown words, passes)."""
        w, mask = self.w, (1 << self.w) - 1
        base = {}
        for word, ids in self.word_bits.items():
            if word not in self.unknown:
                for i, v in enumerate(ids):
                    base[v] = (ref[word] >> i) & 1
        for tag, (kind, words) in self.pseudo.items():
            val = 0
            if kind == "K":
                for x in words:
                    val = (val + ref[x]) & mask
            else:
                val = ref[words[0]] ^ ref[words[1]]
            for i in range(w):
                base[self.var_id[(tag, i)]] = (val >> i) & 1
        for v in self.known0:
            if v not in base:
                base[v] = 0          # carry-in bits c0
        sols = []
        for sv in range(1 << len(seeds)):
            val = dict(base)
            for k, v in enumerate(seeds):
                val[v] = (sv >> k) & 1
            changed = True
            ok = True
            while changed and ok:
                changed = False
                for e in self.lin:
                    unk = [u for u in e if u not in val]
                    if len(unk) == 1:
                        x = 0
                        for u in e:
                            if u != unk[0]:
                                x ^= val[u]
                        val[unk[0]] = x
                        changed = True
                for o, ins in self.carry:
                    if o not in val and all(u in val for u in ins):
                        val[o] = 1 if sum(val[u] for u in ins) >= 2 else 0
                        changed = True
            if len(val) < self.n:
                raise RuntimeError("seeds do not determine everything")
            for e in self.lin:
                x = 0
                for u in e:
                    x ^= val[u]
                if x:
                    ok = False
                    break
            if ok:
                for o, ins in self.carry:
                    if val[o] != (1 if sum(val[u] for u in ins) >= 2 else 0):
                        ok = False
                        break
            if ok:
                sols.append({wd: sum(val[ids[i]] << i for i in range(w))
                             for wd, ids in self.word_bits.items() if wd in self.unknown})
        return sols, 1 << len(seeds)

    def checks_after(self, seeds):
        """Count bit equations never needed (consistency checks) given the seed set."""
        known = self.start()
        for v in seeds:
            known[v] = 1
        self.propagate(known, list(seeds))
        return all(known)

    def name(self, v):
        for k, i in self.var_id.items():
            if i == v:
                return k
        return None


def selftest():
    # q + ROR8(q ^ A) = T  as a ring: words q (unknown), u = ROR8(q ^ A) (unknown), T known.
    eqs = [("X:d2", ("u", "q", "A")), ("X:c1", ("T", "q", "u"))]
    for w in (8, 16, 32):
        bs = BitSystem(eqs, {"q", "u"}, w)
        rng = random.Random(1)
        best = min(len(bs.solve_greedy(rng)) for _ in range(20))
        print(f"selftest w={w}: q + ROR{rots(w)[2]}(q^A) = T -> greedy seeds {best}, windows {bs.solve_windows()}"
              f", multiwindow {bs.solve_multiwindow(rng)}")
    # b,d pinned: ROR12(b ^ r) ^ (r + D) = K  -> Sol: 12 seeds.  words r, s=ROR12(b^r), z=r+D; s ^ z = K
    eqs = [("X:b1", ("s", "b", "r")), ("X:c1", ("z", "r", "D")), ("out", ("s", "z"))]
    bs = BitSystem(eqs, {"r", "s", "z"}, 32)
    print("selftest b,d pinned (expect 12 or better):", bs.solve_windows(), bs.solve_multiwindow(random.Random(2)))


if __name__ == "__main__":
    selftest()
