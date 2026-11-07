"""Birthday collision search on 6-round BLAKE3-256 (blake3-r6, one block) with 256 bit-sliced lanes and distinguished points.

The message is 64 bytes: 32 zero bytes (words m0..m7) and x (words m8..m15, little endian), one block: chaining value IV, counter 0, length 64, flags 11 =
CHUNK_START|CHUNK_END|ROOT, 6 rounds with the message permutation between rounds.  f(x) is the 256-bit little-endian digest integer; the walk is on g(x) = f(x) XOR q,
q = the mask of the polarities of the stored digest planes (0 for the rolled program: the planes are stored upright).  n = 256 is the claim; the organizer experiments
run the same code at reduced n (the low n bits of g).
Sections: 1 scalar digest, 2 packed 7-lane tracer (recovery circuit), 3 bit-sliced generator (256 lanes, one plane per bit: rotations are renaming; full adders by
the pivot rule), 4 the rolled program (rounds 1-2 straight, rounds 3-6 a loop of one generic round) and its register allocation, 5 plan and ledger, 6 search and
recovery, 7 organizer experiments, 8 command line (--selftest --ledger --loss --stats --gen-c), 9 the circuit generator in C (GEN_C).
Credit: the pivot full adder and the mask walk are the method of jungjipdo's 6ae36351 (proof 3.3, 3.4), implemented here from its text; the rest is our program.
"""
import sys
import json
import hashlib
from fractions import Fraction
from math import isqrt, log, exp, expm1, log1p

M32 = 0xFFFFFFFF
IV = (0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19)
ROUNDS = 6                         # rounds of the target (blake3-r7-prefix-v1)
UNIT = 1262                         # organizer reference operation cost C of blake3-r7 (222, 430, 638, 846, 1054, 1262, 1470 for 1..7 rounds)
PERM = (2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8)
GCALLS = ((0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15),
          (0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14))
LANES, ALL = 256, (1 << 256) - 1
FLAGS = 11


# -------- 1 scalar digest
def _ror(v, k):
    return ((v >> k) | (v << (32 - k))) & M32


def digest_words(m, rounds=ROUNDS, flags=FLAGS, blen=64, counter=0):
    """One block m (16 words), chaining value IV, counter 0, length 64, flags 11: the 8 digest words v[i] XOR v[i+8] after `rounds` rounds."""
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


# -------- 2 packed tracer (recovery circuit)
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
    """The recovery circuit for the walk g = f XOR q: the plain 6-round compression of the block 0^32 || x followed by one XOR of each of the 8
    output words with the 32-bit word of q (a word that is 0 costs no operation).  qw = the 8 words of q."""
    tr = Tracer()
    v = [("c", w) for w in IV] + [("c", w) for w in IV[:4]] + [("c", 0), ("c", 0), ("c", 64), ("c", FLAGS)]
    m = [("c", 0)] * 8 + [("v", "i%d" % i, M32) for i in range(8, 16)]
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
            self.hits += 1                                   # a shared gate (none at the 6-round target: see selftest)
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
        """(sum, carry) of three planes by the pivot rule (the method of 6ae36351 proof 3.3, implemented here from its text): three variable planes: two of the three
        polarities agree, the third is the pivot p, the equal ones x and y; u = x ^ p, sum = u ^ y, carry = (u & (y ^ p)) ^ p: 5 gates.  One or two constant planes fold."""
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


def _rounds(g, v, m, k):
    """k rounds on the signal words v (16 words of 32 planes) with the message words m (16 words); returns v and the permuted m."""
    for _ in range(k):
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
    return v, m


# -------- 4 the rolled program and its register allocation
# Registers: x planes 0.., state words 256..767, message slots 768..1279, loop temporaries 1312.. Program: rounds 1-2 straight, complements, message slots of round 3,
# 5 times one generic round (every message slot a real operand), message slot permutation by plane copies (4 times), 256 output XORs.
XB, SB, WB, TB, KPRE = 0, 256, 768, 1312, 2
LOOPS = ROUNDS - KPRE
NONE = -1


