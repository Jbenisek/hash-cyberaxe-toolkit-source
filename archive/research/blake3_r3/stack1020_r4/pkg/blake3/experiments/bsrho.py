"""Birthday collision search on 4-round BLAKE3 (blake3-r4-prefix-v1), 256 bit-sliced lanes, distinguished points.  Message = the 32-byte
prefix KEY (m0..m7, advice) || x (m8..m15), one block, IV, flags 11.  Walk g(x) = f(x) XOR q (q = polarities of the generated digest
planes); g(x) = g(y) iff f(x) = f(y).  Credit: pivot full adder and mask walk from 6ae36351, column templates 0 and 1 from 10ce9f59 (text).
"""
import sys
import json
import hashlib
from fractions import Fraction
from math import isqrt, log, exp, expm1, log1p

M32 = 0xFFFFFFFF
IV = (0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19)
ROUNDS = 4                         # rounds of the target (blake3-r4-prefix-v1)
UNIT = 846                          # organizer reference operation cost C of blake3-r4 (222, 430, 638, 846, 1054, 1262, 1470 for 1..7 rounds)
PERM = (2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8)
GCALLS = ((0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15),
          (0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14))
LANES, ALL = 256, (1 << 256) - 1
FLAGS = 11
KEY = [0x80000000, 0, 0x80000000, 0, 0x70000000, 0, 0, 0]   # m0..m7: declared advice (32 bytes), proof 3.7
KEYINT = sum(k << (32 * i) for i, k in enumerate(KEY))


# -------- 1 scalar digest
def _ror(v, k):
    return ((v >> k) | (v << (32 - k))) & M32


def digest_words(m, rounds=ROUNDS, flags=FLAGS, blen=64, counter=0):
    """Compression of the single block m (16 words) with chaining value IV, counter 0, length 64, flags 11 (CHUNK_START|CHUNK_END|ROOT):
    8 digest words v[i] XOR v[i+8], `rounds` rounds (7 for the target)."""
    v = list(IV) + list(IV[:4]) + [counter & M32, counter >> 32, blen, flags]
    m = list(m)
    for _ in range(rounds):
        for j, (a, b, c, d) in enumerate(GCALLS):
            x, y = m[2 * j], m[2 * j + 1]
            v[a] = (v[a] + v[b] + x) & M32
            v[d] = _ror(v[d] ^ v[a], 16)
            v[c] = (v[c] + v[d]) & M32
            v[b] = _ror(v[b] ^ v[c], 12)
            v[a] = (v[a] + v[b] + y) & M32
            v[d] = _ror(v[d] ^ v[a], 8)
            v[c] = (v[c] + v[d]) & M32
            v[b] = _ror(v[b] ^ v[c], 7)
        m = [m[i] for i in PERM]
    return [v[i] ^ v[i + 8] for i in range(8)]


def f_scalar(x, n, key=None):
    """f(x): the low n bits of the digest of the message key (32 bytes, default KEY) || x."""
    key = KEYINT if key is None else key
    kw = [(key >> (32 * i)) & M32 for i in range(8)]
    d = digest_words(kw + [(x >> (32 * i)) & M32 for i in range(8)])
    return sum(d[i] << (32 * i) for i in range(8)) & ((1 << n) - 1)


def message(x):
    return KEYINT.to_bytes(32, "little") + x.to_bytes(32, "little")


# -------- 2 packed tracer (recovery circuit)
PITCH, PLANES7 = 36, 7
REP = sum(1 << (PITCH * i) for i in range(PLANES7))
LIM = 1 << PITCH


class Tracer:
    """Straight-line code over 256-bit words of 7 lanes of 36 bits.  A value is ('c', k) (a constant, folded) or ('v', register, bound);
    every emitted line is one machine operation (add, and, or, xor, shl, shr; constants are immediates)."""

    def __init__(self):
        self.lines, self.ops, self.k = [], 0, 0

    def emit(self, expr):
        self.k += 1
        name = "t%d" % self.k
        self.lines.append("%s=%s" % (name, expr))
        self.ops += 1
        return name

    def mask(self, a):
        return ("v", self.emit("%s&%d" % (a[1], REP * M32)), M32)

    def add(self, *xs):
        c = sum(x[1] for x in xs if x[0] == "c") & M32
        vs = [x for x in xs if x[0] == "v"]
        if not vs:
            return ("c", c)
        acc = vs[0]
        for v in vs[1:]:
            while acc[2] + v[2] >= LIM:
                if acc[2] >= v[2]:
                    acc = self.mask(acc)
                else:
                    v = self.mask(v)
            acc = ("v", self.emit("%s+%s" % (acc[1], v[1])), acc[2] + v[2])
        if c:
            if acc[2] + c >= LIM:
                acc = self.mask(acc)
            acc = ("v", self.emit("%s+%d" % (acc[1], REP * c)), acc[2] + c)
        return acc

    def xor(self, a, b):
        if a[0] == "c" and b[0] == "c":
            return ("c", a[1] ^ b[1])
        if a[0] == "c":
            a, b = b, a
        if b[0] == "c":
            if b[1] == 0:
                return a
            return ("v", self.emit("%s^%d" % (a[1], REP * b[1])), (1 << max(a[2].bit_length(), b[1].bit_length())) - 1)
        return ("v", self.emit("%s^%s" % (a[1], b[1])), (1 << max(a[2].bit_length(), b[2].bit_length())) - 1)

    def ror(self, a, r):
        if a[0] == "c":
            return ("c", _ror(a[1], r))
        s1 = self.emit("%s>>%d" % (a[1], r))
        h = self.emit("%s&%d" % (s1, REP * ((1 << (32 - r)) - 1)))
        s2 = self.emit("%s<<%d" % (a[1], 32 - r))
        lw = self.emit("%s&%d" % (s2, REP * (((1 << r) - 1) << (32 - r))))
        return ("v", self.emit("%s|%s" % (h, lw)), M32)


def build_packed(qw):
    """The recovery circuit for g = f XOR q: the compression of the block KEY || x, then one XOR of each output word with the word of q."""
    tr = Tracer()
    v = [("c", w) for w in IV] + [("c", w) for w in IV[:4]] + [("c", 0), ("c", 0), ("c", 64), ("c", FLAGS)]
    m = [("c", k) for k in KEY] + [("v", "i%d" % i, M32) for i in range(8, 16)]
    for _ in range(ROUNDS):
        for j, (a, b, c, d) in enumerate(GCALLS):
            x, y = m[2 * j], m[2 * j + 1]
            v[a] = tr.add(v[a], v[b], x)
            v[d] = tr.ror(tr.xor(v[d], v[a]), 16)
            v[c] = tr.add(v[c], v[d])
            v[b] = tr.ror(tr.xor(v[b], v[c]), 12)
            v[a] = tr.add(v[a], v[b], y)
            v[d] = tr.ror(tr.xor(v[d], v[a]), 8)
            v[c] = tr.add(v[c], v[d])
            v[b] = tr.ror(tr.xor(v[b], v[c]), 7)
        m = [m[i] for i in PERM]
    out = []
    for i in range(8):
        z = tr.xor(tr.xor(v[i], v[i + 8]), ("c", qw[i]))
        if z[2] > M32:
            z = tr.mask(z)
        out.append(z[1])
    nl = chr(10)
    src = "def batch(%s):" % ",".join("i%d" % i for i in range(8, 16)) + nl
    src += "".join("    %s" % ln + nl for ln in tr.lines) + "    return (%s,)" % ",".join(out) + nl
    ns = {}
    exec(src, {}, ns)
    return ns["batch"], tr.ops


_PACKED = {}


def packed_circuit(qw):
    qw = tuple(qw)
    if qw not in _PACKED:
        _PACKED[qw] = build_packed(qw)
    return _PACKED[qw]


def packed_f(xs, n, qw):
    """g on up to 7 values at once with the packed recovery circuit (g = f XOR q, low n bits; qw = the 8 words of q)."""
    words = [sum(((x >> (32 * i)) & M32) << (PITCH * l) for l, x in enumerate(xs)) for i in range(8)]
    out = packed_circuit(qw)[0](*words)
    mask = (1 << n) - 1
    return [sum(((out[i] >> (PITCH * l)) & M32) << (32 * i) for i in range(8)) & mask for l in range(len(xs))]


# -------- 3 bit-sliced generator
ZERO, ONE = (0, 0), (0, 1)


