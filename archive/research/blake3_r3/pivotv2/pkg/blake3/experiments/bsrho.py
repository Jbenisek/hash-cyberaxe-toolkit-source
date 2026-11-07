"""Birthday collision search on 3-round BLAKE3-256 (blake3-r3, one block) with 256 bit-sliced lanes and distinguished points.

The message is 64 bytes: 32 zero bytes (words m0..m7) and x (words m8..m15, little endian), one chunk of one block: chaining value IV, counter 0,
length 64, flags 11 = CHUNK_START|CHUNK_END|ROOT.  f(x) is the 256-bit little-endian digest integer; the walk is on g(x) = f(x) XOR q, where q is the
fixed 256-bit mask of the polarities of the digest planes of the generated circuit (the digest planes are fed back as the circuit stores them, no
complement is computed); g(x) = g(y) if and only if f(x) = f(y).  n = 256 is the claim; the organizer experiments run the same code at reduced n
(the low n bits of g).
Sections: 1 scalar digest, 2 packed 7-lane tracer (the recovery circuit), 3 bit-sliced generator (256 lanes, one plane per bit: rotations are
renaming; full adders by the pivot rule), 4 register allocation, 5 plan and ledger, 6 search and recovery, 7 organizer experiments,
8 command line (--selftest --ledger --loss --sweep --stats --gencode).
Credit: the pivot full adder and the mask walk g = f XOR q are the method of jungjipdo's 6ae36351 (proof 3.3, 3.4), implemented here from its
text; everything else is our 0a9640ed / 3356413f program.
"""
import sys
import json
import hashlib
from fractions import Fraction
from math import isqrt, log, exp, expm1, log1p, comb

M32 = 0xFFFFFFFF
IV = (0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19)
PERM = (2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8)
GCALLS = ((0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15),
          (0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14))
LANES, ALL = 256, (1 << 256) - 1
FLAGS = 11


# ---------------------------------------------------------------- 1 scalar digest
def _ror(v, k):
    return ((v >> k) | (v << (32 - k))) & M32


def digest_words(m, rounds=3, flags=FLAGS, blen=64, counter=0):
    """Compression of the single block m (16 words) with chaining value IV, counter 0, length 64, flags 11 (CHUNK_START|CHUNK_END|ROOT):
    8 digest words v[i] XOR v[i+8], 3 rounds."""
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


def f_scalar(x, n, key=0):
    """f(x): the low n bits of the digest of the message key(32 bytes) || x.  key = 0 is the target."""
    kw = [(key >> (32 * i)) & M32 for i in range(8)]
    d = digest_words(kw + [(x >> (32 * i)) & M32 for i in range(8)])
    return sum(d[i] << (32 * i) for i in range(8)) & ((1 << n) - 1)


def message(x):
    return bytes(32) + x.to_bytes(32, "little")


# ---------------------------------------------------------------- 2 packed tracer (recovery circuit)
PITCH, PLANES7 = 36, 7
REP = sum(1 << (PITCH * i) for i in range(PLANES7))
LIM = 1 << PITCH


class Tracer:
    """Straight-line code over 256-bit words holding 7 lanes of 36 bits (32 data bits and 4 guard bits).  A value is ('c', k),
    the same constant in every lane (folded at build time, no operation), or ('v', register, bound).  Every emitted line is one
    machine operation (add, and, or, xor, shl, shr; constants are immediates)."""

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
    """The recovery circuit for the walk g = f XOR q: the plain 3-round compression of the block 0^32 || x followed by one XOR of each of the 8
    output words with the 32-bit word of q (a word that is 0 costs no operation).  qw = the 8 words of q."""
    tr = Tracer()
    v = [("c", w) for w in IV] + [("c", w) for w in IV[:4]] + [("c", 0), ("c", 0), ("c", 64), ("c", FLAGS)]
    m = [("c", 0)] * 8 + [("v", "i%d" % i, M32) for i in range(8, 16)]
    for _ in range(3):
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


# ---------------------------------------------------------------- 3 bit-sliced generator
ZERO, ONE = (0, 0), (0, 1)


class Gen:
    """Hash-consed gate network over signals (node, neg): the stored plane is the true plane xor all-ones when neg = 1.
    Node kinds: ('v', j) input plane j, (op, a, b) with op x (xor), a (and), o (or).  calls counts generator primitives."""

    def __init__(self, n):
        self.n, self.nodes, self.memo, self.calls = n, [("c",)], {}, 0
        self.inputs = []
        for j in range(n):
            self.nodes.append(("v", j))
            self.inputs.append((len(self.nodes) - 1, 0))

    def mk(self, op, a, b):
        self.calls += 1
        if a > b:
            a, b = b, a
        k = (op, a, b)
        if k not in self.memo:
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
        """(sum, carry) of three planes a + b + c by the pivot rule (the method of 6ae36351 proof 3.3, implemented here from its text).
        Three variable planes: two of the three polarities agree, so take the third as the pivot p and the two equal ones as x and y;
        u = x ^ p, v = y ^ p, sum = u ^ y, carry = (u & v) ^ p.  u and v then have equal polarity, so the AND is always one gate (AND or OR):
        every full adder is 5 gates.  One or two constant planes fold: with one constant k, sum = x ^ y ^ k and carry = x & y (k = 0)
        or x | y (k = 1), 2 or 3 gates; with two constants the plane passes through."""
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
            cr = self.AND((xx[0], xx[1] ^ 1), (t[0], t[1] ^ 1))
            return s, (cr[0], cr[1] ^ 1)
        if len(vs) == 1:
            x = vs[0]
            k1, k2 = cs[0][1], cs[1][1]
            return (x[0], x[1] ^ k), (ONE if k1 == k2 == 1 else ZERO if k1 == k2 == 0 else x)
        kk = cs[0][1] + cs[1][1] + cs[2][1]
        return (ZERO if kk % 2 == 0 else ONE), (ONE if kk >= 2 else ZERO)

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


def _ror_planes(A, r):
    return [A[(i + r) % 32] for i in range(32)]


def _constw(v):
    return [ONE if (v >> i) & 1 else ZERO for i in range(32)]


def trace(n):
    """The network of the 3-round digest of the block 0^32 || x (chaining value IV, flags 11), x = low n bits of the input planes (planes >= n are 0).
    Input planes are upright; output plane j is the signal (node, neg): the plane the circuit stores is the node, so the stored value is the digest
    plane XOR neg."""
    g = Gen(n)
    zero = _constw(0)
    m = [zero] * 8 + [[g.inputs[32 * i + b] if 32 * i + b < n else ZERO for b in range(32)] for i in range(8)]
    v = [_constw(w) for w in IV] + [_constw(w) for w in IV[:4]] + [zero, zero, _constw(64), _constw(FLAGS)]
    for _ in range(3):
        for j, (a, b, c, d) in enumerate(GCALLS):
            x, y = m[2 * j], m[2 * j + 1]
            v[a] = g.add(g.add(v[a], v[b]), x)
            v[d] = _ror_planes(g.xorw(v[d], v[a]), 16)
            v[c] = g.add(v[c], v[d])
            v[b] = _ror_planes(g.xorw(v[b], v[c]), 12)
            v[a] = g.add(g.add(v[a], v[b]), y)
            v[d] = _ror_planes(g.xorw(v[d], v[a]), 8)
            v[c] = g.add(v[c], v[d])
            v[b] = _ror_planes(g.xorw(v[b], v[c]), 7)
        m = [m[i] for i in PERM]
    return g, [s for i in range(8) for s in g.xorw(v[i], v[i + 8])]      # output plane 32 i + b