def _segment(g, outs, pins, inreg, base):
    """Straight-line code of the network g: input node 1 + j in register inreg[j], output k in register pins[k] (an inverted plane gets one complement), temporaries
    from register base (freed at the last use, lowest free register first)."""
    import heapq
    nodes = g.nodes
    seen = set(t[0] for t in outs if t[0])
    for k in range(len(nodes) - 1, 0, -1):
        if k in seen and nodes[k][0] in "xao":
            seen.add(nodes[k][1])
            seen.add(nodes[k][2])
    order = [k for k in range(1, len(nodes)) if k in seen and nodes[k][0] in "xao"]
    last, pinned, reg = {}, {}, {1 + j: r for j, r in enumerate(inreg)}
    for t, k in enumerate(order):
        last[nodes[k][1]] = last[nodes[k][2]] = t
    for t, r in zip(outs, pins):
        if t[0]:
            pinned[t[0]] = r
    inat = {r: 1 + j for j, r in enumerate(inreg)}
    free, nxt, top, code = [], base, base, []
    for t, k in enumerate(order):
        op, a, b = nodes[k]
        ra, rb = reg[a], reg[b]
        for u in {a, b}:
            if last[u] == t and reg[u] >= base:
                heapq.heappush(free, reg[u])
        if k in pinned:
            d = pinned[k]
            if d in inat and last.get(inat[d], -1) > t:
                raise ValueError("input plane in register %d still needed" % d)
        elif free:
            d = heapq.heappop(free)
        else:
            d = nxt
            nxt += 1
        top = max(top, d + 1)
        reg[k] = d
        code.append(({"x": "^", "a": "&", "o": "|"}[op], d, ra, rb))
    for t, r in zip(outs, pins):
        if t[0] == 0:
            code.append(("o" if t[1] else "z", r, NONE, NONE))
        elif t[1]:
            code.append(("~", r, r, NONE))
    return code, top, len(nodes) - 1 - len(inreg) - len(order), g.hits, g.calls


def listing(n=256):
    """The program for the low n input planes: blocks A (rounds 1-2, complements, message slots of round 3), B (loop body), M (message permutation), F (output XORs) and
    the flat listing A, I, B, D, C, Z, M, J, F."""
    g = Gen(n)
    zero = _constw(0)
    m = [zero] * 8 + [[g.inputs[32 * i + b] if 32 * i + b < n else ZERO for b in range(32)] for i in range(8)]
    v = [_constw(w) for w in IV] + [_constw(w) for w in IV[:4]] + [zero, zero, _constw(64), _constw(FLAGS)]
    v, m = _rounds(g, v, m, KPRE)
    A, top1, dead1, hits1, c1 = _segment(g, [t for w in v for t in w], [SB + i for i in range(512)], [XB + j for j in range(n)], WB)
    for s in range(16):
        for b in range(32):
            t = m[s][b]
            A.append(("z", WB + 32 * s + b, NONE, NONE) if t[0] == 0 else ("=", WB + 32 * s + b, XB + t[0] - 1, NONE))
    g2 = Gen(1024)
    v2 = [[g2.inputs[32 * w + b] for b in range(32)] for w in range(16)]
    m2 = [[g2.inputs[512 + 32 * w + b] for b in range(32)] for w in range(16)]
    v2, _ = _rounds(g2, v2, m2, 1)
    Bc, top2, dead2, hits2, c2 = _segment(g2, [t for w in v2 for t in w], [SB + i for i in range(512)], [SB + j for j in range(1024)], TB)
    assert all(c[0] in "^&|" for c in Bc)
    M, seen = [], set()
    for s0 in range(16):                                      # slot s takes slot PERM[s]; one temporary word (registers TB..) per cycle
        if s0 in seen:
            continue
        cyc = [s0]
        while PERM[cyc[-1]] != s0:
            cyc.append(PERM[cyc[-1]])
        seen.update(cyc)
        M += [("=", TB + b, WB + 32 * s0 + b, NONE) for b in range(32)]
        for i, c in enumerate(cyc):
            M += [("=", WB + 32 * c + b, WB + 32 * cyc[i + 1] + b if i + 1 < len(cyc) else TB + b, NONE) for b in range(32)]
    F = [("^", j, SB + j, SB + 256 + j) for j in range(n)]
    ctl = lambda o: (o, NONE, NONE, NONE)
    flat = A + [ctl("I")] + Bc + [ctl("D"), ctl("C"), ctl("Z")] + M + [ctl("J")] + F
    ops = len(A) + 1 + LOOPS * (len(Bc) + 3) + (LOOPS - 1) * (len(M) + 1) + len(F)  # executed: I once, D C Z 5 times, J 4 times
    return dict(A=A, B=Bc, M=M, F=F, flat=flat, regs=max(top1, top2, TB + 32), dead=dead1 + dead2, hits=hits1 + hits2, calls=c1 + c2, ops=ops, instr=len(flat),
                nodes=max(len(g.nodes), len(g2.nodes)))