class Gen:
    """Hash-consed gate network over signals (node, neg): the stored plane is the true plane xor all-ones when neg = 1.
    Node kinds: ('v', j) input plane j, (op, a, b) with op x (xor), a (and), o (or).  calls counts generator primitives."""

    def __init__(self, n):
        self.n, self.nodes, self.memo, self.calls, self.hits = n, [("c",)], {}, 0, 0
        self.inputs = []
        for j in range(n):
            self.nodes.append(("v", j))
            self.inputs.append((len(self.nodes) - 1, 0))

    def mk(self, op, a, b):
        self.calls += 1
        if a > b:
            a, b = b, a
        k = (op, a, b)
        if k in self.memo:
            self.hits += 1                                   # a shared gate (none at this target: see selftest)
        else:
            self.nodes.append(k)
            self.memo[k] = len(self.nodes) - 1
        return self.memo[k]

    def XOR(self, x, y):
        self.calls += 1
        if x[0] == 0:
            return (y[0], y[1] ^ x[1])
        if y[0] == 0:
            return (x[0], x[1] ^ y[1])
        if x[0] == y[0]:
            return (0, x[1] ^ y[1])
        return (self.mk("x", x[0], y[0]), x[1] ^ y[1])

    def AND(self, x, y):
        self.calls += 1
        if x[0] == 0:
            return ZERO if x[1] == 0 else y
        if y[0] == 0:
            return ZERO if y[1] == 0 else x
        if x[0] == y[0]:
            return x if x[1] == y[1] else ZERO
        if x[1] == 0 and y[1] == 0:
            return (self.mk("a", x[0], y[0]), 0)
        if x[1] == 1 and y[1] == 1:
            return (self.mk("o", x[0], y[0]), 1)           # !a & !b = !(a | b)
        p, q = (x, y) if x[1] == 0 else (y, x)               # p positive, q negative: p & !qn = p ^ (p & qn)
        return self.XOR(p, (self.mk("a", p[0], q[0]), 0))

    def fa(self, a, b, c):
        """(sum, carry) of a + b + c by the pivot rule of 6ae36351: p = the plane whose polarity differs, u = x ^ p, sum = u ^ y,
        carry = (u & (y ^ p)) ^ p, 5 gates.  One constant k: sum = x ^ y ^ k, carry x & y (k = 0) or x | y (k = 1), 2 gates; two fold."""
        ops = (a, b, c)
        cs = [t for t in ops if t[0] == 0]
        vs = [t for t in ops if t[0] != 0]
        k = 0
        for t in cs:
            k ^= t[1]
        if len(vs) == 3:
            for pi in range(3):
                o = [vs[j] for j in range(3) if j != pi]
                if o[0][1] == o[1][1]:
                    p, x, y = vs[pi], o[0], o[1]
                    break
            u = self.XOR(x, p)
            return self.XOR(u, y), self.XOR(self.AND(u, self.XOR(y, p)), p)
        if len(vs) == 2:
            x, y = vs
            t = self.XOR(x, y)
            s = (t[0], t[1] ^ k)
            if x[1] == y[1]:
                if k == 0:
                    return s, self.AND(x, y)
                cr = self.AND((x[0], x[1] ^ 1), (y[0], y[1] ^ 1))
                return s, (cr[0], cr[1] ^ 1)
            nt = (t[0], t[1] ^ 1)
            xx = x if x[1] == nt[1] else y
            if k == 0:
                return s, self.AND(xx, nt)
            yy = x if x[1] == t[1] else y                    # k = 1, opposite polarities: carry = yy OR (x XOR y), 2 gates
            cr = self.AND((yy[0], yy[1] ^ 1), (t[0], t[1] ^ 1))
            return s, (cr[0], cr[1] ^ 1)
        if len(vs) == 1:
            x = vs[0]
            k1, k2 = cs[0][1], cs[1][1]
            return (x[0], x[1] ^ k), (ONE if k1 == k2 == 1 else ZERO if k1 == k2 == 0 else x)
        kk = cs[0][1] + cs[1][1] + cs[2][1]
        return (ZERO if kk % 2 == 0 else ONE), (ONE if kk >= 2 else ZERO)

    def OR(self, x, y):
        r = self.AND((x[0], x[1] ^ 1), (y[0], y[1] ^ 1))
        return (r[0], r[1] ^ 1)

    def _col(self, x, y, z, u, U, tm, oU):
        """One column of a three-addend sum: bits x, y, z and the carry pair (u, U) = U ? 1 : 2u; returns (sum, u', U') with
        x + y + z + c = s + 2 c'.  Template 0 or 1 (9 gates), or tm = 2: the COLLIB circuit of the stored polarities of the five
        inputs.  oU (bit 30): u' is not built."""
        X, A, O = self.XOR, self.AND, self.OR
        ins = (x, y, z, u, U); key = (sum(t[1] << i for i, t in enumerate(ins)), int(oU))
        if tm == 2 and key not in COLLIB:
            tm = 0
        if tm == 2:
            g, o = COLLIB[key]
            nd = [(t[0], 0) for t in ins]
            for op, i, j in g:
                nd.append({'x': X, 'a': A, 'o': O}[op](nd[i], nd[j]))
            r = [None if (str(k) not in o) else (nd[o[str(k)][0]][0], nd[o[str(k)][0]][1] ^ o[str(k)][1]) for k in (0, 1, 2)]
            return r[0], r[1], r[2]
        if tm:
            w = X(y, U); n8 = X(z, w); s = X(x, n8); n6 = O(U, X(y, u))
            return s, (None if oU else X(n6, w)), X(n6, A(n8, X(x, w)))
        n5 = X(z, U); n9 = X(x, n5); s = X(y, n9); n6 = X(x, y); n8 = O(U, X(z, u)); n11 = A((n6[0], n6[1] ^ 1), n9)
        return s, (None if oU else X(n5, n11)), X(n8, n11)

    def add3(self, A, B, C):
        """A + B + C in one ripple of carry pairs: bit 0 is a full adder (its carry is the pair (0, k)); for each bit 1..30 the six addend
        orders and three column forms are built as dry trials (nodes removed again) and the one with fewest new gates is kept."""
        s = [None] * 32
        s[0], U = self.fa(A[0], B[0], C[0])
        u = ZERO
        for i in range(1, 31):
            a, b, c, best = A[i], B[i], C[i], None
            for o in ((a, b, c), (a, c, b), (b, a, c), (b, c, a), (c, a, b), (c, b, a)):
                for tm in (0, 1, 2):
                    n0, h0 = len(self.nodes), self.hits
                    self._col(*o, u, U, tm, i == 30)
                    k = len(self.nodes) - n0
                    for nd in self.nodes[n0:]:
                        del self.memo[nd]
                    del self.nodes[n0:]
                    self.hits = h0
                    if best is None or k < best[0]:
                        best = (k, o, tm)
            s[i], u, U = self._col(*best[1], u, U, best[2], i == 30)
        s[31] = self.XOR(self.XOR(self.XOR(A[31], B[31]), C[31]), U)
        return s

    def add(self, A, B):
        """Ripple add of two 32-plane words, carry out of bit 31 dropped (full adders by `fa`)."""
        s, c = [], ZERO
        for i in range(32):
            if i == 31:
                s.append(self.XOR(self.XOR(A[i], B[i]), c))
            else:
                si, c = self.fa(A[i], B[i], c)
                s.append(si)
        return s

    def xorw(self, A, B):
        return [self.XOR(a, b) for a, b in zip(A, B)]


# exact-synthesis columns (AND, OR, XOR of stored planes): key = (input polarities x|y<<1|z<<2|u<<3|U<<4, oU); gate (op, i, j) over
# nodes 0..4 = x, y, z, u, U and the earlier gates; outputs k: (node, polarity flip) for s, u', U'
COLLIB = {(16, 0): ([['x', 0, 4], ['x', 1, 5], ['x', 1, 2], ['x', 3, 5], ['o', 6, 7], ['x', 2, 6], ['a', 4, 8], ['x', 5, 9], ['x', 9, 11]], {'0': [10, 1], '1': [12, 0], '2': [13, 0]}), (16, 1): ([['x', 1, 4], ['x', 3, 5], ['x', 0, 2], ['x', 2, 5], ['o', 7, 8], ['a', 4, 6], ['x', 0, 8], ['x', 9, 10]], {'0': [11, 1], '2': [12, 0]}), (7, 0): ([['x', 0, 2], ['x', 1, 5], ['x', 3, 6], ['x', 0, 1], ['o', 4, 7], ['o', 5, 8], ['x', 6, 9], ['x', 9, 10], ['x', 4, 6]], {'0': [13, 1], '1': [11, 0], '2': [12, 1]}), (7, 1): ([['x', 1, 2], ['x', 0, 5], ['x', 0, 1], ['o', 5, 7], ['x', 4, 6], ['x', 3, 9], ['o', 4, 10], ['x', 8, 11]], {'0': [9, 1], '2': [12, 1]})}


def _ror_planes(A, r):
    return [A[(i + r) % 32] for i in range(32)]


def _constw(v):
    return [ONE if (v >> i) & 1 else ZERO for i in range(32)]


def used_gates(g, out):
    """The gates that some output uses, in creation order."""
    seen = set(o[0] for o in out)
    for k in range(len(g.nodes) - 1, 0, -1):
        if k in seen and g.nodes[k][0] in "xao":
            seen.add(g.nodes[k][1])
            seen.add(g.nodes[k][2])
    return [k for k in range(1, len(g.nodes)) if k in seen and g.nodes[k][0] in "xao"]


def trace(n, key=None):
    """The network of the digest of the block KEY || x (IV, flags 11), x = the low n bits of the input planes (planes >= n are 0).  Input planes
    are upright; output plane j is the signal (node, neg), stored value = digest plane XOR neg.  a + b + m is one three-addend ripple when all
    96 planes are variable, else two two-addend ripples (constants fold)."""
    g = Gen(n)

    def s3(A, B, C):
        if all(p[0] != 0 for W in (A, B, C) for p in W):
            return g.add3(A, B, C)
        return g.add(g.add(A, B), C)
    zero = _constw(0)
    m = [_constw(k) for k in (key or KEY)] + [[g.inputs[32 * i + b] if 32 * i + b < n else ZERO for b in range(32)] for i in range(8)]
    v = [_constw(w) for w in IV] + [_constw(w) for w in IV[:4]] + [zero, zero, _constw(64), _constw(FLAGS)]
    for _ in range(ROUNDS):
        for j, (a, b, c, d) in enumerate(GCALLS):
            x, y = m[2 * j], m[2 * j + 1]
            v[a] = s3(v[a], v[b], x)
            v[d] = _ror_planes(g.xorw(v[d], v[a]), 16)
            v[c] = g.add(v[c], v[d])
            v[b] = _ror_planes(g.xorw(v[b], v[c]), 12)
            v[a] = s3(v[a], v[b], y)
            v[d] = _ror_planes(g.xorw(v[d], v[a]), 8)
            v[c] = g.add(v[c], v[d])
            v[b] = _ror_planes(g.xorw(v[b], v[c]), 7)
        m = [m[i] for i in PERM]
    return g, [s for i in range(8) for s in g.xorw(v[i], v[i + 8])]      # output plane 32 i + b