class Step:
    """The straight-line chain step for width n.  step(*planes) takes the n input planes (upright) and returns the n output planes exactly as the
    circuit stores them: stored plane j = digest plane j XOR q_j, where q_j is the polarity of the generated signal (self.q).  The digest planes are
    fed back as they are, so the chain is x -> g(x) = f(x) XOR q (low n bits); no operation complements a plane.  ops = gates."""

    def __init__(self, n=256):
        g, out = trace(n)
        self.n, self.pin, self.gen_calls = n, [0] * n, g.calls
        assert all(out[j][0] != 0 for j in range(n))
        self.q = [out[j][1] for j in range(n)]
        self.qint = sum(b << j for j, b in enumerate(self.q))
        self.qwords = [(self.qint >> (32 * i)) & M32 for i in range(8)]
        seen = set(out[j][0] for j in range(n))
        for k in range(len(g.nodes) - 1, 0, -1):
            if k in seen and g.nodes[k][0] in "xao":
                seen.add(g.nodes[k][1])
                seen.add(g.nodes[k][2])
        order = [k for k in range(1, len(g.nodes)) if k in seen and g.nodes[k][0] in "xao"]
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
        outs = [names[out[j][0]] for j in range(n)]
        self.ops, self.outs = self.gates, outs
        nl = chr(10)
        self.src = ("def step(%s):" % ",".join("i%d" % j for j in range(n)) + nl + "".join("    %s" % ln + nl for ln in lines)
                    + "    return (%s,)" % ",".join(outs) + nl)
        ns = {}
        exec(compile(self.src, "<bitslice-step-n%d>" % n, "exec"), {}, ns)
        self.step = ns["step"]

    def _last(self):
        last = {}
        for k, (_, a, b) in enumerate(self.lines):
            for v in (a, b):
                last[v] = k
        return last

    def peak_live(self):
        """Largest number of live plane registers after one operation (inputs live at the start, a result may reuse the register
        of a dying operand, outputs live to the end)."""
        last, outs = self._last(), set(self.outs)
        live = {"i%d" % j for j in range(self.n)}
        peak = len(live)
        for k, (nm, a, b) in enumerate(self.lines):
            live.add(nm)
            live = {v for v in live if last.get(v, -1) > k or v == nm or v in outs}
            peak = max(peak, len(live))
        return peak

    def spill_ops(self, R):
        """Loads plus stores one step needs with R plane registers (Belady farthest-next-use; inputs beyond R start in memory)."""
        from bisect import bisect_left
        INF = 10 ** 10
        uses = {}
        for k, (_, a, b) in enumerate(self.lines):
            for v in (a, b):
                if v not in ("0", "#"):
                    uses.setdefault(v, []).append(k)
        outs = set(self.outs)

        def nxt(v, k):
            u = uses.get(v)
            if u:
                i = bisect_left(u, k)
                if i < len(u):
                    return u[i]
            return 10 ** 9 if v in outs else INF

        reg, mem, cost = {"i%d" % j for j in range(self.n)}, set(), 0
        if len(reg) > R:
            for v in sorted(reg, key=lambda y: -nxt(y, 0))[:len(reg) - R]:
                reg.discard(v)
                mem.add(v)
        for k, (nm, a, b) in enumerate(self.lines):
            need = [v for v in {a, b} if v not in ("0", "#")]
            for v in need:
                if v not in reg:
                    cost += 1
                    while len(reg) >= R:
                        w = max((y for y in reg if y not in need), key=lambda y: nxt(y, k))
                        reg.discard(w)
                        if w not in mem and nxt(w, k) < INF:
                            cost += 1
                            mem.add(w)
                    reg.add(v)
            for v in need:
                if nxt(v, k + 1) >= INF:
                    reg.discard(v)
            while len(reg) >= R:
                w = max(reg, key=lambda y: nxt(y, k + 1))
                reg.discard(w)
                if w not in mem and nxt(w, k + 1) < INF:
                    cost += 1
                    mem.add(w)
            reg.add(nm)
        return cost


# ---------------------------------------------------------------- 4 register allocation
def allocate(st):
    """Register assignment of the straight line: input plane j and output plane j both live in register j (the chain feed is
    renaming, no moves); temporaries take the lowest free register above n.  Returns (instructions as (op, dst, a, b) with
    register numbers, number of registers used).  Raises if output j would have to be written while input j is still needed."""
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


# ---------------------------------------------------------------- lane transposition, packing, extraction
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


# ---------------------------------------------------------------- 5 plan and ledger
LAMBDA = Fraction(497, 1000)       # 1 - exp(-LAMBDA) = 0.39165
CUTLOSS = Fraction(15, 100000)     # allowance for cut-trail points, as a fraction of Q
TAIL_AGES = 1e-6                   # probability that the 256 unfinished trails hold more than M * L points
CMAX = 2                           # halt when more than CMAX trails are cut (more is charged as failure)
EPS = 1e-3                         # Lemma 2 (proof 4): tail budget of the finished-trail count and of the trail sums, each
P_MIN = 0.390000001                # plan target; Appendix A proves P_F >= 0.39 exactly
HZ = 257 / 2                       # weight of a squared trail length in the trail sums
GRAIN = 10 ** 24                   # B is a multiple of GRAIN
STAGE1_PLANES = 32
# machine charges (proof 3.3)
LOOP_OPS = 3                       # batch counter increment, compare with the slice limit, branch
HIT_OPS = 2800                     # a stage-1 hit lane: store the 256 planes (256), extract the lane (2,304), window test and bookkeeping
EVENT_OPS = 3800                   # a finished trail: key, entry, insert the new start in memory (3,072), reload (256), bookkeeping
CUT_OPS = 4200                     # a cut trail: age scan share, insert (3,072), reload (256), bookkeeping
SLICE_OPS = 1300                   # slice check: 256 ages
RECOVER_EXTRA = 64                 # per recovery batch beyond the packed circuit (the exact test and loop need 29; call and 8 moves 10)
INSTR_BYTES = 36                   # opcode, registers and an inline 256-bit immediate
GEN_CODE = 2040                    # instructions of the runtime circuit generator (Gen, trace, Step.__init__, allocate: 2,036 bytecode instructions, `python3 bsrho.py --gencode`)
OTHER_CODE = 1810                  # instructions besides the main body: handlers 1,000, recovery 650 (603-operation circuit, test, loop, call, moves), setup, cut and slice 160
REGISTERS = 1024                   # declared register file of 256-bit words, counted as memory
REGFILE = REGISTERS * 32
COUNTERS = 16384                   # trail numbers, ages, counters (8 KiB) and the plane copy used by the handlers (8 KiB)
ENTRY = 25
MEM_LIMIT = 1 << 20
ADVICE = 0                         # bytes of nonuniform advice: none (the mask q is derived by the generator at setup)
TAIL_LOG2 = -40
KAPPA_256 = 11
GEN_FACTOR = 200                   # word operations charged per generator primitive call and per emitted line
GEN_SLOTS = 1 << 15                # slots of the hash-consing table (2 bytes each; load factor 0.58)
GEN_STATE = 10240                 # signal words of the trace (v, m, temporaries) 8,192 + outputs 2,048
SETUP_FIXED = 256 * 3100 + 20000   # 256 starts inserted in memory, reloaded, random word, counters
# reduced widths: s1, W, Tp, kappa
CFG = {18: dict(s1=2, W=0, Tp=1, kappa=12, Sb=4), 20: dict(s1=2, W=0, Tp=1, kappa=12, Sb=4),
       256: dict(s1=32, W=90, kappa=KAPPA_256, Sb=1 << 48)}