def run_listing(flat, planes, n, regs):
    """Interpreter of the flat listing (I sets the loop counter, D decrements, C compares, Z leaves the loop, J jumps back)."""
    R = [0] * (regs + 1)
    R[:n] = planes
    pc, cnt, flag, top = 0, 0, False, 0
    jend = max(i for i, c in enumerate(flat) if c[0] == "J")
    while pc < len(flat):
        op, d, a, b = flat[pc]
        pc += 1
        if op == "^":
            R[d] = R[a] ^ R[b]
        elif op == "&":
            R[d] = R[a] & R[b]
        elif op == "|":
            R[d] = R[a] | R[b]
        elif op == "=":
            R[d] = R[a]
        elif op == "~":
            R[d] = R[a] ^ ALL
        elif op == "z":
            R[d] = 0
        elif op == "o":
            R[d] = ALL
        elif op == "I":
            cnt, top = LOOPS, pc
        elif op == "D":
            cnt -= 1
        elif op == "C":
            flag = cnt == 0
        elif op == "Z" and flag:
            pc = jend + 1
        elif op == "J":
            pc = top
    return R[:n]


def _compile(code, K=2000):
    """Python functions f(R) executing the code on the register list R, in chunks of K lines (a single huge function needs 100 MB to compile)."""
    fns = []
    for s0 in range(0, len(code), K):
        ch, rd, wr, body = code[s0:s0 + K], [], set(), []
        for op, d, a, b in ch:
            for r in (a, b):
                if r >= 0 and r not in wr and r not in rd:
                    rd.append(r)
            body.append("r%d=" % d + {"^": "r%d^r%d" % (a, b), "&": "r%d&r%d" % (a, b), "|": "r%d|r%d" % (a, b), "=": "r%d" % a, "~": "r%d^ALL" % a, "z": "0", "o": "ALL"}[op])
            wr.add(d)
        src = "def c(R):\n" + ("    %s=%s\n" % (",".join("r%d" % r for r in rd), ",".join("R[%d]" % r for r in rd)) if rd else "")
        src += "".join("    %s\n" % x for x in body) + "".join("    R[%d]=r%d\n" % (r, r) for r in sorted(wr))
        ns = {"ALL": ALL}
        exec(compile(src, "<rolled-step>", "exec"), ns)
        fns.append(ns["c"])
    return fns


class Step:
    """The chain step for width n (256 lanes): step(*planes) maps the n upright input planes to the n output planes (digest planes upright, q = 0).  ops = operations
    executed by one step, instr = instructions of its code, regs = registers used."""

    def __init__(self, n=256):
        L = listing(n)
        self.n, self.pin, self.qint, self.qwords = n, [0] * n, 0, [0] * 8
        self.L, self.ops, self.instr, self.regs = L, L["ops"], L["instr"], L["regs"]
        self.hits, self.dead, self.gen_calls, self.flat = L["hits"], L["dead"], L["calls"], L["flat"]
        self.fa, self.fb, self.fm, self.ff = _compile(L["A"]), _compile(L["B"]), _compile(L["M"]), _compile(L["F"])

    def step(self, *x):
        R = [0] * self.regs
        R[:self.n] = x
        for f in self.fa:
            f(R)
        for i in range(LOOPS):
            for f in self.fb:
                f(R)
            if i < LOOPS - 1:
                for f in self.fm:
                    f(R)
        for f in self.ff:
            f(R)
        return tuple(R[:self.n])


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
LAMBDA = Fraction(497, 1000)       # 1 - exp(-LAMBDA) = 0.39165
CUTLOSS = Fraction(15, 100000)     # allowance for cut-trail points, as a fraction of Q
EPS = 1e-3                         # Lemma 2 (proof 4): tail budget of the finished-trail count and of the trail sums, each
P_MIN = 0.390000001                # plan target; Appendix A proves P_F >= 0.39 exactly
HZ = 257 / 2                       # weight of a squared trail length in the trail sums
GRAIN = 10 ** 24                   # B is a multiple of GRAIN
CMAX = 1                           # halt when more than CMAX trails are cut (more is charged as failure)
STAGE1_PLANES = 32
# machine charges (proof 3.3)
LOOP_OPS = 3                       # batch counter increment, compare with the slice limit, branch
HIT_OPS = 2800                     # a stage-1 hit lane (proof 3.3)
EVENT_OPS = 3800                   # a finished trail (proof 3.3)
CUT_OPS = 4200                     # a cut trail (proof 3.3)
SLICE_OPS = 1300                   # slice check: 256 ages
RECOVER_EXTRA = 64                 # per recovery batch beyond the packed circuit (proof 3.3)
RECOVER_PASSES = 2                 # pass 1 recomputes both trail lengths; pass 2 aligns and walks them; each at most capr batches
INSTR_BYTES = 36                   # opcode, registers and an inline 256-bit immediate
GEN_CODE = 2249                    # wasm instructions of GEN_C compiled with clang -Os, 36 bytes each
HANDLER_CODE, SETUP_CODE, RECOVERY_CODE = 1000, 160, 47   # handlers; setup, cut, slice; recovery
REGISTERS = 1856                   # declared register file of 256-bit words, counted as memory (the program uses 1,827, 29 spare)
REGFILE = REGISTERS * 32
COUNTERS = 16384                   # trail numbers, ages, counters (8 KiB) and the plane copy of the handlers (8 KiB)
ENTRY = 10                         # table entry: key 8 bytes, trail number 2; no length stored
MEM_LIMIT = 1048576                   # bytes: 2^20
SPARE = 64                         # bytes left unused under the limit
ADVICE = 0                         # bytes of nonuniform advice: none (the mask q is derived by the generator at setup)
TAIL_LOG2 = -40
KAPPA_256 = 13
GEN_FACTOR = 200                   # word operations charged per generator primitive call and per emitted line
GEN_STATE = 2432                   # generator state words (v 2,048, tmp, mw and the free-register bitmap 128 each)
GEN_STACK = 2048                   # shadow stack of the generator
GEN_INFO = 68                      # result record of the generator
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