class Step:
    """The straight-line step for width n: n upright input planes -> the n output planes as stored (digest plane j XOR q_j, q_j the
    polarity of the generated signal); fed back as they are, so the chain is x -> g(x) = f(x) XOR q.  ops = gates."""

    def __init__(self, n=256):
        g, out = trace(n)
        self.n, self.pin, self.gen_calls, self.hits = n, [0] * n, g.calls, g.hits
        assert all(out[j][0] != 0 for j in range(n))
        self.q = [out[j][1] for j in range(n)]
        self.qint = sum(b << j for j, b in enumerate(self.q))
        self.qwords = [(self.qint >> (32 * i)) & M32 for i in range(8)]
        order = used_gates(g, out[:n])
        names, lines, self.lines, self.by, self.opsym = {0: "0"}, [], [], {}, {}
        for j, (nid, _) in enumerate(g.inputs):
            names[nid] = "i%d" % j
        sym = {"x": "^", "a": "&", "o": "|"}
        for k in order:
            op, a, b = g.nodes[k]
            names[k] = "t%d" % k
            lines.append("%s=%s%s%s" % (names[k], names[a], sym[op], names[b]))
            self.lines.append((names[k], names[a], names[b]))
            self.opsym[names[k]] = (sym[op], False)
            self.by[op] = self.by.get(op, 0) + 1
        self.gates = len(order)
        self.dead = len(g.nodes) - 1 - n - len(order)           # gates built that no output uses
        outs = [names[out[j][0]] for j in range(n)]
        self.ops, self.outs = self.gates, outs
        nl, K, live, lu = chr(10), 2000, ["i%d" % j for j in range(n)], {}
        for k, (_, a, b) in enumerate(self.lines):
            lu[a] = lu[b] = k
        for o in outs:
            lu[o] = len(lines)
        self.fns = []                                         # compiled in chunks of K lines (a single 46,000-line function needs 100 MB to compile)
        for s0 in range(0, len(lines), K):
            e0 = min(s0 + K, len(lines))
            nxt = [v for v in live + [d for d, _, _ in self.lines[s0:e0]] if lu.get(v, -1) >= e0]
            src = "def c(%s):" % ",".join(live) + nl + "".join("    %s" % ln + nl for ln in lines[s0:e0]) + "    return (%s,)" % ",".join(outs if e0 == len(lines) else nxt) + nl
            ns = {}
            exec(compile(src, "<bitslice-step-n%d>" % n, "exec"), {}, ns)
            self.fns.append(ns["c"])
            live = nxt
        self.step = self._chain

    def _chain(self, *x):
        for f in self.fns:
            x = f(*x)
        return x

    def _last(self):
        last = {}
        for k, (_, a, b) in enumerate(self.lines):
            for v in (a, b):
                last[v] = k
        return last

# -------- 4 register allocation
def allocate(st):
    """Registers: input and output plane j in register j (no moves); temporaries take the lowest free register above n.
    Returns ((op, dst, a, b) per instruction, registers used); raises if output j is written while input j is still needed."""
    import heapq
    n, last, free, nxt = st.n, st._last(), [], st.n
    reg = {"i%d" % j: j for j in range(n)}
    outpin = {nm: j for j, nm in enumerate(st.outs)}
    code, top = [], n
    for k, (nm, a, b) in enumerate(st.lines):
        ra, rb = reg.get(a, -1), reg.get(b, -1)
        for v in {a, b}:
            if v in reg and last.get(v, -1) == k and v not in outpin:
                if reg[v] >= n:
                    heapq.heappush(free, reg[v])
        if nm in outpin:
            j = outpin[nm]
            if last.get("i%d" % j, -1) > k:
                raise ValueError("input %d still live when output %d is produced" % (j, j))
            reg[nm] = j
        elif free:
            reg[nm] = heapq.heappop(free)
        else:
            reg[nm] = nxt
            nxt += 1
        top = max(top, reg[nm] + 1)
        code.append((nm, reg[nm], ra, rb))
    return code, top


def run_allocated(st, code, planes):
    """Execute the allocated code on a register file; returns the first n registers (the next input planes)."""
    regs = [0] * (max(c[1] for c in code) + 1)
    regs[:st.n] = planes
    for (nm, d, ra, rb) in code:
        va = regs[ra] if ra >= 0 else 0
        vb = ALL if st.opsym[nm][1] else (regs[rb] if rb >= 0 else 0)
        o = st.opsym[nm][0]
        regs[d] = va ^ vb if o == "^" else (va & vb if o == "&" else va | vb)
    return regs[:st.n]


# -------- lane transposition, packing, extraction
def _tmasks():
    res, s = {}, 128
    while s:
        m = 0
        for c in range(256):
            if not c & s:
                m |= 1 << c
        res[s] = m
        s >>= 1
    return res


_TM = _tmasks()


def transpose(rows):
    """Transpose a 256 x 256 bit matrix given as 256 integers of 256 bits (bit c of rows[i] = element (i, c))."""
    R = list(rows) + [0] * (256 - len(rows))
    s = 128
    while s:
        m = _TM[s]
        for i in range(256):
            if not i & s:
                t = ((R[i] >> s) ^ R[i + s]) & m
                R[i + s] ^= t
                R[i] ^= t << s
        s >>= 1
    return R


def pack_lanes(xs, n, pin):
    """Stored input planes (low n) for up to 256 lane values."""
    T = transpose(xs)
    return [T[j] ^ (ALL if pin[j] else 0) for j in range(n)]


def lanes_of(planes, n, pin):
    """All 256 lane values (n bits) from n stored planes."""
    T = transpose([planes[j] ^ (ALL if pin[j] else 0) for j in range(n)])
    return T[:256]


def lane_value(planes, l, pin, n):
    x = 0
    for j in range(n):
        x |= (((planes[j] >> l) & 1) ^ pin[j]) << j
    return x


def set_lane(planes, l, x, pin, n):
    bit = 1 << l
    return [(planes[j] & ~bit) | ((((x >> j) & 1) ^ pin[j]) << l) for j in range(n)]


# -------- 5 plan and ledger
LAMBDA = Fraction(497, 1000)       # n = 18 plan: 1 - exp(-LAMBDA) = 0.39165
CUTLOSS = Fraction(15, 100000)     # n = 18 plan: allowance for cut-trail points, as a fraction of Q
P_MIN = 0.390000001                # plan target; Appendix A proves P_F >= 0.39 exactly
GRAIN = 10 ** 24                   # B is a multiple of GRAIN
CMAX = 1                           # halt when more than CMAX trails are cut
STAGE1_PLANES, SC = 32, 12         # stage-1 planes; the AND of the first SC planes is tested first (proof 3.3)
# machine charges (proof 3.3)
LOOP_OPS = 1                       # batch counter increment
LIMIT_OPS = 2                      # passing batch: counter vs next limit, branch
DELAY_MAX = 3000                   # limits act at the next passing batch, <= DELAY_MAX late (proof 4, Step 7)
PASS_SLACK = Fraction(1, 1024)     # pmax = ceil((1 + PASS_SLACK) B P_SC) + 64
HIT_OPS = 2800                     # a stage-1 hit lane
EVENT_OPS = 3800                   # a finished trail, besides the table walk
SLOT_OPS = 64                      # table walk per finished trail and per slot (a lookup visits <= 3 S slots at 12, an insertion moves <= S at 24)
CUT_OPS = 4200                     # a cut trail
SLICE_OPS = 1300                   # slice check: 256 ages
KR, KCHK = Fraction(62, 5), 8192   # recovery: pass-1 cap c_r = ceil(12.4 L) steps; at most 8192 checkpoints per trail
REC1_OPS, REC2_OPS = 38, 39        # per recovery batch beyond the packed circuit: pass 1 (35 + checkpoint counter 3), pass 2 (39)
CHK_OPS, PROBE_OPS, REC_FIXED = 80, 100, 600   # a stored checkpoint pair; a bisection probe besides its walk; call and setup
INSTR_BYTES = 9                    # other instructions: opcode, 3 registers, 32-bit immediate
IMM_INSTR, IMM_BYTES = 64, 37      # at most 64 of them with a 256-bit immediate
GEN_INSTR_BYTES = 36               # per wasm instruction of the generator image
GATE_BYTES = 5                     # one register-only gate (^ & |): 8-bit opcode + three 10-bit register numbers (800 registers < 1024)
GEN_CODE = 2149                    # wasm instructions of GEN_C (clang -Os, llvm-objdump -d), GEN_INSTR_BYTES each
GEN_CONST = 256                    # constant tables of GEN_C (IV 32, KEY 32, PERM 16, GC 32, LIB 144), bytes
HANDLER_CODE, SETUP_CODE, RECOVERY_CODE = 1060, 160, 110   # instructions: handlers 1,000 + table walk 60; setup, cut, slice; recovery besides its circuit
STAGE1_CODE = 4                    # stage-1 branches 2, limit compare and branch 2
REGISTERS = 775                    # declared register file (773 + counter + limit), counted as memory
REGFILE = REGISTERS * 32
COUNTERS = 5248                    # trail numbers 1024, births 4096, counters 128
ENTRY, TBITS, META = 7, 18, 3      # table slot, 56 bits: key remainder, 18-bit trail number, 3 quotient-filter bits (proof 7)
MEM_LIMIT = 1048576                # bytes: 2^20
SPARE = 64                         # bytes under the limit outside tmax slots (the table's extra slot is taken from them)
ADVICE = 32                        # nonuniform advice: the prefix KEY
KEY_OPS = 17750836600              # offline choice of KEY: 241 evaluations, charged (python3 bsrho.py --choose-key, proof 3.7)
TAIL_LOG2 = -40
KAPPA_256 = 20
GEN_FACTOR = 200                   # word operations charged per generator primitive call and per emitted line
GEN_STATE = 2400                   # generator state words (v 2,048, tmp and mw 128 each, free-register bitmap 96)
GEN_STACK = 2048                   # shadow stack of the generator
GEN_INFO = 68                      # result record of the generator
SETUP_FIXED = 256 * 3100 + 20000   # 256 starts inserted in memory, reloaded, random word, counters
CFG = {18: dict(s1=2, W=0, Tp=1, kappa=12, Sb=4),
       256: dict(s1=32, W=90, kappa=KAPPA_256, Sb=1 << 48)}