def stage1_ops(pin, s1):
    """Operations of the stage-1 test (mask of lanes whose s1 low digest bits are zero): OR over the positive planes, AND over
    the inverted planes, one complement if both kinds occur, one combine, one final complement; plus compare and branch."""
    npos = sum(1 for j in range(s1) if not pin[j])
    nneg = s1 - npos
    ops = max(npos - 1, 0) + max(nneg - 1, 0)
    if nneg:
        ops += 2 if npos else 1
    return ops + 1 + 2


def stage1(planes, s1, pin):
    """Mask of lanes whose s1 low digest bits are all zero."""
    nz = 0
    pos = [planes[j] for j in range(s1) if not pin[j]]
    neg = [planes[j] for j in range(s1) if pin[j]]
    if pos:
        acc = pos[0]
        for q in pos[1:]:
            acc |= q
        nz |= acc
    if neg:
        acc = neg[0]
        for q in neg[1:]:
            acc &= q
        nz |= acc ^ ALL
    return ALL ^ nz


def inflight_m(lanes=LANES, eps=TAIL_AGES):
    """Smallest integer M with P(sum of `lanes` exponential ages > M L) <= eps (Chernoff, exact in the exponent)."""
    m = lanes
    while True:
        x = m / lanes
        if exp(-lanes * (x - 1 - log(x))) <= eps:
            return m
        m += 1


INFLIGHT = inflight_m()