INFLIGHT = 350                     # n = 18 plan only (sum of 256 exponential ages, units of L)


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


def other_code(st=None):
    """Instructions besides the main body: handlers 1,000, recovery (the packed circuit, plus 47), setup, cut and slice 160."""
    st = st or step256()
    return HANDLER_CODE + packed_circuit(st.qwords)[1] + RECOVERY_CODE + SETUP_CODE


def machine_constants(st=None):
    """(PH, FILT, BODY, code bytes, tmax) of the n = 256 program: PH = operations executed by one step, BODY = PH + filter + loop control (operations per batch),
    code bytes = 36 per instruction of the step, the filter, the batch loop and the other code."""
    st = st or step256()
    assert st.regs <= REGISTERS
    ph = st.ops
    filt = stage1_ops(st.pin, STAGE1_PLANES)
    body = ph + filt + LOOP_OPS
    code = (st.instr + filt + LOOP_OPS + other_code(st)) * INSTR_BYTES
    tmax = (MEM_LIMIT - SPARE - code - REGFILE - COUNTERS - ADVICE) // ENTRY
    return ph, filt, body, code, tmax


def gen_scratch(nodes=None):
    """Scratch bytes of the runtime generator (GEN_C, no node table): per node of the larger segment an 8-bit use count and a 16-bit pin, signal state, stack, result record."""
    nodes = nodes or step256().L["nodes"] + 1
    assert nodes < 1 << 16
    uses = 3 * nodes
    return uses + GEN_STATE + GEN_STACK + GEN_INFO, uses, nodes


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