def stage1_ops(s1):
    """(per batch, extra per passing batch): k - 1 ANDs and a branch on zero; s1 - k ANDs, a branch, LIMIT_OPS."""
    k = min(SC, s1)
    return k - 1 + 1, s1 - k + 1 + LIMIT_OPS


def stage1(planes, p, cnt):
    """None (not passing) or the mask of the lanes with the s1 low bits all ones; passing batches are budgeted (pmax)."""
    k, acc = min(SC, p["s1"]), planes[0]
    for j in range(1, k):
        acc &= planes[j]
    if acc == 0:
        return None
    cnt["passing"] += 1
    if cnt["passing"] > p["pmax"]:
        raise Halt("stage-1 checkpoint budget")
    for j in range(k, p["s1"]):
        acc &= planes[j]
    return acc


def keybits(tmax):
    """Key bits of an entry: the 36 stored remainder bits plus the l = floor(log2(tmax + 1)) quotient bits the slot implies."""
    return 8 * ENTRY - TBITS - META + (tmax + 1).bit_length() - 1


INFLIGHT = 350                     # n = 18 plan only (sum of 256 exponential ages, units of L)


def _plan(n, Tp, kappa, tmax, Sb):
    c = CFG[n]
    s1, W = c["s1"], c["W"]
    N, D = 1 << n, s1 + W
    L = Fraction(1 << D, Tp)
    if n == 256:
        assert LANES + tmax + CMAX < 1 << TBITS and KCHK * 64 <= ENTRY * (tmax + 1)   # trail numbers fit; checkpoints fit in the table region
        B = _b256(Tp, tmax, kappa, Sb)
    else:                                                     # reduced widths: the plan of the 18-bit experiment
        ureq = isqrt(2 * N * LAMBDA.numerator // LAMBDA.denominator) + 2
        num, den = ureq + INFLIGHT * L + 1, CUTLOSS.denominator
        q = -(-(num * den) // (den - CUTLOSS.numerator))
        B = -(-q // LANES)
    cc = -(-kappa * L.numerator // L.denominator)
    fb = (Tp - 1).bit_length()
    pk = 1 - Fraction((1 << SC) - 1, 1 << SC) ** LANES           # P(a batch passes the first SC planes), 256 uniform lanes
    big = n == 256
    return dict(n=n, s1=s1, W=W, D=D, Tp=Tp, fb=fb, kb=min(keybits(tmax) - fb, n - D), L=L, N=N, Q=B * LANES, B=B, kappa=kappa, Sb=Sb,
                c=cc, capr=cc + Sb, cr=-(-(KR * L.numerator) // L.denominator) if big else cc + Sb, tmax=tmax,
                e2max=2 * B * LANES // (1 << s1) + 64, pmax=-(-((1 + PASS_SLACK) * B * pk).numerator // ((1 + PASS_SLACK) * B * pk).denominator) + 64 if big else 10 ** 9,
                cmax=CMAX if big else 10 ** 9)


def tail_log2(mean, k):
    """log2 of the Chernoff bound exp(-mean) (e mean / k)^k on P(count >= k), k > mean."""
    return (-mean + k * (1 + log(mean / k))) / log(2)


_STEP256 = {}


def step256():
    if 256 not in _STEP256:
        _STEP256[256] = Step(256)
    return _STEP256[256]


def machine_constants(st=None):
    """(PH, per-batch stage 1, passing extra, BODY, code bytes, tmax) of the n = 256 program."""
    st = st or step256()
    ph = st.ops
    per, rest = stage1_ops(STAGE1_PLANES)
    body = ph + per + LOOP_OPS
    code = (ph + STAGE1_PLANES - 1 + packed_circuit(st.qwords)[1]) * GATE_BYTES + (
        body - ph - per + STAGE1_CODE + HANDLER_CODE + SETUP_CODE + RECOVERY_CODE) * INSTR_BYTES + IMM_INSTR * (IMM_BYTES - INSTR_BYTES)
    tmax = (MEM_LIMIT - SPARE - code - REGFILE - COUNTERS - ADVICE) // ENTRY
    return ph, per, rest, body, code, tmax


def gen_scratch(nodes=None):
    """Scratch bytes of GEN_C: 8-bit use counts (one byte per node of the n = 256 network), state, constants, shadow stack, result record."""
    nodes = nodes or len(trace(256)[0].nodes)
    uses = nodes + 1
    return uses + GEN_STATE + GEN_CONST + GEN_STACK + GEN_INFO, uses, nodes


def phase_bytes(code, tmax):
    """(setup phase, search phase) resident bytes.  Setup: code, advice, counters, the generator's image and scratch.  Search: code, advice,
    counters, register file and the table of tmax + 1 slots; the generator's image and scratch are overwritten by the table and registers."""
    return code + ADVICE + COUNTERS + GEN_CODE * GEN_INSTR_BYTES + gen_scratch()[0], code + ADVICE + COUNTERS + REGFILE + ENTRY * (tmax + 1)


def plan(n, kappa=None, Tp=None):
    if n != 256:
        c = CFG[n]
        p = _plan(n, c["Tp"], c["kappa"], 0, c["Sb"])
        p["tmax"] = 4 * (p["Q"] // int(p["L"])) + 64
        return p
    kappa = kappa or KAPPA_256
    tmax = machine_constants()[5]
    if Tp:
        return _plan(256, Tp, kappa, tmax, CFG[256]["Sb"])
    lo, hi = 1.0, float(tmax + 1)                        # largest mean number of trails the table holds (tail 2^-40)
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if tail_log2(mid, tmax + 1) <= TAIL_LOG2 else (lo, mid)
    ok = lambda t: _lossq(t, lo, tmax, kappa, CFG[256]["Sb"])["P_lower"] >= P_MIN
    a, b = 1500, 4095                                    # bisection for the largest Tp (monotone); a passes, a + 1 fails
    if not ok(a):
        return None
    while b - a > 1:
        mm = (a + b) // 2
        a, b = (mm, b) if ok(mm) else (a, mm)
    assert ok(a) and not ok(a + 1)
    return _plan(256, a, kappa, tmax, CFG[256]["Sb"])


def rec_ops(p, pk):
    """Recovery bound: pass 1 at most c_r batches; the checkpoint pairs; pass 2 at most 17 D batches (16 single-lane walks of at most
    D - 1 steps and one joint walk of at most D) and 16 probes; call and setup."""
    D = -(-p["cr"] // KCHK)
    return p["cr"] * (pk + REC1_OPS) + KCHK * CHK_OPS + 17 * D * (pk + REC2_OPS) + 16 * PROBE_OPS + REC_FIXED


def ledger(p=None, st=None):
    """Operation budget in word operations (exact); time is operations / UNIT."""
    p = p or plan(256)
    st = st or step256()
    ph, per, rest, body, code, _ = machine_constants(st)
    gen = GEN_FACTOR * (2 * st.gen_calls + st.ops)           # the generator builds the network twice (use counts, then emission)
    bx = p["B"] + DELAY_MAX
    parts = dict(main=body * bx, stage1_rest=p["pmax"] * rest, slices=-(-bx // p["Sb"]) * SLICE_OPS,
                 stage1_hits=p["e2max"] * HIT_OPS, events=p["tmax"] * (EVENT_OPS + SLOT_OPS * (p["tmax"] + 1)),
                 cuts=p["cmax"] * CUT_OPS, recovery=rec_ops(p, packed_circuit(st.qwords)[1]), setup=SETUP_FIXED + gen, key_choice=KEY_OPS)
    return dict(parts=parts, total=sum(parts.values()), plan=p, body=body, gen=gen)


def _lossq(Tp, q, tmax, kappa, Sb, rate=1.0, fine=20000, coarse=2000):
    """Lemma 2 of proof Section 4 for q = Q / L trails; `rate` scales the collision hazard (H1 (d) sensitivity)."""
    L = Fraction(1 << 122, Tp)
    c = -(-kappa * L.numerator // L.denominator)
    th, Lf, cf, kr = Tp / 2.0 ** 122, float(L), float(c), float(KR) * float(L)
    Q, B, Np = q * Lf, q * Lf / LANES, 2.0 ** 256 / rate         # Q evaluations, B batches, N' (theta N is below float resolution)
    k = int(q) + 1
    while tail_log2(q, k) > -40:                                   # N1 ~ Binomial(Q, theta) <= k - 1 except with probability 2^-40
        k += 1
    n2, shift = k + LANES + 1, 1 / (1 - k * Q / Np)
    pi = lambda m: exp(-m * (m - 1) / (2 * Np))                    # Pi_m <= this; the collision term uses Pi_(Q-k+1) <= Pi_Q shift
    split = max(1.0, Q - 120 * LANES * Lf)                         # the detection penalty lives on the last 120 L batches: fine bins there
    edges = [split * i / coarse for i in range(coarse + 1)] + [split + (Q - split) * i / fine for i in range(1, fine + 1)]
    delay, pa = 0.0, 1.0
    for b in edges[1:]:
        pb = pi(b)
        delay += (pa - pb) * exp(-th * max(0.0, B - b / LANES))   # sum of (Pi_a - Pi_b) (1 - theta)^(B - ceil(b / 256)) over the bins (a, b]
        pa = pb
    p, ql, hq = exp(-cf * th), Q * Lf / Np, Q * (Q - 1) / (2 * Np)
    p2 = exp(-(cf - 1) * th) * (1 + (cf - 1) * th / (1 - th))
    hh = (Q * (Q - 1) / 2 + 2.0 ** TBITS * Q) / Np
    t = dict(collision=pi(Q) * shift, delay=delay * shift, own_trail=ql, long_partner=(cf + Sb + DELAY_MAX) * Q * p * (q + LANES) / ((1 - p) * Np), age_cap=hq * p2,
             rec_cap=2 * hq * exp(-(kr - 1) * th) * (1 + (kr - 1) * th / (1 - th)),
             disturbance=hq * Lf * (Q + 2.0 ** TBITS) / Np, finished_count=2.0 ** -40,
             cut_halt=-expm1(n2 * log1p(-p)) - n2 * p * exp((n2 - 1) * log1p(-p)) + ql * (1 + (2 + kappa) * exp(-kappa / 2) + 2 * hq) + hq * p * (3 + 2 * kappa),
             key_false_match=tmax * (tmax - 1) / 2 * 2.0 ** -(min(keybits(tmax) - (Tp - 1).bit_length(), 134) + log(Tp, 2)),
             table_capacity=2.0 ** tail_log2(q, tmax - 59),
             tiny=Q * 2.0 ** TBITS / Np + k * k * Lf / Np + 255 * Q / Np + exp(min(700.0, -300 + (exp(5) - 1) * hh)) + 2.0 ** -90)
    t["sum"] = sum(t.values())
    t["P_lower"] = 1 - t["sum"]
    t.update(trails=q, k=k, n2=n2, p=p, p2=p2, ql=ql, hq=hq, hh=hh, shift=shift)
    return t


_B = {}


def _b256(Tp, tmax, kappa, Sb):
    """The least B (multiple of GRAIN) with P_lower >= P_MIN."""
    if (Tp, tmax, kappa) not in _B:
        L = Fraction(1 << 122, Tp)
        lo, hi = 1.0, float(tmax + 1)
        for _ in range(40):
            mid = (lo + hi) / 2
            lo, hi = (lo, mid) if _lossq(Tp, mid, tmax, kappa, Sb)["P_lower"] >= P_MIN else (mid, hi)
        B = -(-int(hi * L / LANES) // GRAIN) * GRAIN
        while _lossq(Tp, float(B * LANES / L), tmax, kappa, Sb)["P_lower"] < P_MIN:
            B += GRAIN
        _B[(Tp, tmax, kappa)] = B
    return _B[(Tp, tmax, kappa)]


def loss(p, rate=1.0):
    """The probability losses of proof Section 4 (floats): the terms, their sum and the lower bound on the success probability."""
    return _lossq(p["Tp"], float(p["Q"] / p["L"]), p["tmax"], p["kappa"], p["Sb"], rate)


# -------- 6 search, table and recovery
class Halt(Exception):
    pass


class Engine:
    """The chain function g = f XOR q in two forms: step(planes) for 256 lanes and f2(xs) for the recovery (packed circuit with the XOR of q)."""

    def __init__(self, n):
        self.n = n
        st = Step(n)
        self.st, self.pin, self.step = st, st.pin, st.step

    def f2(self, xs):
        return packed_f(xs, self.n, self.st.qwords)

    def g_scalar(self, x):
        return f_scalar(x, self.n) ^ self.st.qint


class IdealEngine:
    """An ideal function of the same width (keyed blake2b) used as the control of test T3."""

    def __init__(self, n, key):
        self.n, self.key, self.pin = n, key, [0] * n
        self.nb = (n + 7) // 8

    def g(self, v):
        h = hashlib.blake2b(v.to_bytes(self.nb, "little"), key=self.key, digest_size=self.nb).digest()
        return int.from_bytes(h, "little") & ((1 << self.n) - 1)

    def step(self, *planes):
        vals = lanes_of(planes, self.n, self.pin)
        return pack_lanes([self.g(v) for v in vals], self.n, self.pin)

    def f2(self, xs):
        return [self.g(x) for x in xs]


def is_dp(x, p):
    """Mixed distinguished point: low s1 bits all ones and the window above them below Tp."""
    m = (1 << p["s1"]) - 1
    return x & m == m and (x >> p["s1"]) & ((1 << p["W"]) - 1) < p["Tp"]


def dp_key(x, p):
    """The kb bits above the window, then the fb low bits of the window value (which determine it)."""
    return (((x >> p["D"]) & ((1 << p["kb"]) - 1)) << p["fb"]) | ((x >> p["s1"]) & ((1 << p["fb"]) - 1))


class QF:
    """The table: a quotient filter of S slots (Bender et al., VLDB 2012).  A key of kb bits = quotient (top l bits, l = floor(log2 S):
    the home slot) and remainder (kb - l bits, stored with the trail number and the bits occupied, continuation, shifted).  The entries of
    one quotient form a run; runs lie in quotient order, shifted right (cyclically) past used slots.  The program never stores S keys, so
    a slot stays empty and every walk ends."""

    def __init__(self, S, kb):
        self.S, self.l = S, min(kb, S.bit_length() - 1)
        self.rb, self.n = kb - self.l, 0
        self.occ, self.cont, self.shf, self.rem, self.tr = ([0] * S for _ in range(5))

    def _start(self, h):
        """First slot of the run of home slot h (occ[h] set): back to the start of the cluster, then forward one run per occupied slot."""
        S, b = self.S, h
        while self.shf[b]:
            b = (b - 1) % S
        x = b
        while b != h:
            x = (x + 1) % S
            while self.cont[x]:
                x = (x + 1) % S
            b = (b + 1) % S
            while not self.occ[b]:
                b = (b + 1) % S
        return x

    def find(self, key):
        """(trail number, None) if key is stored; else (None, (h, x, c)): the slot x where key goes (the end of its run, c = 1, or the
        place of a new run, c = 0)."""
        h, r = key >> self.rb, key & ((1 << self.rb) - 1)
        if not self.occ[h]:
            self.occ[h] = 1
            x = self._start(h)
            self.occ[h] = 0
            return None, (h, x, 0)
        x = self._start(h)
        while True:
            if self.rem[x] == r:
                return self.tr[x], None
            x = (x + 1) % self.S
            if not self.cont[x]:
                return None, (h, x, 1)

    def put(self, key, t, at):
        """Store (remainder, t) at slot x; the entries from x up to the first empty slot move one slot right (shifted set)."""
        h, x, c = at
        r = key & ((1 << self.rb) - 1)
        assert t < 1 << TBITS and self.n < self.S - 1
        self.occ[h], e = 1, (r, t, c, int(x != h))
        while self.cont[x] or self.shf[x] or (self.occ[x] and (x != h or c)):
            e, (self.rem[x], self.tr[x], self.cont[x], self.shf[x]) = (self.rem[x], self.tr[x], self.cont[x], 1), e
            x = (x + 1) % self.S
        self.rem[x], self.tr[x], self.cont[x], self.shf[x] = e
        self.n += 1


def walk(xs, k, f2):
    for _ in range(k):
        xs = f2(xs)
    return xs


def recover(p, r, t0, t1, f2, kchk=KCHK):
    """Two trails t0, t1 with the same key.  Pass 1 walks both from their starts together (two lanes of one packed batch per step) until
    each is at a DP, at most c_r steps (else a halt), keeping every D-th point of each (D = ceil(c_r / kchk)).  Pass 2: A = the longer
    trail, d = l1 - l2, P(j): A_(j + d) = B_j is false, then true.  Unequal ends (P(l2) false) or P(0) true (B starts on A): no pair.
    Bisection over the checkpoints: P(lo D) false, P(min(hi D, l2)) true (a probe walks A d mod D steps from a checkpoint); then both
    walk together to the first equal outputs.  Returns (x, y), x != y, g(x) = g(y), or None."""
    mask, cr = p["N"] - 1, p["cr"]
    D = -(-cr // kchk)
    xs, ls, ends = [(r + t0) & mask, (r + t1) & mask], [None, None], [None, None]
    ck = [[xs[0]], [xs[1]]]
    for k in range(1, cr + 1):
        xs = f2(xs)
        for i in (0, 1):
            if ls[i] is None:
                if k % D == 0:
                    ck[i].append(xs[i])
                if is_dp(xs[i], p):
                    ls[i], ends[i] = k, xs[i]
        if None not in ls:
            break
    else:
        raise Halt("recovery length")
    a = 0 if ls[0] >= ls[1] else 1
    lb, (qd, rd) = ls[1 - a], divmod(abs(ls[0] - ls[1]), D)
    A = lambda i: walk([ck[a][i + qd]], rd, f2)[0]              # A_(i D + d)
    if ends[0] != ends[1] or A(0) == ck[1 - a][0]:
        return None
    lo, hi = 0, lb // D + 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        lo, hi = (lo, mid) if A(mid) == ck[1 - a][mid] else (mid, hi)
    x, y = A(lo), ck[1 - a][lo]
    for _ in range(min(hi * D, lb) - lo * D):
        fx, fy = f2([x, y])
        if fx == fy:
            return x, y
        x, y = fx, fy
    return None


def search(eng, p, r, cnt):
    """One attempt with the fresh random word r: the pair (x, y) or None.  Raises Halt at a budget.  Budgets: B batches, pmax passing
    batches, e2max stage-1 hits, tmax table keys, cmax cut trails, a recovery of at most c_r pass-1 batches."""
    n, mask, pin = p["n"], p["N"] - 1, eng.pin
    assert not any(pin)
    table, births, ts, nxt = QF(p["tmax"] + 1, p["kb"] + p["fb"]), [0] * LANES, list(range(LANES)), LANES
    planes = pack_lanes([(r + t) & mask for t in ts], n, pin)
    cnt["inserts"] += LANES
    batches, nslice = 0, p["Sb"]
    while True:
        planes = list(eng.step(*planes))
        batches += 1
        cnt["batches"] += 1
        hit = stage1(planes, p, cnt)
        if hit is None:
            continue
        while hit:
            cnt["stage1_hits"] += 1
            if cnt["stage1_hits"] > p["e2max"]:
                raise Halt("stage-1 budget")
            l = (hit & -hit).bit_length() - 1
            hit &= hit - 1
            x = lane_value(planes, l, pin, n)
            if is_dp(x, p):
                key = dp_key(x, p)
                cnt["finished"] += 1
                t0, at = table.find(key)
                if t0 is not None:
                    cnt["recoveries"] += 1
                    res = recover(p, r, t0, ts[l], eng.f2)
                    if res is None:
                        raise Halt("recovery found no pair")
                    return res
                if table.n >= p["tmax"]:
                    raise Halt("table full")
                table.put(key, ts[l], at)
                ts[l], nxt, births[l] = nxt, nxt + 1, batches
                planes = set_lane(planes, l, (r + ts[l]) & mask, pin, n)
                cnt["inserts"] += 1
        if batches >= min(nslice, p["B"]):
            if batches >= p["B"]:
                break
            nslice = (batches // p["Sb"] + 1) * p["Sb"]
            for l in range(LANES):
                if batches - births[l] >= p["c"]:
                    cnt["cut"] += 1
                    if cnt["cut"] > p["cmax"]:
                        raise Halt("cut budget")
                    ts[l], nxt, births[l] = nxt, nxt + 1, batches
                    planes = set_lane(planes, l, (r + ts[l]) & mask, pin, n)
                    cnt["inserts"] += 1
    return None


class Counters(dict):
    def __missing__(self, k):
        return 0


def derive(seed, tag, bits=256):
    return int.from_bytes(hashlib.shake_256(("%s/%s" % (seed, tag)).encode()).digest((bits + 7) // 8), "little") & ((1 << bits) - 1)


def attempt(eng, p, seed, tag):
    cnt = Counters()
    try:
        res = search(eng, p, derive(seed, tag, p["n"]), cnt)
    except Halt as e:
        cnt["halt"] += 1
        res = None
    return res, cnt


# -------- 7 organizer experiments
N_T3 = 18                          # width of the search experiment and of the ideal control
N_T1 = 12                          # width of the family-law runs (fresh key)
M_T2, B_T2 = 2048, 21              # points per trial, projection width (event: low 21 bits of the digest)


def t1_run(seed, n=N_T1):
    """Family law, fresh random prefix P: steps until the first repeat of x -> low n bits of digest(P || x)."""
    key, x, seen = derive(seed, "k"), derive(seed, "s", n), set()
    while x not in seen:
        seen.add(x)
        x = f_scalar(x, n, key)
    return len(seen)


def e1_trial(seed, eng, ideal_cls):
    """T3 (target, organizer-checked pair) and the ideal control, one attempt each; T1 as an observation."""
    p = plan(N_T3)
    res, cnt = attempt(eng, p, seed, "t")
    ideal = ideal_cls(N_T3, hashlib.blake2b(("%s/ideal" % seed).encode(), digest_size=32).digest())
    res_i, cnt_i = attempt(ideal, p, seed, "i")
    obs = dict(target_ok=int(res is not None), ideal_ok=int(res_i is not None), target_batches=cnt["batches"],
               target_halt=cnt["halt"], ideal_halt=cnt_i["halt"], t1_steps=t1_run(seed))
    if res is None:
        return None, None, obs
    return message(res[0]), message(res[1]), obs


def e2_trial(seed, tr, st256):
    """T2: M_T2 points of the target at width 256 (source by trial index: uniform inputs, counter r + i, or iterates of g from 256 random
    starts), digests f(x) = (stored planes) XOR q; a pair whose digests agree in the low B_T2 bits, and the number of such equal pairs."""
    src = tr % 3
    if src == 0:
        xs = [derive(seed, "u%d" % i) for i in range(M_T2)]
    elif src == 1:
        r = derive(seed, "r")
        xs = [(r + i) & ((1 << 256) - 1) for i in range(M_T2)]
    else:
        xs = None
    digs = []
    if xs is not None:
        for b in range(M_T2 // LANES):
            pl = pack_lanes(xs[b * LANES:(b + 1) * LANES], 256, st256.pin)
            digs += lanes_of(list(st256.step(*pl)), 256, st256.pin)
    else:
        cur = [derive(seed, "c%d" % l) for l in range(LANES)]
        xs = []
        for b in range(M_T2 // LANES):
            xs += cur
            cur = lanes_of(list(st256.step(*pack_lanes(cur, 256, st256.pin))), 256, st256.pin)
            digs += cur
    digs = [d ^ st256.qint for d in digs]                  # the circuit stores g(x) = f(x) XOR q; the projections are of the digest f(x)
    col = [d & ((1 << B_T2) - 1) for d in digs]
    obs, pair, first = {"source": src, "dup_w0": len(col) - len(set(col))}, None, {}
    for i, c in enumerate(col):
        if c in first and xs[first[c]] != xs[i]:
            pair = (xs[first[c]], xs[i])
            break
        first.setdefault(c, i)
    if pair is None:
        return None, None, obs
    return message(pair[0]), message(pair[1]), obs


def serve(req):
    eid, out = req["experiment_id"], []
    if eid == "bsrho-n18":
        eng = Engine(N_T3)
        for t in req["trials"]:
            a, b, obs = e1_trial(t["seed"], eng, IdealEngine)
            out.append({"trial": t["trial"], "message_a_hex": a.hex() if a else None, "message_b_hex": b.hex() if b else None,
                        "observations": obs})
    elif eid == "proj-k0-w256":
        st = step256()
        for t in req["trials"]:
            a, b, obs = e2_trial(t["seed"], t["trial"], st)
            out.append({"trial": t["trial"], "message_a_hex": a.hex() if a else None, "message_b_hex": b.hex() if b else None,
                        "observations": obs})
    else:
        raise ValueError("unknown experiment")
    return {"schema_version": 1, "trials": out}


# -------- 8 command line
def selftest():
    import random
    ok = True
    rnd = random.Random(3)
    st = step256()
    print("hash-consing hits", st.hits, "dead gates", st.dead, "(the machine generator keeps no node table: both must be 0)")
    ok &= st.hits == 0 and st.dead == 0
    print("n=256 step: gates", st.gates, st.by, "q weight", bin(st.qint).count("1"))
    code, regs = allocate(st)
    print("allocation: registers used", regs, "moves 0 (output j in register j)")
    pl0 = [rnd.getrandbits(256) for _ in range(256)]
    good = run_allocated(st, code, pl0) == list(st.step(*pl0))
    print("allocated code on a register file equals the step:", good)
    ok &= good
    good, tot = True, 0                                   # the step against the scalar compression, full 256-bit g = f XOR q
    for _ in range(16):
        xs = [rnd.getrandbits(256) for _ in range(LANES)]
        out = lanes_of(list(st.step(*pack_lanes(xs, 256, st.pin))), 256, st.pin)
        good &= all(out[l] == f_scalar(xs[l], 256) ^ st.qint for l in range(LANES))
        tot += LANES
    print("%d lanes, step vs scalar compression: %s" % (tot, good))
    ok &= good
    good = True
    for _ in range(16):
        cur = [rnd.getrandbits(256) for _ in range(LANES)]
        pl = pack_lanes(cur, 256, st.pin)
        for _ in range(7):
            pl = list(st.step(*pl))
            cur = [f_scalar(x, 256) ^ st.qint for x in cur]
        good &= lanes_of(pl, 256, st.pin) == cur
    print("4,096 lanes chained for 7 steps vs scalar compression:", good)
    ok &= good
    e = Engine(N_T3)
    xs = [rnd.getrandbits(N_T3) for _ in range(LANES)]
    pl = pack_lanes(xs, N_T3, e.pin)
    for _ in range(5):
        pl = list(e.step(*pl))
        xs = [e.g_scalar(x) for x in xs]
    good = lanes_of(pl, N_T3, e.pin)[:LANES] == xs
    print("n=%d chain, 5 steps, 256 lanes:" % N_T3, good)
    ok &= good
    xs = [rnd.getrandbits(256) for _ in range(7)]
    good = packed_f(xs, 256, st.qwords) == [f_scalar(x, 256) ^ st.qint for x in xs]
    print("packed recovery circuit (%d ops, with the XORs of q) vs scalar:" % packed_circuit(st.qwords)[1], good)
    ok &= good
    rows = [rnd.getrandbits(256) for _ in range(256)]
    good = transpose(transpose(rows)) == rows and (transpose(rows)[5] >> 9) & 1 == (rows[9] >> 5) & 1
    print("transpose:", good)
    ok &= good
    good = True                                           # the table against a dictionary, small S with wraparound
    for S, kb in ((37, 12), (64, 9), (101, 20)):
        qf, ref = QF(S, kb), {}
        while qf.n < S - 1:
            k = rnd.getrandbits(kb)
            t0, at = qf.find(k)
            good &= t0 == ref.get(k)
            if t0 is None:
                ref[k] = qf.n
                qf.put(k, qf.n, at)
        good &= all(qf.find(k)[0] == v for k, v in ref.items())
    print("quotient-filter table vs dictionary:", good)
    ok &= good
    p = plan(N_T3)                                        # the recovery with checkpoints (D = 1 and D > 1) on trails with equal ends
    r, ends, pairs = rnd.getrandbits(N_T3), {}, 0
    for t in range(400):
        x, l = (r + t) % p["N"], 0
        while l < p["cr"]:
            x, l = e.f2([x])[0], l + 1
            if is_dp(x, p):
                if x in ends and pairs < 20:
                    a, b = recover(p, r, ends[x], t, e.f2), recover(p, r, ends[x], t, e.f2, 3)
                    good &= a == b and (a is None or (a[0] != a[1] and e.g_scalar(a[0]) == e.g_scalar(a[1])))
                    pairs += a is not None
                ends.setdefault(x, t)
                break
    print("recovery, checkpoints every step and every ceil(c_r / 3) steps agree on %d pairs:" % pairs, good)
    ok &= good and pairs > 0
    found = 0                                             # the search at n = 18 finds recoverable collisions
    for s in range(6):
        res, cnt = attempt(e, p, "selftest/%d" % s, "t")
        if res is not None:
            found += 1
            ok &= res[0] != res[1] and f_scalar(res[0], N_T3) == f_scalar(res[1], N_T3)
    print("search n=%d: %d of 6 attempts returned a verified pair" % (N_T3, found))
    ok &= found > 0
    print("selftest", ok)
    return ok


def choose_key(nb=4):
    """The offline choice of KEY (proof 3.7): coordinate descent from the zero key; word i = 0..7 in order, values v << (32 - nb),
    v = 0 .. 2^nb - 1 in order; a value is kept when the number of gates of the network drops; sweeps until one keeps nothing.
    Prints the key, the evaluations and their charge GEN_FACTOR * (primitive calls + nodes), summed."""
    def ev(k):
        g, out = trace(256, k)
        return len(used_gates(g, out)), GEN_FACTOR * (g.calls + len(g.nodes))
    key = [0] * 8
    best, ops = ev(key)
    evals, imp = 1, True
    while imp:
        imp = False
        for i in range(8):
            for v in range(1 << nb):
                if v << (32 - nb) != key[i]:
                    k2 = key[:i] + [v << (32 - nb)] + key[i + 1:]
                    g, o = ev(k2)
                    evals, ops = evals + 1, ops + o
                    if g < best:
                        best, key, imp = g, k2, True
    print("key", ["%08x" % k for k in key], "gates", best, "evaluations", evals, "charge", ops)


def print_ledger(lg):
    from math import log2
    print({k: (str(v) if isinstance(v, Fraction) else v) for k, v in lg["plan"].items()})
    print("operations per batch (body)", lg["body"])
    for k, v in lg["parts"].items():
        print(k, v)
    print("N =", lg["total"])
    print("time_log2 = %.5f (unrounded %.8f)" % (log2(lg["total"] / UNIT) + 5e-6, log2(lg["total"] / UNIT)))


# -------- 9 the circuit generator in C (proof 3.6): compiled with clang -Os to WebAssembly and run with 16 pages (2^20 bytes) of guest
# memory it emits the same program as Step/allocate (sha256 equal).  `--gen-c` prints it.
GEN_C = r'''/* GEN_C: C port of Gen / trace(256) / allocate, two passes, no node table (no shared, no dead gate), no libc.  Pass 0 counts the uses
   of each node (8 bits); pass 1 rebuilds, frees a register when its count reaches 0 (output j pinned to register j), writes 5-byte records
   (op byte, then dst, a, b as 10-bit fields).  Column choice by dry trials (dry = 1: counted, not recorded), as Gen.add3. */
typedef unsigned char u8; typedef unsigned int u32;
#ifndef NMAX
#define NMAX 23736
#endif
#ifndef CODE_BYTES
#define CODE_BYTES 135582
#endif
#define ROUNDS 4
#define N 256
#define REC 5
#define NODE(s) (((s) >> 1) & 0xFFFFu)
#define REG(s) ((s) >> 17)
#define ZERO 0u
#define ONE 1u

static u8 code[CODE_BYTES];
__attribute__((used)) static u8 counters[5248];
static u8 uses[NMAX + 1];
static u32 v[16][32], tmp[32], mw[32], fbits[24];
static u32 nn, calls, err, pass, kk, nxt, top, firstout, dry;
static struct { u32 ninst, nreg, nodes, calls, err, sz_code, sz_ctr, sz_uses, sz_state; u8 q[32]; } info;

static const u32 IV[8] = {0x6A09E667u,0xBB67AE85u,0x3C6EF372u,0xA54FF53Au,0x510E527Fu,0x9B05688Cu,0x1F83D9ABu,0x5BE0CD19u};
static const u32 KEY[8] = {0x80000000u,0,0x80000000u,0,0x70000000u,0,0,0};
static const u8 PERM[16] = {2,6,3,10,7,0,4,13,1,11,12,5,9,14,15,8};
static const u8 GC[8][4] = {{0,4,8,12},{1,5,9,13},{2,6,10,14},{3,7,11,15},{0,5,10,15},{1,6,11,12},{2,7,8,13},{3,4,9,14}};
/* COLLIB: polarity key, oU, gate count, 9 gates (op 0 xor 1 and 2 or, i, j), outputs s, u', U' (node or 255, polarity flip) */
static const u8 LIB[4][36] = {
 {16,0,9, 0,0,4, 0,1,5, 0,1,2, 0,3,5, 2,6,7, 0,2,6, 1,4,8, 0,5,9, 0,9,11, 10,1, 12,0, 13,0},
 {16,1,8, 0,1,4, 0,3,5, 0,0,2, 0,2,5, 2,7,8, 1,4,6, 0,0,8, 0,9,10, 0,0,0, 11,1, 255,0, 12,0},
 {7,0,9,  0,0,2, 0,1,5, 0,3,6, 0,0,1, 2,4,7, 2,5,8, 0,6,9, 0,9,10, 0,4,6, 13,1, 11,0, 12,1},
 {7,1,8,  0,1,2, 0,0,5, 0,0,1, 2,5,7, 0,4,6, 0,3,9, 2,4,10, 0,8,11, 0,0,0, 9,1, 255,0, 12,1}};

static void put32(u8 *p, u32 w) { p[0] = (u8)w; p[1] = (u8)(w >> 8); p[2] = (u8)(w >> 16); p[3] = (u8)(w >> 24); }
static void drop(u32 s) {
  u32 n = NODE(s), c = uses[n] - 1u;
  uses[n] = (u8)c;
  if (c == 0 && REG(s) >= N) { u32 r = REG(s) - N; fbits[r >> 5] |= 1u << (r & 31); }
}
static u32 mk(u32 op, u32 x, u32 y) {
  calls++;
  if (NODE(x) > NODE(y)) { u32 t = x; x = y; y = t; }
  u32 id = nn++;
  if (dry) return id << 1;
  if (id >= NMAX) { err = 1; return 0; }
  if (pass == 0) {
    u32 a = NODE(x), b = NODE(y);
    if (uses[a] == 255 || uses[b] == 255) { err = 6; return 0; }
    uses[a]++; uses[b]++;
    return id << 1;
  }
  u32 ra = REG(x), rb = REG(y), d;
  drop(x); drop(y);
  if (id >= firstout) {
    d = id - firstout;
    if (uses[1 + d] != 0) { err = 4; return 0; }
  } else {
    u32 w = 0;
    while (w < 24 && fbits[w] == 0) w++;
    if (w < 24) { u32 b = 0; while (!((fbits[w] >> b) & 1u)) b++; fbits[w] &= ~(1u << b); d = N + 32 * w + b; }
    else d = nxt++;
  }
  if (d + 1 > top) top = d + 1;
  if (kk >= CODE_BYTES / REC) { err = 5; return 0; }
  u8 *rec = code + (u32)REC * kk++;
  rec[0] = op == 0 ? '^' : op == 1 ? '&' : '|';
  if (d >= 1024 || ra >= 1024 || rb >= 1024) { err = 7; return 0; }
  put32(rec + 1, d | (ra << 10) | (rb << 20));
  return (id << 1) | (d << 17);
}
static u32 XOR(u32 x, u32 y) {
  calls++;
  if (!NODE(x)) return y ^ (x & 1);
  if (!NODE(y)) return x ^ (y & 1);
  if (NODE(x) == NODE(y)) return (x ^ y) & 1;
  return mk(0, x, y) ^ ((x ^ y) & 1);
}
static u32 AND(u32 x, u32 y) {
  calls++;
  if (!NODE(x)) return (x & 1) == 0 ? ZERO : y;
  if (!NODE(y)) return (y & 1) == 0 ? ZERO : x;
  if (NODE(x) == NODE(y)) return x == y ? x : ZERO;
  if (!(x & 1) && !(y & 1)) return mk(1, x, y);
  if ((x & 1) && (y & 1)) return mk(2, x, y) | 1;
  u32 p = (x & 1) == 0 ? x : y, q = (x & 1) == 0 ? y : x;
  return XOR(p, mk(1, p, q));
}
static u32 OR(u32 x, u32 y) { return AND(x ^ 1, y ^ 1) ^ 1; }
static void fa(u32 a, u32 b, u32 c, u32 *sum, u32 *carry) {
  u32 ops[3] = {a, b, c}, vs[3], nv = 0, k = 0, nc = 0, cs[3] = {0, 0, 0};
  for (int i = 0; i < 3; i++) {
    if (!NODE(ops[i])) { cs[nc++] = ops[i] & 1; k ^= ops[i] & 1; } else vs[nv++] = ops[i];
  }
  if (nv == 3) {
    u32 p = 0, x = 0, y = 0;
    for (int pi = 0; pi < 3; pi++) {
      u32 o0 = vs[pi == 0 ? 1 : 0], o1 = vs[pi == 2 ? 1 : 2];
      if ((o0 & 1) == (o1 & 1)) { p = vs[pi]; x = o0; y = o1; break; }
    }
    u32 u = XOR(x, p);
    u32 s = XOR(u, y);
    u32 w = XOR(y, p);
    u32 an = AND(u, w);
    *sum = s; *carry = XOR(an, p); return;
  }
  if (nv == 2) {
    u32 x = vs[0], y = vs[1];
    u32 t = XOR(x, y);
    u32 s = t ^ k;
    if ((x & 1) == (y & 1)) {
      if (k == 0) { *sum = s; *carry = AND(x, y); return; }
      *sum = s; *carry = AND(x ^ 1, y ^ 1) ^ 1; return;
    }
    u32 nt = t ^ 1;
    u32 xx = (x & 1) == (nt & 1) ? x : y;
    if (k == 0) { *sum = s; *carry = AND(xx, nt); return; }
    u32 yy = (x & 1) == (t & 1) ? x : y;                  /* k = 1, opposite polarities: carry = yy OR (x XOR y) */
    *sum = s; *carry = AND(yy ^ 1, t ^ 1) ^ 1; return;
  }
  if (nv == 1) {
    u32 x = vs[0], k1 = cs[0], k2 = cs[1];
    *sum = x ^ k; *carry = (k1 == 1 && k2 == 1) ? ONE : (k1 == 0 && k2 == 0) ? ZERO : x; return;
  }
  u32 kk3 = cs[0] + cs[1] + cs[2];
  *sum = (kk3 % 2 == 0) ? ZERO : ONE; *carry = kk3 >= 2 ? ONE : ZERO;
}
static void add(const u32 *A, const u32 *B, u32 *out) {   /* out may alias A */
  u32 c = ZERO;
  for (int i = 0; i < 32; i++) {
    if (i == 31) out[i] = XOR(XOR(A[i], B[i]), c);
    else { u32 si; fa(A[i], B[i], c, &si, &c); out[i] = si; }
  }
}
static void col(u32 x, u32 y, u32 z, u32 u, u32 U, int tm, int oU, u32 *s, u32 *uo, u32 *Uo) {   /* Gen._col */
  if (tm == 2) {
    u32 key = (x & 1) | (y & 1) << 1 | (z & 1) << 2 | (u & 1) << 3 | (U & 1) << 4, e = 0;
    while (e < 4 && !(LIB[e][0] == key && LIB[e][1] == (u32)oU)) e++;
    if (e == 4) tm = 0;
    else {
      const u8 *L = LIB[e];
      u32 nd[14] = {x & ~1u, y & ~1u, z & ~1u, u & ~1u, U & ~1u};
      for (u32 g = 0; g < L[2]; g++) {
        const u8 *G = L + 3 + 3 * g;
        nd[5 + g] = G[0] == 0 ? XOR(nd[G[1]], nd[G[2]]) : G[0] == 1 ? AND(nd[G[1]], nd[G[2]]) : OR(nd[G[1]], nd[G[2]]);
      }
      *s = nd[L[30]] ^ L[31];
      if (L[32] != 255) *uo = nd[L[32]] ^ L[33];
      *Uo = nd[L[34]] ^ L[35];
      return;
    }
  }
  if (tm) {
    u32 w = XOR(y, U), n8 = XOR(z, w);
    *s = XOR(x, n8);
    u32 t1 = XOR(y, u), n6 = OR(U, t1);
    if (!oU) *uo = XOR(n6, w);
    u32 t2 = XOR(x, w), t3 = AND(n8, t2);
    *Uo = XOR(n6, t3);
  } else {
    u32 n5 = XOR(z, U), n9 = XOR(x, n5);
    *s = XOR(y, n9);
    u32 n6 = XOR(x, y), t1 = XOR(z, u), n8 = OR(U, t1), n11 = AND(n6 ^ 1, n9);
    if (!oU) *uo = XOR(n5, n11);
    *Uo = XOR(n8, n11);
  }
}
static void add3(const u32 *A, const u32 *B, const u32 *C, u32 *out) {   /* Gen.add3; out may alias A */
  u32 U, u = ZERO, s, uo = 0, Uo, s0;
  fa(A[0], B[0], C[0], &s0, &U);
  out[0] = s0;
  for (int i = 1; i < 31; i++) {
    u32 a = A[i], b = B[i], c = C[i];
    u32 o[6][3] = {{a, b, c}, {a, c, b}, {b, a, c}, {b, c, a}, {c, a, b}, {c, b, a}};
    u32 bk = 1000, bo = 0, bt = 0;
    for (u32 j = 0; j < 6; j++)
      for (u32 tm = 0; tm < 3; tm++) {
        u32 n0 = nn;
        dry = 1; col(o[j][0], o[j][1], o[j][2], u, U, (int)tm, i == 30, &s, &uo, &Uo); dry = 0;
        u32 k = nn - n0; nn = n0;
        if (k < bk) { bk = k; bo = j; bt = tm; }
      }
    col(o[bo][0], o[bo][1], o[bo][2], u, U, (int)bt, i == 30, &s, &uo, &Uo);
    out[i] = s; u = uo; U = Uo;
  }
  out[31] = XOR(XOR(XOR(A[31], B[31]), C[31]), U);
}
static int allvar(const u32 *A) { for (int i = 0; i < 32; i++) if (!NODE(A[i])) return 0; return 1; }
static void s3(u32 *a, const u32 *b, const u32 *m) {      /* a = a + b + m */
  if (allvar(a) && allvar(b) && allvar(m)) add3(a, b, m, a);
  else { add(a, b, a); add(a, m, a); }
}
static void xorrot(u32 *D, const u32 *A, int r) {         /* D = ror_planes(xorw(D, A), r) */
  for (int i = 0; i < 32; i++) tmp[i] = XOR(D[i], A[i]);
  for (int i = 0; i < 32; i++) D[i] = tmp[(i + r) & 31];
}
static void constw(u32 *w, u32 val) { for (int i = 0; i < 32; i++) w[i] = (val >> i) & 1u; }
static u32 inp(u32 j) { return ((1 + j) << 1) | (j << 17); }
static u32 *msg(u32 w) {                                  /* message word w of KEY || x */
  if (w < 8) constw(mw, KEY[w]); else for (u32 b = 0; b < 32; b++) mw[b] = inp(32 * (w - 8) + b);
  return mw;
}
static void trace(void) {
  u32 mi[16], nm[16];
  nn = 1 + N;
  for (int i = 0; i < 8; i++) constw(v[i], IV[i]);
  for (int i = 0; i < 4; i++) constw(v[8 + i], IV[i]);
  constw(v[12], 0); constw(v[13], 0); constw(v[14], 64); constw(v[15], 11);
  for (int i = 0; i < 16; i++) mi[i] = (u32)i;
  for (int r = 0; r < ROUNDS; r++) {
    for (int j = 0; j < 8; j++) {
      u32 a = GC[j][0], b = GC[j][1], c = GC[j][2], d = GC[j][3];
      s3(v[a], v[b], msg(mi[2 * j]));
      xorrot(v[d], v[a], 16);
      add(v[c], v[d], v[c]);
      xorrot(v[b], v[c], 12);
      s3(v[a], v[b], msg(mi[2 * j + 1]));
      xorrot(v[d], v[a], 8);
      add(v[c], v[d], v[c]);
      xorrot(v[b], v[c], 7);
    }
    for (int i = 0; i < 16; i++) nm[i] = mi[PERM[i]];
    for (int i = 0; i < 16; i++) mi[i] = nm[i];
  }
  firstout = nn;                                           /* the 256 output gates are the last 256 gates, in order */
  for (u32 j = 0; j < N; j++) {
    u32 s = XOR(v[j >> 5][j & 31], v[(j >> 5) + 8][j & 31]);
    if (!NODE(s) || NODE(s) != firstout + j) err = 3;
    info.q[j >> 3] |= (u8)((s & 1) << (j & 7));
  }
}
__attribute__((export_name("info_ptr"))) u32 info_ptr(void) { return (u32)(unsigned long)&info; }
__attribute__((export_name("code_ptr"))) u32 code_ptr(void) { return (u32)(unsigned long)code; }
__attribute__((export_name("run"))) int run(void) {
  info.sz_code = sizeof code; info.sz_ctr = sizeof counters; info.sz_uses = sizeof uses;
  info.sz_state = sizeof v + sizeof tmp + sizeof mw + sizeof fbits;
  err = 0; calls = 0; pass = 0; kk = 0; nxt = N; top = N; dry = 0;
  trace();
  info.nodes = nn;
  if (err) { info.err = err; return (int)err; }
  pass = 1;
  trace();
  info.calls = calls;
  info.ninst = kk; info.nreg = top; info.err = err;
  return (int)err;
}
'''


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    if arg == "--selftest":
        sys.exit(0 if selftest() else 1)
    elif arg == "--ledger":
        from math import log2
        print_ledger(ledger())
        st = step256()
        ph, per, rest, body, code, tmax = machine_constants(st)
        print("PH", ph, "stage 1 per batch", per, "passing extra", rest, "body", body, "code bytes", code, "tmax", tmax, "key bits", keybits(tmax))
        ph1, ph2 = phase_bytes(code, tmax)
        print("setup phase bytes", ph1, "search phase bytes", ph2, "limit", MEM_LIMIT, "fits", max(ph1, ph2) <= MEM_LIMIT)
        print("generator scratch, use counts, nodes", gen_scratch(), "image", GEN_CODE * GEN_INSTR_BYTES, "calls (one pass)", st.gen_calls)
        print("recovery circuit operations", packed_circuit(st.qwords)[1], "registers", allocate(st)[1], "q (hex)", "%064x" % st.qint)
    elif arg == "--choose-key":
        choose_key()
    elif arg == "--gen-c":
        sys.stdout.write(GEN_C)
    elif arg == "--loss":
        for k, v in loss(plan(256)).items():
            print(k, v)
    else:
        json.dump(serve(json.load(sys.stdin)), sys.stdout)