def _plan(n, Tp, kappa, tmax, Sb):
    c = CFG[n]
    s1, W = c["s1"], c["W"]
    N, D = 1 << n, s1 + W
    L = Fraction(1 << D, Tp)
    if n == 256:
        B = _b256(Tp, tmax, kappa, Sb)
    else:                                                     # reduced widths: the plan of the 18-bit experiment
        ureq = isqrt(2 * N * LAMBDA.numerator // LAMBDA.denominator) + 2
        num, den = ureq + INFLIGHT * L + 1, CUTLOSS.denominator
        q = -(-(num * den) // (den - CUTLOSS.numerator))
        B = -(-q // LANES)
    cc = -(-kappa * L.numerator // L.denominator)
    fb = (Tp - 1).bit_length()
    return dict(n=n, s1=s1, W=W, D=D, Tp=Tp, fb=fb, kb=min(64 - fb, n - D), L=L, N=N, Q=B * LANES, B=B, kappa=kappa, Sb=Sb,
                c=cc, capr=cc + Sb, tmax=tmax, e2max=2 * B * LANES // (1 << s1) + 64,
                cmax=CMAX if n == 256 else 10 ** 9)


def tail_log2(mean, k):
    """log2 of the Chernoff bound exp(-mean) (e mean / k)^k on P(count >= k), k > mean."""
    return (-mean + k * (1 + log(mean / k))) / log(2)


_STEP256 = {}


def step256():
    if 256 not in _STEP256:
        _STEP256[256] = Step(256)
    return _STEP256[256]


def machine_constants(st=None, R=REGISTERS):
    """(PH, FILT, BODY, code bytes, tmax) of the n = 256 program with R registers (spill loads and stores added to the body)."""
    st = st or step256()
    ph = st.ops
    filt = stage1_ops(st.pin, STAGE1_PLANES)
    body = ph + (st.spill_ops(R) if R < REGISTERS else 0) + filt + LOOP_OPS
    code = (body + OTHER_CODE) * INSTR_BYTES
    tmax = (MEM_LIMIT - code - R * 32 - COUNTERS - ADVICE) // ENTRY
    return ph, filt, body, code, tmax


def gen_scratch(nodes=None):
    """Peak scratch bytes of the runtime generator (nodes = nodes of the n = 256 network, peak over the polarity vectors tried).
    Trace phase: node table 4 bytes per node (2-bit op, two 15-bit operands), hash-consing table GEN_SLOTS x 2 bytes, signal state.
    Emit phase (the hash table is dead): node table, reachability mark 1 byte, last-use 4 bytes, register 2 bytes per node, heap and state."""
    nodes = nodes or len(trace(256)[0].nodes)
    assert nodes < 1 << 15
    trace_phase = 4 * nodes + 2 * GEN_SLOTS + GEN_STATE
    emit_phase = 11 * nodes + 2048 + GEN_STATE
    return max(trace_phase, emit_phase), trace_phase, emit_phase, nodes


def gen_idle(tmax):
    """Bytes of the region that holds the table, the register file, and the counters and plane copy once the search runs; while the generator
    runs the search has not started and the same region holds the generator's code image and its scratch."""
    return ENTRY * tmax + REGFILE + COUNTERS


def phase_bytes(code, tmax):
    """(setup phase, search phase) resident bytes.  Setup: main code (as large as the final code, written as the generator emits it), advice,
    the counters and plane copy, the generator's code image (GEN_CODE instructions) and its peak scratch.  Search: main code, advice, table,
    register file, counters.  The generator is never called after setup; its image and scratch are overwritten by the table and the register file."""
    scratch = gen_scratch()[0]
    return code + ADVICE + COUNTERS + GEN_CODE * INSTR_BYTES + scratch, code + ADVICE + COUNTERS + REGFILE + ENTRY * tmax

def plan(n, kappa=None, Tp=None, R=REGISTERS):
    if n != 256:
        c = CFG[n]
        p = _plan(n, c["Tp"], c["kappa"], 0, c["Sb"])
        p["tmax"] = 4 * (p["Q"] // int(p["L"])) + 64
        return p
    kappa = kappa or KAPPA_256
    tmax = machine_constants(None, R)[4]
    if Tp:
        return _plan(256, Tp, kappa, tmax, CFG[256]["Sb"])
    lo, hi = 1.0, float(tmax + 1)                        # largest mean number of trails the table holds
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if tail_log2(mid, tmax + 1) <= TAIL_LOG2 else (lo, mid)
    a, z = 1, 4097                                        # bisection: a Tp that reaches 0.39 at that mean (any Tp is a valid plan; not claimed optimal)
    while z - a > 1:
        m = (a + z) // 2
        a, z = (m, z) if _lossq(m, lo, tmax, kappa, CFG[256]["Sb"])["P_lower"] >= P_MIN else (a, m)
    return _plan(256, a, kappa, tmax, CFG[256]["Sb"])


def ledger(p=None, st=None, R=REGISTERS):
    """Operation budget in word operations (exact Fractions); units are operations / 638 (C of blake3-r3)."""
    p = p or plan(256, None, None, R)
    st = st or step256()
    ph, filt, body, code, _ = machine_constants(st, R)
    gen = GEN_FACTOR * (st.gen_calls + st.ops)
    parts = dict(main=body * p["B"],
                 slices=-(-p["B"] // p["Sb"]) * SLICE_OPS,
                 stage1_hits=p["e2max"] * HIT_OPS,
                 events=p["tmax"] * (EVENT_OPS + 3 * p["tmax"]),
                 cuts=p["cmax"] * CUT_OPS,
                 recovery=p["capr"] * (packed_circuit(st.qwords)[1] + RECOVER_EXTRA) + 600,
                 setup=SETUP_FIXED + gen)
    return dict(parts=parts, total=sum(parts.values()), plan=p, body=body, gen=gen)


def _zq(q, uc, uh, n):
    """Upper Chernoff quantile at EPS (units L^2) of n i.i.d. block terms (proof 4, Step 5): trapezoid rule on the convex exp(lam z(u) - u)."""
    k = 20000
    h = uc / k
    us = [i * h for i in range(k + 1)]
    zs = [HZ * u * u + 2 * q * max(0.0, u - uh) for u in us]

    def f(lam):
        a = [lam * z - u for z, u in zip(zs, us)]
        m = max(a)
        e = [exp(x - m) for x in a]
        return (n * (m + log(((sum(e) - (e[0] + e[-1]) / 2) * h + e[-1]) * (1 + 2.0 ** -30))) - log(EPS)) / lam
    lo, hi = -16.0, -4.0
    for _ in range(50):
        m1, m2 = lo + (hi - lo) / 3, hi - (hi - lo) / 3
        lo, hi = (lo, m2) if f(exp(m1)) < f(exp(m2)) else (m1, hi)
    return f(exp((lo + hi) / 2))


def _lossq(Tp, q, tmax, kappa, Sb, rate=1.0):
    """Lemma 2 v2 of proof Section 4 for q = Q / L trails; `rate` scales the collision hazard (H1 (d) sensitivity)."""
    L = Fraction(1 << 122, Tp)
    c = -(-kappa * L.numerator // L.denominator)
    uc, uh = float((c + Sb) / L), float((c // 2) / L)
    k = int(q) + 1
    while tail_log2(q, k) > log(EPS, 2) - 1e-6:           # N1 ~ Binomial(Q, 1/L) <= k - 1 except with prob. EPS
        k += 1
    nmax = k - 1 + LANES                                  # lottery blocks
    z = _zq(q, uc, uh, nmax)
    l2n = float(L * L / (1 << 256)) * rate                # L^2 / N, scaled
    kap = (2 * q * uc + HZ * uc * uc + 2 * q * (uc - uh)) * l2n   # cost of one colliding trail, over N
    w = 1.0
    for _ in range(100):
        w = exp(w * kap)                                  # ln w = w kap
    w *= 1 + 2.0 ** -40
    s0 = q * q / 2
    th = l2n * (w * (s0 - z - CMAX * (q * uc + min(q * (uc - uh), z / (LANES + 1) + q * float(Sb / L)))) - (w - 1) * s0)
    p, hq, ql, n2 = exp(-kappa), s0 * l2n, q * l2n, k + LANES + CMAX
    cuts = 1 - sum(comb(n2, j) * p ** j * exp((n2 - j) * log1p(-p)) for j in range(CMAX + 1))   # P(Bin(n2, p) > CMAX): fresh cut trails
    cuts += ql * (1 + (2 + kappa) * exp(-kappa / 2) + 2 * hq) + hq * p * (3 + 2 * kappa)       # colliding cut trails: S, X, J2a, J2b, Y
    t = dict(main=exp(-th), finished_count=EPS, trail_sums=EPS, cut_halt=cuts,
             collision_on_path=uc * q * l2n, key_false_match=tmax * (tmax - 1) / 2 * 2.0 ** -(min(64 - (Tp - 1).bit_length(), 134) + log(Tp, 2)),
             table_capacity=2.0 ** tail_log2(q, tmax - 59), long_finish=n2 * p * float(Sb / L), recovery_no_pair=2.0 ** -90)
    t["sum"] = sum(t.values())
    t["P_lower"] = 1 - t["sum"]
    t.update(theta=th, z=z, nmax=nmax, w=w, kap=kap, uc=uc, uh=uh, trails=q, k=k)
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


# ---------------------------------------------------------------- 6 search and recovery
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
    """Mixed distinguished point: low s1 bits zero and the window above them below Tp."""
    return x & ((1 << p["s1"]) - 1) == 0 and (x >> p["s1"]) & ((1 << p["W"]) - 1) < p["Tp"]


def dp_key(x, p):
    """The kb bits above the window, then the fb low bits of the window value (which determine it)."""
    return (((x >> p["D"]) & ((1 << p["kb"]) - 1)) << p["fb"]) | ((x >> p["s1"]) & ((1 << p["fb"]) - 1))


def pack_entry(key, t, length):
    assert key < 1 << 64 and t < 1 << 16 and length < 1 << 120
    return key | (t << 64) | (length << 80)


def unpack_entry(e):
    return e & ((1 << 64) - 1), (e >> 64) & 0xFFFF, e >> 80


def recover(p, r, a, b, f2):
    """a, b = (t, length) of two finished trails with the same end.  Returns (x, y), x != y, f(x) = f(y), or None.  The longer
    trail moves alone for l1 - l2 steps, then both move together (two lanes of the packed circuit)."""
    mask = p["N"] - 1
    if a[1] < b[1]:
        a, b = b, a
    if a[1] > p["capr"]:
        raise Halt("recovery length")
    xs = [(r + a[0]) & mask, (r + b[0]) & mask]
    for _ in range(a[1] - b[1]):
        xs[0] = f2([xs[0]])[0]
    if xs[0] == xs[1]:
        return None
    for _ in range(b[1] + 1):
        ya, yb = f2(xs)
        if ya == yb:
            return xs[0], xs[1]
        xs = [ya, yb]
    return None


def search(eng, p, r, cnt):
    """One attempt with the fresh random word r: the pair (x, y) or None.  Raises Halt at a budget.  Budgets: B batches,
    e2max stage-1 hits, tmax table keys, cmax cut trails, a recovery of at most capr batches."""
    n, mask, pin = p["n"], p["N"] - 1, eng.pin
    table, births, ts, nxt = {}, [0] * LANES, list(range(LANES)), LANES
    planes = pack_lanes([(r + t) & mask for t in ts], n, pin)
    cnt["inserts"] += LANES
    batches = 0
    while batches < p["B"]:
        planes = list(eng.step(*planes))
        batches += 1
        cnt["batches"] += 1
        hit = stage1(planes, p["s1"], pin)
        while hit:
            cnt["stage1_hits"] += 1
            if cnt["stage1_hits"] > p["e2max"]:
                raise Halt("stage-1 budget")
            l = (hit & -hit).bit_length() - 1
            hit &= hit - 1
            x = lane_value(planes, l, pin, n)
            if is_dp(x, p):
                key, length = dp_key(x, p), batches - births[l]
                cnt["finished"] += 1
                if key in table:
                    _, t0, l0 = unpack_entry(table[key])
                    cnt["recoveries"] += 1
                    res = recover(p, r, (t0, l0), (ts[l], length), eng.f2)
                    if res is None:
                        raise Halt("recovery found no pair")
                    return res
                if len(table) >= p["tmax"]:
                    raise Halt("table full")
                table[key] = pack_entry(key, ts[l], length)
                ts[l], nxt, births[l] = nxt, nxt + 1, batches
                planes = set_lane(planes, l, (r + ts[l]) & mask, pin, n)
                cnt["inserts"] += 1
        if batches % p["Sb"] == 0:
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


# ---------------------------------------------------------------- 7 organizer experiments
N_T3 = 18                          # width of the search experiment and of the ideal control
N_T1 = 12                          # width of the family-law runs (fresh key)
M_T2, B_T2 = 2048, 21              # points per trial, projection width (event: low 21 bits of the digest)
T2_NAMES = ("w0", "w3", "w7", "xor8", "sum8", "p01", "p23")


def t1_run(seed, n=N_T1):
    """Family law, fresh random key K: steps until the first repeat of x -> low n bits of digest(K || x)."""
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


_M21 = (1 << B_T2) - 1
_F21 = sum(_M21 << (32 * i) for i in range(8))
_KS = sum(1 << (32 * i) for i in range(8))


def t2_columns(digs):
    """The seven projections (T2_NAMES) of each 256-bit digest, as seven lists of B_T2-bit values:
    word 0, word 3, word 7, xor of the 8 words, sum of the 8 words, and two 22-bit concatenations of 11-bit pieces."""
    m = _M21
    folded = [d ^ (d >> 128) for d in digs]
    folded = [d ^ (d >> 64) for d in folded]
    return [[d & m for d in digs], [(d >> 96) & m for d in digs], [(d >> 224) & m for d in digs],
            [(d ^ (d >> 32)) & m for d in folded],
            [(((d & _F21) * _KS) >> 224) & m for d in digs],
            [((d & 0x7FF) | (((d >> 32) & 0x7FF) << 11)) & m for d in digs],
            [(((d >> 64) & 0x7FF) | (((d >> 107) & 0x7FF) << 11)) & m for d in digs]]


def e2_trial(seed, tr, st256):
    """T2: M_T2 points of the target function (the block 0^32 || x, K = 0) at width 256 (source by trial index: uniform inputs, counter r + i, or iterates of g
    from 256 random starts), the 256-bit digests f(x) = (stored planes) XOR q, equal pairs in seven 21-bit projections.  w0 is the checked event."""
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
    obs = {"source": src}
    pair = None
    for k, col in enumerate(t2_columns(digs)):
        name = T2_NAMES[k]
        obs["dup_" + name] = len(col) - len(set(col))
        if k == 0 and obs["dup_w0"]:
            first = {}
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


# ---------------------------------------------------------------- 8 command line
def selftest():
    import random
    ok = True
    rnd = random.Random(3)
    st = step256()
    print("n=256 step: ops", st.ops, "gates", st.gates, st.by, "peak live", st.peak_live(), "spill_ops(1024)", st.spill_ops(1024), "q weight", bin(st.qint).count("1"))
    code, regs = allocate(st)
    print("allocation: registers used", regs, "moves 0 (output j in register j)")
    pl0 = [rnd.getrandbits(256) for _ in range(256)]
    good = run_allocated(st, code, pl0) == list(st.step(*pl0))
    print("allocated code on a register file equals the step:", good)
    ok &= good
    # regression of the stored-plane step against the scalar 3-round compression: 4,096 lanes (16 batches of 256), full 256-bit g = f XOR q
    good, tot = True, 0
    for _ in range(16):
        xs = [rnd.getrandbits(256) for _ in range(LANES)]
        out = lanes_of(list(st.step(*pack_lanes(xs, 256, st.pin))), 256, st.pin)
        good &= all(out[l] == f_scalar(xs[l], 256) ^ st.qint for l in range(LANES))
        tot += LANES
    print("%d lanes, full 256-bit g = f XOR q, step vs scalar compression: %s" % (tot, good))
    ok &= good
    cur = list(xs)
    pl = pack_lanes(xs, 256, st.pin)
    for _ in range(3):
        pl = list(st.step(*pl))
        cur = [f_scalar(x, 256) ^ st.qint for x in cur]
    good = lanes_of(pl, 256, st.pin) == cur
    print("3 chained steps (256 lanes):", good)
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
    print("packed recovery circuit (%d ops, with the 8 XORs of q) vs scalar:" % packed_circuit(st.qwords)[1], good)
    ok &= good
    rows = [rnd.getrandbits(256) for _ in range(256)]
    good = transpose(transpose(rows)) == rows and (transpose(rows)[5] >> 9) & 1 == (rows[9] >> 5) & 1
    print("transpose:", good)
    ok &= good
    # the search at n = 18 finds recoverable collisions
    p = plan(N_T3)
    found = 0
    for s in range(6):
        res, cnt = attempt(e, p, "selftest/%d" % s, "t")
        if res is not None:
            found += 1
            ok &= res[0] != res[1] and f_scalar(res[0], N_T3) == f_scalar(res[1], N_T3)
    print("search n=%d: %d of 6 attempts returned a verified pair" % (N_T3, found))
    ok &= found > 0
    print("selftest", ok)
    return ok


def print_ledger(lg):
    from math import log2
    print({k: (str(v) if isinstance(v, Fraction) else v) for k, v in lg["plan"].items()})
    print("operations per batch (body)", lg["body"])
    for k, v in lg["parts"].items():
        print(k, v)
    print("N =", lg["total"])
    print("time_log2 = %.5f (unrounded %.8f)" % (log2(lg["total"] / 638) + 5e-6, log2(lg["total"] / 638)))


def stats(trials=256):
    """Run the two experiments locally on pseudo-random seeds and print the counts (descriptive only, no inference is drawn from them)."""
    from math import sqrt, pi
    seeds = [hashlib.sha256(("stats/%d" % i).encode()).hexdigest() for i in range(trials)]
    rows = serve({"experiment_id": "bsrho-n18", "trials": [{"trial": i, "seed": s} for i, s in enumerate(seeds)]})["trials"]
    N1 = 1 << N_T1
    tt = sum(r["observations"]["target_ok"] for r in rows)
    ii = sum(r["observations"]["ideal_ok"] for r in rows)
    print("T3 n=%d: attempts returning a verified pair: target %d of %d, ideal function %d of %d" % (N_T3, tt, trials, ii, trials))
    ts = [r["observations"]["t1_steps"] for r in rows]
    mean = sum(ts) / trials
    print("T1 n=%d fresh K: %d runs, mean first repeat %.2f (sqrt(pi N/2) = %.2f)" % (N_T1, trials, mean, sqrt(pi * N1 / 2)))
    seedl = [hashlib.sha256(("stats2/%d" % i).encode()).hexdigest() for i in range(trials)]
    r2 = serve({"experiment_id": "proj-k0-w256", "trials": [{"trial": i, "seed": s} for i, s in enumerate(seedl)]})["trials"]
    lam = M_T2 * (M_T2 - 1) / 2 / (1 << B_T2)
    print("T2 width 256, K=0: %d points, %d-bit projections, equal pairs per trial if uniform %.4f, trials with a pair if uniform %.4f" % (M_T2, B_T2, lam, 1 - exp(-lam)))
    for s in range(3):
        sel = [r for r in r2 if r["observations"]["source"] == s]
        line = []
        for name in T2_NAMES:
            tot = sum(r["observations"]["dup_" + name] for r in sel)
            line.append("%s %d (uniform reference %.1f)" % (name, tot, lam * len(sel)))
        hit = sum(1 for r in sel if r["message_a_hex"])
        print("  source %s (%d trials): returned pairs %d (uniform reference %.1f); " % (("uniform", "counter", "iterates")[s], len(sel), hit, (1 - exp(-lam)) * len(sel)) + "; ".join(line))
    return rows, r2


# ---------------------------------------------------------------- 9 the circuit generator in C
# The generator of section 3 and 4 (pivot adder, hash-consing, dead-code elimination, register allocation) written in freestanding C.  It was compiled to
# WebAssembly and run in a sandbox with 16 pages (1,048,576 bytes) of guest memory: it emits the same program as Gen/Step/allocate (proof 3.6).  `--gen-c` prints it.
GEN_C = r'''/* Freestanding C port of the bsrho.py circuit generator (Gen / trace(256) / Step DCE / allocate).
   No libc, no malloc, no imports.  Exports: run(), info_ptr(), code_ptr().
   Static memory map:
     code region  687,060 B (final main-code size of the entry; 36-byte records: op, dst, a, b as u16 LE)
     counters      16,384 B
     nodes          4 B/node  (2-bit op | 15-bit a | 15-bit b), op 0 xor, 1 and, 2 or, 3 leaf (node 0 const, 1..256 inputs)
     union scratch: trace phase  hash 2^15 x 2 B + signal state (v, m, tmp)
                    emit  phase  mark 1 B + last 4 B + reg 2 B per node + heap 1024 x 2 B
     outs[256] uint16 output signals (node<<1|neg)                                                       */
typedef unsigned char u8; typedef unsigned short u16; typedef unsigned int u32;

#ifndef NMAX
#define NMAX 17495
#endif
#define N 256
#define REC 36
#define CODE_BYTES 687060
#define CTR_BYTES 16384
#define HASHN 32768
#define HEAPN 1024

static u8 code[CODE_BYTES];
__attribute__((used)) static u8 counters[CTR_BYTES];
static u32 nodes[NMAX];
static u16 outs[N];

typedef struct { u16 hash[HASHN]; u16 v[16][32]; u16 m[16][32]; u16 tmp[32]; } TraceScr;
typedef struct { u8 mark[NMAX]; u32 last[NMAX]; u16 reg[NMAX]; u16 heap[HEAPN]; } EmitScr;
static union { TraceScr t; EmitScr e; } S;

static u32 nn, calls, err, hsz;
static struct {
  u32 ninst, nreg, nodes, calls, err, maxheap, maxprobe, hashfill; u8 q[32];
  u32 sz_code, sz_ctr, sz_nodes, sz_outs, sz_trace_scr, sz_emit_scr, sz_union, sz_hash, sz_state, sz_heap;
} info;

static const u32 IV[8] = {0x6A09E667u,0xBB67AE85u,0x3C6EF372u,0xA54FF53Au,0x510E527Fu,0x9B05688Cu,0x1F83D9ABu,0x5BE0CD19u};
static const u8 PERM[16] = {2,6,3,10,7,0,4,13,1,11,12,5,9,14,15,8};
static const u8 GC[8][4] = {{0,4,8,12},{1,5,9,13},{2,6,10,14},{3,7,11,15},{0,5,10,15},{1,6,11,12},{2,7,8,13},{3,4,9,14}};

#define ZERO 0
#define ONE 1

static u32 mk(u32 op, u32 a, u32 b) {
  calls++;
  if (a > b) { u32 t = a; a = b; b = t; }
  u32 key = (op << 30) | (a << 15) | b;
  u32 h = (key * 0x9E3779B1u) >> 17;           /* 15 bits */
  u32 probes = 0;
  for (;;) {
    u32 e = S.t.hash[h];
    if (e == 0) {
      if (nn >= NMAX) { err = 1; return 0; }
      nodes[nn] = key; S.t.hash[h] = (u16)nn;
      if (probes > info.maxprobe) info.maxprobe = probes;
      return nn++;
    }
    if (nodes[e] == key) { if (probes > info.maxprobe) info.maxprobe = probes; return e; }
    h = (h + 1) & (HASHN - 1); probes++;
  }
}
static u16 XOR(u16 x, u16 y) {
  calls++;
  if (!(x >> 1)) return (u16)(y ^ (x & 1));
  if (!(y >> 1)) return (u16)(x ^ (y & 1));
  if ((x >> 1) == (y >> 1)) return (u16)((x ^ y) & 1);
  u32 n = mk(0, x >> 1, y >> 1);
  return (u16)((n << 1) | ((x ^ y) & 1));
}
static u16 AND(u16 x, u16 y) {
  calls++;
  if (!(x >> 1)) return (x & 1) == 0 ? ZERO : y;
  if (!(y >> 1)) return (y & 1) == 0 ? ZERO : x;
  if ((x >> 1) == (y >> 1)) return x == y ? x : ZERO;
  if (!(x & 1) && !(y & 1)) return (u16)(mk(1, x >> 1, y >> 1) << 1);
  if ((x & 1) && (y & 1)) return (u16)((mk(2, x >> 1, y >> 1) << 1) | 1);
  u16 p = (x & 1) == 0 ? x : y, q = (x & 1) == 0 ? y : x;
  u16 an = (u16)(mk(1, p >> 1, q >> 1) << 1);
  return XOR(p, an);
}
static void fa(u16 a, u16 b, u16 c, u16 *sum, u16 *carry) {
  u16 ops[3] = {a, b, c}, vs[3]; u32 nv = 0, k = 0, nc = 0, cs[3] = {0, 0, 0};
  for (int i = 0; i < 3; i++) {
    if (!(ops[i] >> 1)) { cs[nc++] = ops[i] & 1; k ^= ops[i] & 1; } else vs[nv++] = ops[i];
  }
  if (nv == 3) {
    u16 p = 0, x = 0, y = 0;
    for (int pi = 0; pi < 3; pi++) {
      u16 o0 = vs[pi == 0 ? 1 : 0], o1 = vs[pi == 2 ? 1 : 2];
      if ((o0 & 1) == (o1 & 1)) { p = vs[pi]; x = o0; y = o1; break; }
    }
    u16 u = XOR(x, p);
    u16 s = XOR(u, y);
    u16 w = XOR(y, p);
    u16 an = AND(u, w);
    u16 cr = XOR(an, p);
    *sum = s; *carry = cr; return;
  }
  if (nv == 2) {
    u16 x = vs[0], y = vs[1];
    u16 t = XOR(x, y);
    u16 s = (u16)(t ^ k);
    if ((x & 1) == (y & 1)) {
      if (k == 0) { u16 cr = AND(x, y); *sum = s; *carry = cr; return; }
      u16 cr = AND((u16)(x ^ 1), (u16)(y ^ 1));
      *sum = s; *carry = (u16)(cr ^ 1); return;
    }
    u16 nt = (u16)(t ^ 1);
    u16 xx = (x & 1) == (nt & 1) ? x : y;
    if (k == 0) { u16 cr = AND(xx, nt); *sum = s; *carry = cr; return; }
    u16 cr = AND((u16)(xx ^ 1), (u16)(t ^ 1));
    *sum = s; *carry = (u16)(cr ^ 1); return;
  }
  if (nv == 1) {
    u16 x = vs[0]; u32 k1 = cs[0], k2 = cs[1];
    *sum = (u16)(x ^ k); *carry = (k1 == 1 && k2 == 1) ? ONE : (k1 == 0 && k2 == 0) ? ZERO : x; return;
  }
  u32 kk = cs[0] + cs[1] + cs[2];
  *sum = (kk % 2 == 0) ? ZERO : ONE; *carry = kk >= 2 ? ONE : ZERO;
}
static void add(const u16 *A, const u16 *B, u16 *out) {   /* out may alias A */
  u16 c = ZERO;
  for (int i = 0; i < 32; i++) {
    if (i == 31) { u16 t = XOR(A[i], B[i]); out[i] = XOR(t, c); }
    else { u16 si; fa(A[i], B[i], c, &si, &c); out[i] = si; }
  }
}
static void xorrot(u16 *D, const u16 *A, int r) {         /* D = ror_planes(xorw(D, A), r) */
  u16 *t = S.t.tmp;
  for (int i = 0; i < 32; i++) t[i] = XOR(D[i], A[i]);
  for (int i = 0; i < 32; i++) D[i] = t[(i + r) & 31];
}
static void constw(u16 *w, u32 val) { for (int i = 0; i < 32; i++) w[i] = (u16)((val >> i) & 1); }

static void trace(void) {
  u32 mi[16];
  for (int i = 0; i < HASHN; i++) S.t.hash[i] = 0;
  calls = 0;
  nodes[0] = 3u << 30; nn = 1;                                       /* const node 0 (leaf) */
  for (int j = 0; j < N; j++) nodes[nn++] = (3u << 30) | (u32)j;     /* input j -> node 1+j */
  for (int i = 0; i < 8; i++) constw(S.t.m[i], 0);
  for (int i = 0; i < 8; i++) for (int b = 0; b < 32; b++) S.t.m[8 + i][b] = (u16)((1 + 32 * i + b) << 1);
  for (int i = 0; i < 8; i++) constw(S.t.v[i], IV[i]);
  for (int i = 0; i < 4; i++) constw(S.t.v[8 + i], IV[i]);
  constw(S.t.v[12], 0); constw(S.t.v[13], 0); constw(S.t.v[14], 64); constw(S.t.v[15], 11);
  for (int i = 0; i < 16; i++) mi[i] = (u32)i;
  for (int r = 0; r < 3; r++) {
    for (int j = 0; j < 8; j++) {
      u32 a = GC[j][0], b = GC[j][1], c = GC[j][2], d = GC[j][3];
      const u16 *x = S.t.m[mi[2 * j]], *y = S.t.m[mi[2 * j + 1]];
      add(S.t.v[a], S.t.v[b], S.t.v[a]); add(S.t.v[a], x, S.t.v[a]);
      xorrot(S.t.v[d], S.t.v[a], 16);
      add(S.t.v[c], S.t.v[d], S.t.v[c]);
      xorrot(S.t.v[b], S.t.v[c], 12);
      add(S.t.v[a], S.t.v[b], S.t.v[a]); add(S.t.v[a], y, S.t.v[a]);
      xorrot(S.t.v[d], S.t.v[a], 8);
      add(S.t.v[c], S.t.v[d], S.t.v[c]);
      xorrot(S.t.v[b], S.t.v[c], 7);
    }
    u32 nm[16];
    for (int i = 0; i < 16; i++) nm[i] = mi[PERM[i]];
    for (int i = 0; i < 16; i++) mi[i] = nm[i];
  }
  for (int i = 0; i < 8; i++) for (int b = 0; b < 32; b++) outs[32 * i + b] = XOR(S.t.v[i][b], S.t.v[i + 8][b]);
}

static void hpush(u16 v) {
  if (hsz >= HEAPN) { err = 2; return; }
  u16 *h = S.e.heap; u32 i = hsz++;
  if (hsz > info.maxheap) info.maxheap = hsz;
  while (i > 0) { u32 p = (i - 1) >> 1; if (h[p] <= v) break; h[i] = h[p]; i = p; }
  h[i] = v;
}
static u16 hpop(void) {
  u16 *h = S.e.heap; u16 top = h[0]; u16 v = h[--hsz]; u32 i = 0;
  for (;;) {
    u32 c = 2 * i + 1; if (c >= hsz) break;
    if (c + 1 < hsz && h[c + 1] < h[c]) c++;
    if (h[c] >= v) break;
    h[i] = h[c]; i = c;
  }
  if (hsz) h[i] = v;
  return top;
}
static void put16(u8 *p, u32 v) { p[0] = (u8)v; p[1] = (u8)(v >> 8); }

__attribute__((export_name("info_ptr"))) u32 info_ptr(void) { return (u32)(unsigned long)&info; }
__attribute__((export_name("code_ptr"))) u32 code_ptr(void) { return (u32)(unsigned long)code; }

__attribute__((export_name("run"))) int run(void) {
  err = 0; info.maxprobe = 0; info.maxheap = 0;
  info.sz_code = sizeof code; info.sz_ctr = sizeof counters; info.sz_nodes = sizeof nodes; info.sz_outs = sizeof outs;
  info.sz_trace_scr = sizeof(TraceScr); info.sz_emit_scr = sizeof(EmitScr); info.sz_union = sizeof S;
  info.sz_hash = sizeof(((TraceScr *)0)->hash); info.sz_state = sizeof(TraceScr) - info.sz_hash; info.sz_heap = HEAPN * 2;
  trace();
  info.calls = calls; info.nodes = nn;
  if (err) { info.err = err; return 1; }
  for (int j = 0; j < N; j++) if (!(outs[j] >> 1)) { info.err = 3; return 3; }
  for (int j = 0; j < 32; j++) info.q[j] = 0;
  for (int j = 0; j < N; j++) info.q[j >> 3] |= (u8)((outs[j] & 1) << (j & 7));
  u32 fill = 0; for (u32 i = 0; i < HASHN; i++) fill += S.t.hash[i] != 0; info.hashfill = fill;
  /* emit phase reuses the scratch union */
  for (u32 k = 0; k < nn; k++) { S.e.mark[k] = 0; S.e.last[k] = 0xFFFFFFFFu; S.e.reg[k] = 0; }
  for (u32 j = 0; j < HEAPN; j++) S.e.heap[j] = 0;
  for (int j = 0; j < N; j++) S.e.mark[outs[j] >> 1] = 1;
  for (u32 k = nn - 1; k >= 1; k--) {
    if (S.e.mark[k] && (nodes[k] >> 30) != 3) { S.e.mark[(nodes[k] >> 15) & 0x7FFF] = 1; S.e.mark[nodes[k] & 0x7FFF] = 1; }
  }
  for (int j = 0; j < N; j++) { u32 nd = outs[j] >> 1; S.e.mark[nd] |= 2; S.e.reg[nd] = (u16)j; }   /* output flag; last j wins */
  for (int j = 0; j < N; j++) S.e.reg[1 + j] = (u16)j;                                           /* input plane j in register j */
  u32 ng = 0;
  for (u32 k = 1; k < nn; k++) {
    if (S.e.mark[k] && (nodes[k] >> 30) != 3) {
      S.e.last[(nodes[k] >> 15) & 0x7FFF] = ng; S.e.last[nodes[k] & 0x7FFF] = ng; ng++;
    }
  }
  /* register allocation, in node order */
  hsz = 0;
  u32 nxt = N, top = N, kk = 0;
  for (u32 k = 1; k < nn; k++) {
    u32 op = nodes[k] >> 30;
    if (!S.e.mark[k] || op == 3) continue;
    u32 a = (nodes[k] >> 15) & 0x7FFF, b = nodes[k] & 0x7FFF;
    u32 ra = S.e.reg[a], rb = S.e.reg[b];
    if (S.e.last[a] == kk && !(S.e.mark[a] & 2) && ra >= N) hpush((u16)ra);
    if (b != a && S.e.last[b] == kk && !(S.e.mark[b] & 2) && rb >= N) hpush((u16)rb);
    u32 d;
    if (S.e.mark[k] & 2) {
      d = S.e.reg[k];
      if ((int)S.e.last[1 + d] > (int)kk && S.e.last[1 + d] != 0xFFFFFFFFu) { info.err = 4; return 4; }
    } else if (hsz) d = hpop();
    else d = nxt++;
    S.e.reg[k] = (u16)d;
    if (d + 1 > top) top = d + 1;
    if (kk >= CODE_BYTES / REC) { info.err = 5; return 5; }
    u8 *rec = code + (u32)REC * kk;
    rec[0] = op == 0 ? '^' : op == 1 ? '&' : '|';
    put16(rec + 1, d); put16(rec + 3, ra); put16(rec + 5, rb);
    kk++;
  }
  info.ninst = kk; info.nreg = top; info.err = err;
  return err;
}
'''


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    if arg == "--selftest":
        sys.exit(0 if selftest() else 1)
    elif arg == "--ledger":
        print_ledger(ledger())
        from math import log2
        for R in (512, 256):
            lgR = ledger(None, None, R)
            print("fallback R = %d: spill ops per batch %d, body %d, tmax %d, Tp %d, time_log2 %.5f" % (
                R, step256().spill_ops(R), lgR["body"], lgR["plan"]["tmax"], lgR["plan"]["Tp"], log2(lgR["total"] / 638)))
        st = step256()
        ph, filt, body, code, tmax = machine_constants(st)
        print("PH", ph, "filter", filt, "body", body, "code bytes", code, "tmax", tmax, "generator calls", st.gen_calls)
        print("memory bytes", ENTRY * tmax + code + REGFILE + COUNTERS + ADVICE, "limit", MEM_LIMIT)
        sc = gen_scratch()
        ph1, ph2 = phase_bytes(code, tmax)
        print("setup phase bytes", ph1, "search phase bytes", ph2, "peak", max(ph1, ph2), "limit", MEM_LIMIT, "fits", max(ph1, ph2) <= MEM_LIMIT)
        print("generator scratch peak", sc[0], "(trace phase", sc[1], ", emit phase", sc[2], ", nodes", sc[3], ") idle region", gen_idle(tmax), "fits", sc[0] <= gen_idle(tmax), "generator code instructions", GEN_CODE)
        print("recovery circuit operations", packed_circuit(st.qwords)[1], "q (hex)", "%064x" % st.qint)
    elif arg == "--gencode":
        import dis, types
        def cnt(co):
            return sum(1 for _ in dis.get_instructions(co)) + sum(cnt(x) for x in co.co_consts if isinstance(x, types.CodeType))
        fs = (Gen.__init__, Gen.mk, Gen.XOR, Gen.AND, Gen.fa, Gen.add, Gen.xorw, _ror_planes, _constw, trace, Step.__init__, Step._last, allocate)
        print("bytecode instructions", sum(cnt(f.__code__) for f in fs), "GEN_CODE", GEN_CODE)
    elif arg == "--gen-c":
        sys.stdout.write(GEN_C)
    elif arg == "--loss":
        for k, v in loss(plan(256)).items():
            print(k, v)
    elif arg == "--sweep":
        from math import log2
        for kappa in range(8, 17):
            p = plan(256, kappa)
            lg = ledger(p)
            ls = loss(p)
            print("kappa", kappa, "Tp", p["Tp"], "tmax", p["tmax"], "time_log2 %.5f" % log2(lg["total"] / 638), "P_lower %.5f" % ls["P_lower"])
    elif arg == "--stats":
        stats()
    else:
        json.dump(serve(json.load(sys.stdin)), sys.stdout)