def plan(n, kappa=None, Tp=None):
    if n != 256:
        c = CFG[n]
        p = _plan(n, c["Tp"], c["kappa"], 0, c["Sb"])
        p["tmax"] = 4 * (p["Q"] // int(p["L"])) + 64
        return p
    kappa = kappa or KAPPA_256
    tmax = machine_constants()[4]
    if Tp:
        return _plan(256, Tp, kappa, tmax, CFG[256]["Sb"])
    if tmax < 1:
        return None
    lo, hi = 1.0, float(tmax + 1)                        # largest mean number of trails the table holds
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if tail_log2(mid, tmax + 1) <= TAIL_LOG2 else (lo, mid)
    for t in range(400, 0, -1):                           # the largest Tp that reaches 0.39 at that mean
        if _lossq(t, lo, tmax, kappa, CFG[256]["Sb"])["P_lower"] >= P_MIN:
            return _plan(256, t, kappa, tmax, CFG[256]["Sb"])
    return None


def ledger(p=None, st=None):
    """Operation budget in word operations (exact Fractions); units are operations / 1262 (C of blake3-r6)."""
    p = p or plan(256)
    st = st or step256()
    ph, filt, body, code, _ = machine_constants(st)
    gen = GEN_FACTOR * (2 * st.gen_calls + st.instr)         # each segment is built twice; one line per instruction
    parts = dict(main=body * p["B"],
                 slices=-(-p["B"] // p["Sb"]) * SLICE_OPS,
                 stage1_hits=p["e2max"] * HIT_OPS,
                 events=p["tmax"] * (EVENT_OPS + 3 * p["tmax"]),
                 cuts=p["cmax"] * CUT_OPS,
                 recovery=RECOVER_PASSES * p["capr"] * (packed_circuit(st.qwords)[1] + RECOVER_EXTRA) + 600,
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
    """Lemma 2 of proof Section 4 for q = Q / L trails; `rate` scales the collision hazard (H1 (d) sensitivity)."""
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
    p, hq, ql, n2 = exp(-kappa), s0 * l2n, q * l2n, k + LANES + 1
    t = dict(main=exp(-th), finished_count=EPS, trail_sums=EPS,
             cut_halt=-expm1(n2 * log1p(-p)) - n2 * p * exp((n2 - 1) * log1p(-p)) + ql * (1 + (2 + kappa) * exp(-kappa / 2) + 2 * hq) + hq * p * (3 + 2 * kappa),
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


# -------- 6 search and recovery
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


def pack_entry(key, t):
    assert key < 1 << 64 and t < 1 << 16
    return key | (t << 64)


def unpack_entry(e):
    return e & ((1 << 64) - 1), (e >> 64) & 0xFFFF


def trail_lengths(p, r, ts, f2):
    """Pass 1 of the recovery: both trails (numbers ts) walk together from their starts, one packed batch per step, until each has
    reached a distinguished point; returns the two lengths.  More than capr steps is a halt."""
    mask = p["N"] - 1
    xs = [(r + ts[0]) & mask, (r + ts[1]) & mask]
    ls = [None, None]
    for k in range(1, p["capr"] + 1):
        xs = f2(xs)
        for i in (0, 1):
            if ls[i] is None and is_dp(xs[i], p):
                ls[i] = k
        if ls[0] is not None and ls[1] is not None:
            return ls
    raise Halt("recovery length")


def recover(p, r, t0, t1, f2):
    """t0, t1 = the numbers of two finished trails with the same end.  Returns (x, y), x != y, f(x) = f(y), or None.  Pass 1 recomputes
    the two lengths; pass 2: the longer trail moves alone for l1 - l2 steps, then both move together (two lanes of the packed circuit)."""
    mask = p["N"] - 1
    la, lb = trail_lengths(p, r, (t0, t1), f2)
    a, b = (t0, la), (t1, lb)
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
                    _, t0 = unpack_entry(table[key])
                    cnt["recoveries"] += 1
                    res = recover(p, r, t0, ts[l], eng.f2)
                    if res is None:
                        raise Halt("recovery found no pair")
                    return res
                if len(table) >= p["tmax"]:
                    raise Halt("table full")
                table[key] = pack_entry(key, ts[l])
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


# -------- 7 organizer experiments
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


# -------- 8 command line
def selftest():
    import random
    ok = True
    rnd = random.Random(3)
    st = step256()
    print("hash-consing hits", st.hits, "dead gates", st.dead, "(both must be 0)")
    ok &= st.hits == 0 and st.dead == 0
    L = st.L
    print("n=256 program: instructions", st.instr, "(A %d, B %d, M %d, F %d), operations per step %d, registers %d" % (len(L["A"]), len(L["B"]), len(L["M"]), len(L["F"]), st.ops, st.regs))
    pl0 = [rnd.getrandbits(256) for _ in range(256)]
    good = run_listing(st.flat, pl0, 256, st.regs) == list(st.step(*pl0))
    print("flat listing interpreted (loop control) equals the compiled step:", good)
    ok &= good
    # regression of the stored-plane step against the scalar 6-round compression: 4,096 lanes (16 batches of 256), full 256-bit g = f XOR q
    good, tot = True, 0
    for _ in range(16):
        xs = [rnd.getrandbits(256) for _ in range(LANES)]
        out = lanes_of(list(st.step(*pack_lanes(xs, 256, st.pin))), 256, st.pin)
        good &= all(out[l] == f_scalar(xs[l], 256) ^ st.qint for l in range(LANES))
        tot += LANES
    print("%d lanes, full 256-bit g = f XOR q, step vs scalar compression: %s" % (tot, good))
    ok &= good
    good = True
    for _ in range(16):
        cur = [rnd.getrandbits(256) for _ in range(LANES)]
        pl = pack_lanes(cur, 256, st.pin)
        for _ in range(7):
            pl = list(st.step(*pl))
            cur = [f_scalar(x, 256) ^ st.qint for x in cur]
        good &= lanes_of(pl, 256, st.pin) == cur
    print("4,096 lanes (16 x 256) chained for 7 steps, g = f XOR q vs scalar compression:", good)
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
    print("packed recovery circuit (%d ops) vs scalar:" % packed_circuit(st.qwords)[1], good)
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
    print("time_log2 = %.5f (unrounded %.8f)" % (log2(lg["total"] / UNIT) + 5e-6, log2(lg["total"] / UNIT)))


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


# -------- 9 the circuit generator in C
# The generator of sections 3 and 4 (pivot adder, rolled listing, register allocation) in freestanding C, two passes per segment, no node table (no segment has a shared or
# a dead gate).  Compiled to WebAssembly (clang -Os) and run with 16 pages (1,048,576 bytes) of guest memory it emits the same listing as listing() (proof 3.6).  `--gen-c` prints it.
GEN_C = r'''/* Freestanding C port of the bsrho.py generator of the rolled 6-round program (Gen, listing()), two passes per segment, no node table, no libc.  Exports run(), info_ptr(),
   code_ptr().  Segment 0 = rounds 1 and 2 (straight, outputs = 512 state planes in registers 256..767, temporaries from 768), then the complement of inverted planes, the
   message slots of round 3, the loop control, segment 1 = one generic round (state 256..767, message slots 768..1279, temporaries from 1312, outputs in place), the message
   permutation, the 256 output XORs.  No shared and no dead gate (hits 0, dead 0), so node numbers are creation order.  Pass 0 counts the uses of every node and records the
   register of every output node; pass 1 rebuilds the segment, an operand whose use count reaches 0 frees its register (temporaries only), a result takes its pinned register,
   else the lowest free one, else a new one.  Record = 36 bytes: op, dst, a, b as u16 LE (0xFFFF = none), rest zero.                                                          */
typedef unsigned char u8; typedef unsigned short u16; typedef unsigned int u32;

#ifndef NMAX
#define NMAX 10056                 /* nodes of the larger segment: constant 0, inputs, one per gate */
#endif
#ifndef CODE_BYTES
#define CODE_BYTES 804456
#endif
#define KPRE 2
#define N 256
#define SB 256
#define WB 768
#define TB 1312
#define REC 36
#define CTR_BYTES 16384
#define NODE(s) (((s) >> 1) & 0xFFFFu)
#define REG(s) ((s) >> 17)
#define ZERO 0u
#define ONE 1u
#define NONE 0xFFFFu

static u8 code[CODE_BYTES];
__attribute__((used)) static u8 counters[CTR_BYTES];
static u8 uses[NMAX];
static u16 pinreg[NMAX];
static u32 v[16][32], tmp[32], mw[32], fbits[32];

static u32 nn, calls, err, pass, kk, nxt, top, base, seg;
static struct { u32 ninst, nreg, nodes, calls, err, sz_code, sz_ctr, sz_uses, sz_state; u8 q[32]; } info;

static const u32 IV[8] = {0x6A09E667u,0xBB67AE85u,0x3C6EF372u,0xA54FF53Au,0x510E527Fu,0x9B05688Cu,0x1F83D9ABu,0x5BE0CD19u};
static const u8 PERM[16] = {2,6,3,10,7,0,4,13,1,11,12,5,9,14,15,8};
static const u8 GC[8][4] = {{0,4,8,12},{1,5,9,13},{2,6,10,14},{3,7,11,15},{0,5,10,15},{1,6,11,12},{2,7,8,13},{3,4,9,14}};

static void put16(u8 *p, u32 w) { p[0] = (u8)w; p[1] = (u8)(w >> 8); }
static void emit(u32 op, u32 d, u32 a, u32 b) {            /* one instruction record */
  if (kk >= CODE_BYTES / REC) { err = 5; return; }
  u8 *rec = code + (u32)REC * kk++;
  rec[0] = (u8)op; put16(rec + 1, d); put16(rec + 3, a); put16(rec + 5, b);
}
static void drop(u32 s) {                                   /* one use of operand s is consumed (pass 1) */
  u32 n = NODE(s), c = uses[n] - 1u;
  uses[n] = (u8)c;
  if (c == 0 && REG(s) >= base) { u32 r = REG(s) - base; fbits[r >> 5] |= 1u << (r & 31); }
}
static u32 mk(u32 op, u32 x, u32 y) {                       /* a new gate of the operands' nodes; returns the positive signal */
  calls++;
  if (NODE(x) > NODE(y)) { u32 t = x; x = y; y = t; }
  u32 id = nn++;
  if (id >= NMAX) { err = 1; return 0; }
  if (pass == 0) {
    u32 a = NODE(x), b = NODE(y);
    if (uses[a] == 255 || uses[b] == 255) { err = 6; return 0; }
    uses[a]++; uses[b]++;
    return id << 1;
  }
  u32 ra = REG(x), rb = REG(y), d;
  drop(x); drop(y);
  if (pinreg[id]) {
    d = pinreg[id];
    if (seg == 1 && uses[1 + d - SB] != 0) { err = 4; return 0; }    /* the input plane in this register is still needed after this gate */
  } else {
    u32 w = 0;
    while (w < 32 && fbits[w] == 0) w++;
    if (w < 32) { u32 b = 0; while (!((fbits[w] >> b) & 1u)) b++; fbits[w] &= ~(1u << b); d = base + 32 * w + b; }
    else d = nxt++;
  }
  if (d + 1 > top) top = d + 1;
  emit(op == 0 ? '^' : op == 1 ? '&' : '|', d, ra, rb);
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
    *sum = s; *carry = AND(xx ^ 1, t ^ 1) ^ 1; return;
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
static void xorrot(u32 *D, const u32 *A, int r) {         /* D = ror_planes(xorw(D, A), r) */
  for (int i = 0; i < 32; i++) tmp[i] = XOR(D[i], A[i]);
  for (int i = 0; i < 32; i++) D[i] = tmp[(i + r) & 31];
}
static void constw(u32 *w, u32 val) { for (int i = 0; i < 32; i++) w[i] = (val >> i) & 1u; }
static u32 inp(u32 j, u32 r) { return ((1 + j) << 1) | (r << 17); }   /* input node 1 + j living in register r */
static u32 *msg(u32 w) {                                     /* message word slot w: segment 0: word w of 0^32 || x; segment 1: the plane slot w in the registers 768.. */
  for (u32 b = 0; b < 32; b++) mw[b] = seg == 1 ? inp(512 + 32 * w + b, WB + 32 * w + b) : w < 8 ? ZERO : inp(32 * (w - 8) + b, 32 * (w - 8) + b);
  return mw;
}
static void rounds(u32 *mi, int nr) {
  u32 nm[16];
  for (int r = 0; r < nr; r++) {
    for (int j = 0; j < 8; j++) {
      u32 a = GC[j][0], b = GC[j][1], c = GC[j][2], d = GC[j][3];
      add(v[a], v[b], v[a]); add(v[a], msg(mi[2 * j]), v[a]);
      xorrot(v[d], v[a], 16);
      add(v[c], v[d], v[c]);
      xorrot(v[b], v[c], 12);
      add(v[a], v[b], v[a]); add(v[a], msg(mi[2 * j + 1]), v[a]);
      xorrot(v[d], v[a], 8);
      add(v[c], v[d], v[c]);
      xorrot(v[b], v[c], 7);
    }
    for (int i = 0; i < 16; i++) nm[i] = mi[PERM[i]];
    for (int i = 0; i < 16; i++) mi[i] = nm[i];
  }
}
static void outputs(void) {                                 /* the 512 state planes are the outputs of the segment: plane 32 w + b is pinned to register 256 + 32 w + b */
  for (u32 j = 0; j < 512; j++) {
    u32 s = v[j >> 5][j & 31];
    if (!NODE(s)) { err = 3; return; }
    if (pass == 0) pinreg[NODE(s)] = (u16)(SB + j);
    else if (s & 1) { if (seg == 0) emit('~', SB + j, SB + j, NONE); else err = 7; }   /* complement of a plane stored inverted */
  }
}
static void segment(u32 sg, int nr, u32 b0, u32 first) {
  u32 mi[16];
  seg = sg; base = b0;
  for (int p = 0; p < 2; p++) {
    pass = (u32)p; nn = first;
    if (p == 0) { for (u32 i = 0; i < NMAX; i++) { uses[i] = 0; pinreg[i] = 0; } }
    else { for (u32 i = 0; i < 32; i++) fbits[i] = 0; nxt = b0; }
    for (int i = 0; i < 16; i++) mi[i] = (u32)i;
    if (sg == 0) {
      for (int i = 0; i < 8; i++) constw(v[i], IV[i]);
      for (int i = 0; i < 4; i++) constw(v[8 + i], IV[i]);
      constw(v[12], 0); constw(v[13], 0); constw(v[14], 64); constw(v[15], 11);
    } else {
      for (u32 w = 0; w < 16; w++) for (u32 b = 0; b < 32; b++) v[w][b] = inp(32 * w + b, SB + 32 * w + b);
    }
    rounds(mi, nr);
    outputs();
    if (err) return;
  }
}

__attribute__((export_name("info_ptr"))) u32 info_ptr(void) { return (u32)(unsigned long)&info; }
__attribute__((export_name("code_ptr"))) u32 code_ptr(void) { return (u32)(unsigned long)code; }

__attribute__((export_name("run"))) int run(void) {
  u32 mi[16], nm[16];
  info.sz_code = sizeof code; info.sz_ctr = sizeof counters; info.sz_uses = sizeof uses + sizeof pinreg;
  info.sz_state = sizeof v + sizeof tmp + sizeof mw + sizeof fbits;
  err = 0; calls = 0; kk = 0; top = TB + 32;
  segment(0, KPRE, WB, 1 + N);                               /* nodes: the constant, 256 input planes, the gates */
  if (err) { info.err = err; return (int)err; }
  info.nodes = nn;
  for (int i = 0; i < 16; i++) mi[i] = (u32)i;               /* message planes of round 3: slot s holds word mi[s] of 0^32 || x */
  for (int r = 0; r < KPRE; r++) { for (int i = 0; i < 16; i++) nm[i] = mi[PERM[i]]; for (int i = 0; i < 16; i++) mi[i] = nm[i]; }
  for (u32 s = 0; s < 16; s++) for (u32 b = 0; b < 32; b++) {
    if (mi[s] < 8) emit('z', WB + 32 * s + b, NONE, NONE); else emit('=', WB + 32 * s + b, 32 * (mi[s] - 8) + b, NONE);
  }
  emit('I', NONE, NONE, NONE);
  segment(1, 1, TB, 1 + 1024);
  if (err) { info.err = err; return (int)err; }
  if (nn > info.nodes) info.nodes = nn;
  emit('D', NONE, NONE, NONE); emit('C', NONE, NONE, NONE); emit('Z', NONE, NONE, NONE);
  for (u32 s0 = 0; s0 < 16; s0++) {                          /* slot s takes slot PERM[s]; one temporary word per cycle, cycles in order of their least slot */
    u32 skip = 0, s1 = PERM[s0];
    while (s1 != s0) { if (s1 < s0) skip = 1; s1 = PERM[s1]; }
    if (skip) continue;
    for (u32 b = 0; b < 32; b++) emit('=', TB + b, WB + 32 * s0 + b, NONE);
    u32 cur = s0;
    for (;;) {
      u32 nx = PERM[cur];
      for (u32 b = 0; b < 32; b++) emit('=', WB + 32 * cur + b, nx == s0 ? TB + b : WB + 32 * nx + b, NONE);
      if (nx == s0) break;
      cur = nx;
    }
  }
  emit('J', NONE, NONE, NONE);
  for (u32 j = 0; j < N; j++) emit('^', j, SB + j, SB + 256 + j);
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
        print_ledger(ledger())
        from math import log2
        st = step256()
        ph, filt, body, code, tmax = machine_constants(st)
        print("PH", ph, "filter", filt, "body", body, "code bytes", code, "tmax", tmax, "generator calls (one pass)", st.gen_calls, "instructions", st.instr, "registers", st.regs)
        print("memory bytes", ENTRY * tmax + code + REGFILE + COUNTERS + ADVICE, "limit", MEM_LIMIT, "main code instructions", st.instr + filt + LOOP_OPS)
        sc = gen_scratch()
        ph1, ph2 = phase_bytes(code, tmax)
        print("setup phase bytes", ph1, "search phase bytes", ph2, "peak", max(ph1, ph2), "limit", MEM_LIMIT, "fits", max(ph1, ph2) <= MEM_LIMIT)
        print("generator scratch", sc[0], "(use counts", sc[1], ", nodes", sc[2], ") + image", GEN_CODE * INSTR_BYTES, "=", sc[0] + GEN_CODE * INSTR_BYTES, "idle region", gen_idle(tmax), "fits", sc[0] + GEN_CODE * INSTR_BYTES <= gen_idle(tmax), "generator code instructions", GEN_CODE)
        print("other code instructions", other_code(st), "step instructions", st.instr, "total instructions", st.instr + filt + LOOP_OPS + other_code(st))
        print("recovery circuit operations", packed_circuit(st.qwords)[1], "q (hex)", "%064x" % st.qint)
    elif arg == "--gen-c":
        sys.stdout.write(GEN_C)
    elif arg == "--loss":
        for k, v in loss(plan(256)).items():
            print(k, v)
    elif arg == "--stats":
        stats()
    else:
        json.dump(serve(json.load(sys.stdin)), sys.stdout)
