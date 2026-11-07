"""Birthday collision search on 3-round BLAKE3-256 (blake3-r3-prefix-v1) with 7 packed lanes and distinguished points.

The message is 128 bytes: a fixed 64-byte prefix P (the constant PREFIX below), 32 zero bytes (words m0..m7 of the last block) and x
(words m8..m15, little endian): one chunk of two blocks.  Block 1 is P (flags CHUNK_START = 1); block 2 is the last block (flags
CHUNK_END|ROOT = 10, counter 0, length 64) with chaining value CV = chain_value(P).  f(x) is the low n bits of the 256-bit
little-endian digest integer.  n = 256 is the claim; the organizer experiments run the same code with n = 22.
Sections: 1 scalar digest, 2 tracer (packed circuit, operation count, register high-water mark), 3 plan (every budget and
halt as exact integers) and ledger, 4 search (grouped filter with replay, mixed distinguished points, 25-byte table entries)
and recovery, 5 organizer protocol.
"""
import sys
import json
import hashlib
import re
from fractions import Fraction
from math import isqrt

M32 = 0xFFFFFFFF
IV = (0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19)
PERM = (2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8)
PITCH, LANES = 36, 7
REP = sum(1 << (PITCH * i) for i in range(LANES))
LIM = 1 << PITCH
ROUNDS = 3
GCALLS = ((0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15),
          (0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14))


# ---------------------------------------------------------------- 1 scalar digest
def _ror(v, k):
    return ((v >> k) | (v << (32 - k))) & M32


def chain_value(m, rounds=ROUNDS):
    """Chaining value of the first block of a chunk (non-root): the 16 words m, chaining value IV, counter 0, length 64,
    flags CHUNK_START = 1; output v[i] XOR v[i+8] for i < 8."""
    v = list(IV) + list(IV[:4]) + [0, 0, 64, 1]
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


# The prefix: the first 64-byte block of every message, little-endian words w0 = i, w1 = 0, ... (i = PREFIX_I); chosen by the
# search of proof.md Section 8 so that CV = chain_value(PREFIX) satisfies one 32-bit condition, A1 + B2 = 0 mod 2^32, where
# (A1, ., ., .) and (., B2, ., .) are the outputs of the round-0 column calls 1 and 2 on CV words (1, 5) and (2, 6) (see Section 8).
PREFIX_I = 10768619076
PREFIX = [PREFIX_I & M32, PREFIX_I >> 32] + [0] * 14
CV = chain_value(PREFIX)


def prefix_condition(cv=None):
    """(A1 + B2) mod 2^32 for the chaining value cv (default CV).  Round 0, column calls 1 and 2 of the last block start from
    (cv[j], cv[j+4], IV[j], D[j]) with D = (0, 0, 64, 10) and message words 0; A1 is v[1] after call 1 and B2 is v[6] after call 2.
    The first addition of diagonal call 5 of round 0 is v[1] + v[6] + m10, so A1 + B2 = 0 removes one addition from the circuit."""
    cv = CV if cv is None else cv
    D = (0, 0, 64, 10)

    def col(j):
        a, b, c, d = cv[j], cv[j + 4], IV[j], D[j]
        a = (a + b) & M32; d = _ror(d ^ a, 16); c = (c + d) & M32; b = _ror(b ^ c, 12)
        a = (a + b) & M32; d = _ror(d ^ a, 8); c = (c + d) & M32; b = _ror(b ^ c, 7)
        return a, b
    return (col(1)[0] + col(2)[1]) & M32


def digest_words(m, rounds=ROUNDS, flags=10, blen=64, counter=0, cv=None):
    """Last (root) compression of a chunk whose first block is PREFIX: 16 message words -> 8 digest words.
    Chaining value CV (default chain_value(PREFIX)), flags CHUNK_END|ROOT = 10."""
    v = list(CV if cv is None else cv) + list(IV[:4]) + [counter & M32, counter >> 32, blen, flags]
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


def f_scalar(x, n):
    """f(x): the low n bits of the digest of the message PREFIX || 0^32 || x (the 128-byte message of message(x))."""
    d = digest_words([0] * 8 + [(x >> (32 * i)) & M32 for i in range(8)])
    return sum(d[i] << (32 * i) for i in range(8)) & ((1 << n) - 1)


def message(x):
    return b"".join(w.to_bytes(4, "little") for w in PREFIX) + bytes(32) + x.to_bytes(32, "little")


# ---------------------------------------------------------------- 2 tracer
class Tracer:
    """Straight-line code over 256-bit words holding 7 lanes of 36 bits (32 data bits and 4 guard bits).
    A value is ('c', k), the same constant in every lane (folded at build time, no operation), or
    ('v', register, bound) with bound the largest value a lane can hold.  Every emitted line is one
    machine operation (add, and, or, xor, shl, shr; constants are immediates)."""

    def __init__(self):
        self.lines, self.ops, self.by, self.k = [], 0, {}, 0

    def emit(self, kind, expr):
        self.k += 1
        name = "t%d" % self.k
        self.lines.append("%s=%s" % (name, expr))
        self.ops += 1
        self.by[kind] = self.by.get(kind, 0) + 1
        return name

    def mask(self, a):
        return ("v", self.emit("and", "%s&%d" % (a[1], REP * M32)), M32)

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
            acc = ("v", self.emit("add", "%s+%s" % (acc[1], v[1])), acc[2] + v[2])
        if c:
            if acc[2] + c >= LIM:
                acc = self.mask(acc)
            acc = ("v", self.emit("add", "%s+%d" % (acc[1], REP * c)), acc[2] + c)
        return acc

    def xor(self, a, b):
        if a[0] == "c" and b[0] == "c":
            return ("c", a[1] ^ b[1])
        if a[0] == "c":
            a, b = b, a
        if b[0] == "c":
            if b[1] == 0:
                return a
            return ("v", self.emit("xor", "%s^%d" % (a[1], REP * b[1])),
                    (1 << max(a[2].bit_length(), b[1].bit_length())) - 1)
        return ("v", self.emit("xor", "%s^%s" % (a[1], b[1])),
                (1 << max(a[2].bit_length(), b[2].bit_length())) - 1)

    def ror(self, a, r):
        """Rotation of every lane by r: shr, and, shl, and, or.  The two masks also drop guard-bit garbage."""
        if a[0] == "c":
            return ("c", _ror(a[1], r))
        s1 = self.emit("shr", "%s>>%d" % (a[1], r))
        h = self.emit("and", "%s&%d" % (s1, REP * ((1 << (32 - r)) - 1)))
        s2 = self.emit("shl", "%s<<%d" % (a[1], 32 - r))
        lw = self.emit("and", "%s&%d" % (s2, REP * (((1 << r) - 1) << (32 - r))))
        return ("v", self.emit("or", "%s|%s" % (h, lw)), M32)


def build_hash():
    """Trace the 3-round digest of PREFIX || 0^32 || x for 7 lanes: source of batch(), operation count, count by kind."""
    tr = Tracer()
    v = [("c", w) for w in CV] + [("c", w) for w in IV[:4]] + [("c", 0), ("c", 0), ("c", 64), ("c", 10)]
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
        z = tr.xor(v[i], v[i + 8])
        if z[2] > M32:
            z = tr.mask(z)
        out.append(z[1])
    src = "def batch(%s):\n" % ",".join("i%d" % i for i in range(8, 16))
    src += "".join("    %s\n" % ln for ln in tr.lines) + "    return (%s,)\n" % ",".join(out)
    return src, tr.ops, dict(tr.by)


_SRC, PH, PH_BY = build_hash()
_ns = {}
exec(_SRC, {}, _ns)
batch = _ns["batch"]


NL = chr(10)


def _ops():
    """The emitted straight-line code as (result, operand a, operator, operand b); immediates are ints."""
    ops = []
    for ln in _SRC.split(NL)[1:-2]:
        name, expr = ln.strip().split("=", 1)
        a, op, b = re.match(r"^(\w+)(<<|>>|\+|&|\||\^)(\w+)$", expr).groups()
        ops.append((name, a, op, b))
    return ops


def _lastuse():
    last = {}
    for k, (n, a, op, b) in enumerate(_ops()):
        for v in (a, b):
            if not v.isdigit():
                last[v] = k
    for v in _SRC.strip().split(NL)[-1][len("    return ("):-2].split(","):
        last[v] = 10 ** 9
    return last


def peak_live():
    """Largest number of register values (inputs i8..i15 and temporaries) alive after one operation of a batch.
    Immediates (256-bit constants inside the instruction) are not registers; a result may reuse a dying operand's register."""
    last, live, peak = _lastuse(), {"i%d" % i for i in range(8, 16)}, 8
    for k, (n, a, op, b) in enumerate(_ops()):
        live.add(n)
        live = {v for v in live if last.get(v, -1) > k or v == n}
        peak = max(peak, len(live))
    return peak


def spill_ops(R):
    """Loads plus stores one batch needs on a machine with R registers (Belady's farthest-next-use rule; inputs start in
    registers, outputs must end in registers).  Immediates need no register."""
    ops, last = _ops(), _lastuse()
    uses = {}
    for k, (n, a, op, b) in enumerate(ops):
        for v in (a, b):
            if not v.isdigit():
                uses.setdefault(v, []).append(k)
    outs = set(_SRC.strip().split(NL)[-1][len("    return ("):-2].split(","))

    def nxt(v, k):
        for u in uses.get(v, []):
            if u >= k:
                return u
        return 10 ** 9 if v in outs else 10 ** 10

    reg, mem, cost = {"i%d" % i for i in range(8, 16)}, set(), 0
    for k, (n, a, op, b) in enumerate(ops):
        need = [v for v in (a, b) if not v.isdigit()]
        for v in need:
            if v not in reg:
                cost += 1                                   # load
                while len(reg) >= R:
                    w = max((y for y in reg if y not in need), key=lambda y: nxt(y, k))
                    reg.discard(w)
                    if w not in mem and nxt(w, k) < 10 ** 10:
                        cost += 1                           # store
                        mem.add(w)
                reg.add(v)
        for v in need:
            if nxt(v, k + 1) >= 10 ** 10:
                reg.discard(v)
        while len(reg) >= R:
            w = max(reg, key=lambda y: nxt(y, k + 1))
            reg.discard(w)
            if w not in mem and nxt(w, k + 1) < 10 ** 10:
                cost += 1
                mem.add(w)
        reg.add(n)
    return cost


def pack(vals):
    return sum(v << (PITCH * l) for l, v in enumerate(vals))


def lane(w, l):
    return (w >> (PITCH * l)) & M32


def lane_x(words, l):
    """The 8 words of lane l as one integer."""
    return sum(lane(words[i], l) << (32 * i) for i in range(8))


def pack_x(xs):
    """Packed input words i8..i15 for the lane values xs (at most 7 integers)."""
    return [pack([(x >> (32 * i)) & M32 for x in xs]) for i in range(8)]


def selftest():
    """The packed circuit against the scalar digest, 70 pseudo-random inputs."""
    h = hashlib.shake_256(b"rho-selftest").digest(70 * 32)
    for s in range(10):
        xs = [int.from_bytes(h[(7 * s + l) * 32:(7 * s + l + 1) * 32], "little") for l in range(7)]
        out = batch(*pack_x(xs))
        for l in range(7):
            if lane_x(out, l) != f_scalar(xs[l], 256):
                return False
    return True


# ---------------------------------------------------------------- 3 plan and ledger
U_UNROLL = 16                      # batches per loop body (one group); loop control is 3 operations per body, plus 1 register move
KAPPA = 12                         # trail age cap in units of L = 1/theta
LAMBDA = Fraction(497, 1000)       # 1 - exp(-LAMBDA) = 0.39165; the proof spends about 3e-4 of the 1.65e-3 above 0.39
INFLIGHT = 28                      # points of the 7 unfinished trails at the halt, in units of L (proof, Lemma 2)
CUTLOSS = Fraction(15, 100000)     # points on trails cut at the age cap, as a fraction of Q (proof, Lemma 2)
DP_EVENT_OPS = 700                 # one finished trail: lane extraction, fingerprint, restart (upper bound)
STAGE2_OPS = 300                   # the batch event itself when a lane of the filter word is zero (upper bound)
REPLAY_OPS = 300                   # per group replay besides its batches: 8 restores + 16 * (4 filter + 2 call/return + 8 moves + 3 loop) = 280, rounded up
RECOVER_EXTRA = 64                 # per recovery batch: 8 shr + 8 xor + 7 or + 1 and + compare + branch = 26, loop add + compare + branch = 3, 29 needed (proof 3.3)
ENTRY = 25                         # table entry bytes: key 8, trail number 2, length 15
RECOVERY_CODE, HANDLER_CODE, REPLAY_CODE = 640, 170, 40    # instructions besides the main body (proof 7)
INSTR_BYTES = 36                   # opcode, registers and an inline 256-bit immediate
COUNTERS, REGFILE = 2048, 2048     # bytes: counters and ages; 64 registers of 32 bytes, counted as memory as well
ADVICE = 32                        # bytes: the nonuniform advice, one 256-bit word holding PREFIX_I (proof 8); counted as memory
MEM_LIMIT = 1 << 20
TAIL_LOG2 = -40                    # table-capacity abort probability at most 2^-40
# Mixed distinguished points: x ends a trail iff its low s1 bits are zero and F = (x >> s1) mod 2^W is below Tp;
# density theta = Tp / 2^(s1 + W) and L = 1 / theta.  The key is the kb bits above the window followed by the fb low bits of F.
CFG = {256: dict(s1=32, W=90), 40: dict(s1=12, W=0, Tp=1), 32: dict(s1=8, W=0, Tp=1), 22: dict(s1=4, W=4, Tp=12, U=2),
       "32m": dict(s1=8, W=4, Tp=12), "40m": dict(s1=12, W=4, Tp=12)}   # "32m", "40m": the mixed predicate at the widths of the organizer experiments (section 5)


def body_ops(U, s1):
    """Operations of one loop body (U batches): batches, grouped filter, loop control and one move (proof 3.3)."""
    group = U * (1 + (1 if s1 < 32 else 0)) + (U - 1) + 3     # U adds [and U ands if s1 < 32], U-1 ands, 1 and, compare, branch
    return U * PH + group + 3 + 1


def _plan(n, Tp, tmax, key=None):
    c = CFG[n if key is None else key]
    s1, W, U = c["s1"], c["W"], c.get("U", U_UNROLL)
    N, D = 1 << n, c["s1"] + c["W"]
    L = Fraction(1 << D, Tp)
    ureq = isqrt(2 * N * LAMBDA.numerator // LAMBDA.denominator) + 2
    num, den = ureq + INFLIGHT * L + 1, CUTLOSS.denominator
    q = -(-(num * den) // (den - CUTLOSS.numerator))
    b = -(-q // LANES)
    b = -(-b // U) * U                                        # whole groups
    sb = (1 << 48) if n == 256 else 4 * U_UNROLL
    cc = -(-KAPPA * L.numerator // L.denominator)
    fb = (Tp - 1).bit_length()
    return dict(n=n, s1=s1, W=W, D=D, Tp=Tp, fb=fb, kb=min(64 - fb, n - D), L=L, N=N, U=U, Q=b * LANES, B=b, Sb=sb, c=cc,
                capr=cc + sb, tmax=tmax, e2max=2 * b * LANES // (1 << s1) + 64)


def code_bytes(n=256):
    return (body_ops(CFG[n].get("U", U_UNROLL), CFG[n]["s1"]) + RECOVERY_CODE + HANDLER_CODE + REPLAY_CODE) * INSTR_BYTES


def tail_log2(mean, k):
    """log2 of the Chernoff bound exp(-mean) * (e * mean / k)^k on P(count >= k) for a count that is binomial or Poisson, k > mean."""
    from math import log
    return (-mean + k * (1 + log(mean / k))) / log(2)


def plan(n, key=None):
    if n != 256:
        p = _plan(n, CFG[n if key is None else key]["Tp"], 0, key)
        p["tmax"] = 4 * (p["Q"] // int(p["L"])) + 64
        return p
    tmax = (MEM_LIMIT - code_bytes() - COUNTERS - REGFILE - ADVICE) // ENTRY
    best = None
    for Tp in range(1, 2049):                                 # the largest Tp whose table-capacity tail is within 2^TAIL_LOG2
        p = _plan(256, Tp, tmax)
        mean = float(p["Q"] / p["L"])
        if mean < tmax + 1 and tail_log2(mean, tmax + 1) <= TAIL_LOG2:
            best = p
    return best


def ledger(n=256, spill=0, spill_body=0):
    """Operation budget in word operations (exact Fractions); units are operations / 638 (C of blake3-r3).
    spill / spill_body: loads and stores added per batch circuit / per loop body on a machine with a small register file (proof 3.1)."""
    p = plan(n)
    ph = PH + spill
    per_body = body_ops(p["U"], p["s1"]) + p["U"] * spill + spill_body
    main = Fraction(per_body, p["U"]) * p["B"]
    parts = dict(main=main,
                 slices=-(-p["B"] // p["Sb"]) * 100,
                 stage2=p["e2max"] * (STAGE2_OPS + p["U"] * ph + REPLAY_OPS),
                 events=p["tmax"] * (DP_EVENT_OPS + 3 * p["tmax"]),
                 recovery=p["capr"] * (ph + RECOVER_EXTRA) + 600,
                 scan=scan_ops(),                              # preprocessing: the scan for PREFIX (section 6b, proof 8)
                 init=2000)                                    # setup: 1 random word, 7 starts <= 287, counters <= 25, folded constants <= 336 (proof 3.3)
    return dict(parts=parts, total=sum(parts.values()), plan=p, per_body=per_body)


def loss(p):
    """The probability losses of proof Section 4 (floats): the terms, their sum and the lower bound on the success probability."""
    from math import exp, factorial, log
    N, Q, L = p["N"], p["Q"], p["L"]
    x = float(LAMBDA)
    trails = float(Q / L)
    f1 = float(p["c"] / Q)                                 # one cut trail, as a fraction of Q
    mu = trails * exp(-KAPPA)
    pk = [exp(-mu) * mu ** j / factorial(j) for j in range(3)]
    slope = 2 * x * exp(-x)                                # dP = slope * dU / U
    cut = sum(pk[j] * max(0.0, j * f1 - float(CUTLOSS)) * slope for j in (1, 2)) + (1 - sum(pk)) * (1 - exp(-x))
    infl = exp(-INFLIGHT) * sum(INFLIGHT ** j / factorial(j) for j in range(7))
    inside = float(Q * L / N)
    keys = 2.0 ** -(p["kb"] + log(p["Tp"], 2))
    t = dict(unfinished=infl, cut_deficit=cut, inside_trail=inside, key_false_match=p["tmax"] * (p["tmax"] - 1) / 2 * keys,
             table_capacity=2.0 ** tail_log2(trails, p["tmax"] + 1), recovery_no_pair=2.0 ** -100)
    t["sum"] = sum(t.values())
    t["P_lower"] = 1 - exp(-x) - t["sum"]
    t["mean_cut_trails"], t["trails"], t["cut_one_trail"] = mu, trails, f1
    return t


# ---------------------------------------------------------------- 4 search and recovery
def feed(z, n):
    """Next inputs i8..i15 from the 8 digest words (n < 256 keeps the low n bits)."""
    out = []
    for i in range(8):
        lo = 32 * i
        if lo >= n:
            out.append(0)
        elif n - lo >= 32:
            out.append(z[i])
        else:
            out.append(z[i] & (REP * ((1 << (n - lo)) - 1)))
    return out


class Halt(Exception):
    pass


def is_dp(x, p):
    """Mixed distinguished point: low s1 bits zero and the window above them below Tp."""
    return x & ((1 << p["s1"]) - 1) == 0 and (x >> p["s1"]) & ((1 << p["W"]) - 1) < p["Tp"]


def dp_key(x, p):
    """The kb bits above the window, then the fb low bits of the window value (which determine it): the end of a trail."""
    return (((x >> p["D"]) & ((1 << p["kb"]) - 1)) << p["fb"]) | ((x >> p["s1"]) & ((1 << p["fb"]) - 1))


def pack_entry(key, t, length):
    """One table entry of ENTRY = 25 bytes: key 8 (64 bits), trail number 2 (16 bits), length 15 (120 bits)."""
    assert key < 1 << 64 and t < 1 << 16 and length < 1 << 120
    return key | (t << 64) | (length << 80)


def unpack_entry(e):
    return e & ((1 << 64) - 1), (e >> 64) & 0xFFFF, e >> 80


def recover(p, r, a, b):
    """a, b = (t, length) of two finished trails with the same end.  Returns (x, y), x != y, f(x) = f(y)."""
    n, mask = p["n"], p["N"] - 1
    if a[1] < b[1]:
        a, b = b, a                                    # a is the longer trail
    xs = [(r + a[0]) & mask, (r + b[0]) & mask]
    for _ in range(a[1] - b[1]):                       # only the longer trail moves
        xs[0] = lane_x(batch(*pack_x([xs[0]])), 0) & mask
    if xs[0] == xs[1]:
        return None
    for _ in range(b[1] + 1):
        z = batch(*pack_x(xs))
        ya, yb = lane_x(z, 0) & mask, lane_x(z, 1) & mask
        if ya == yb:
            return xs[0], xs[1]
        xs = [ya, yb]
    return None


def set_lane(z, l, x):
    out = list(z)
    for i in range(8):
        out[i] = (out[i] & ~(M32 << (PITCH * l))) | (((x >> (32 * i)) & M32) << (PITCH * l))
    return tuple(out)


def search(p, r, U=None):
    """One attempt with the fresh random word r: (pair or None, counters).  Raises Halt at a budget.
    A group is U batches run with only the grouped filter (one add and one and per batch).  If some batch of the group had a lane
    whose tested bits are zero, the group is replayed from its saved inputs, batch by batch, with the full bookkeeping.
    U = 1 is the per-batch search (every flagged batch is replayed at once)."""
    n, mask = p["n"], p["N"] - 1
    U = p["U"] if U is None else U
    bit32, s1mask, rep_ff = REP << 32, REP * ((1 << p["s1"]) - 1), REP * M32
    table, births, ts = {}, [0] * LANES, list(range(LANES))
    nxt = LANES
    cnt = dict(batches=0, stage2=0, finished=0, cut=0, replays=0)
    inp = pack_x([(r + t) & mask for t in ts])
    while cnt["batches"] < p["B"]:
        acc, zz = bit32, inp
        for _ in range(U):
            z = batch(*zz)
            acc &= (z[0] & s1mask) + rep_ff
            zz = feed(z, n)
        if acc & bit32 == bit32:                               # no lane of the group has its tested bits zero
            cnt["batches"] += U
            inp = zz
        else:
            cnt["replays"] += 1
            for _ in range(U):
                z = batch(*inp)
                cnt["batches"] += 1
                if ((z[0] & s1mask) + rep_ff) & bit32 != bit32:
                    cnt["stage2"] += 1
                    if cnt["stage2"] > p["e2max"]:
                        raise Halt("stage-2 budget")
                    for l in range(LANES):
                        x = lane_x(z, l) & mask
                        if is_dp(x, p):
                            key, length = dp_key(x, p), cnt["batches"] - births[l]
                            cnt["finished"] += 1
                            if key in table:
                                _, t0, l0 = unpack_entry(table[key])
                                res = recover(p, r, (t0, l0), (ts[l], length))
                                if res is None:
                                    raise Halt("recovery found no pair")
                                return res, cnt
                            if len(table) >= p["tmax"]:
                                raise Halt("table full")
                            table[key] = pack_entry(key, ts[l], length)
                            ts[l], nxt, births[l] = nxt, nxt + 1, cnt["batches"]
                            z = set_lane(z, l, (r + ts[l]) & mask)
                inp = feed(z, n)
        if cnt["batches"] % p["Sb"] == 0:
            for l in range(LANES):
                if cnt["batches"] - births[l] >= p["c"]:
                    cnt["cut"] += 1
                    ts[l], nxt, births[l] = nxt, nxt + 1, cnt["batches"]
                    inp = set_lane(inp, l, (r + ts[l]) & mask)
    return None, cnt


# ---------------------------------------------------------------- 5 organizer protocol
def run_trial(seed, n=22, attempts=60):
    p = plan(n)
    obs = dict(attempts=0, batches=0)
    for a in range(attempts):
        r = int.from_bytes(hashlib.shake_256(("%s/%d" % (seed, a)).encode()).digest(32), "little") & (p["N"] - 1)
        obs["attempts"] += 1
        try:
            res, cnt = search(p, r)
        except Halt:
            continue
        obs["batches"] += cnt["batches"]
        if res is not None:
            return message(res[0]), message(res[1]), obs
    return None, None, obs


# T3 of proof section 5 on this program, run by the organizer: the shipped search, one attempt per trial with plan(n) of the mixed setting
# (grouped filter with 16 batches per group, DP = low s1 bits zero and the 4 bits above them below 12, 25-byte entries, 7 lanes).  Only the
# first `count` trials of an experiment run an attempt (time limit of the organizer's runner); the other trials return two nulls.
# id: (width n, setting, attempts)
EXPERIMENTS = {"rho-n32-a": (32, "32m", 24), "rho-n32-b": (32, "32m", 24), "rho-n32-c": (32, "32m", 24),
               "rho-n40-a": (40, "40m", 2), "rho-n40-b": (40, "40m", 2), "rho-n40-c": (40, "40m", 2), "rho-n40-d": (40, "40m", 2)}


def run_attempt(seed, n, key):
    p = plan(n, key)
    r = int.from_bytes(hashlib.shake_256(("%s/0" % seed).encode()).digest(32), "little") & (p["N"] - 1)
    obs = dict(attempts=1, halted=0, batches=0, stage2=0, finished=0, replays=0)
    try:
        res, cnt = search(p, r)
    except Halt:
        obs["halted"] = 1
        return None, None, obs
    for k in ("batches", "stage2", "finished", "replays"):
        obs[k] = cnt[k]
    if res is None:
        return None, None, obs
    return message(res[0]), message(res[1]), obs


def main():
    req = json.load(sys.stdin)
    ex = EXPERIMENTS.get(req.get("experiment_id"))
    out = []
    for t in req["trials"]:
        if ex is None:
            a, b, obs = run_trial(t["seed"])
        elif t["trial"] < ex[2]:
            a, b, obs = run_attempt(t["seed"], ex[0], ex[1])
        else:
            a, b, obs = None, None, dict(attempts=0)
        out.append({"trial": t["trial"], "message_a_hex": a.hex() if a else None,
                    "message_b_hex": b.hex() if b else None, "observations": obs})
    json.dump({"schema_version": 1, "trials": out}, sys.stdout)


def attack():
    """The claimed attack, n = 256 (not run here): one attempt, one fresh uniform 256-bit word r."""
    import os
    res, _ = search(plan(256), int.from_bytes(os.urandom(32), "little"))
    return None if res is None else (message(res[0]), message(res[1]))


def equivalence(seeds=24):
    """The grouped search against the per-batch search (U = 1) at n = 22 on pseudo-random starts: identical pairs and counters."""
    p = plan(22)
    for s in range(seeds):
        r = int.from_bytes(hashlib.shake_256(b"equiv/%d" % s).digest(32), "little") & (p["N"] - 1)
        out = []
        for U in (p["U"], 1):
            try:
                res, cnt = search(p, r, U)
            except Halt as e:
                res, cnt = str(e), {}
            out.append((res, {k: v for k, v in cnt.items() if k not in ("replays",)}))
        if out[0] != out[1]:
            return False
    return True


def _print_ledger(lg):
    from math import log2
    print({k: (str(v) if isinstance(v, Fraction) else v) for k, v in lg["plan"].items()})
    print("operations per body of %d batches" % lg["plan"]["U"], lg["per_body"])
    for k, v in lg["parts"].items():
        print(k, v, "=", float(v))
    print("total operations", lg["total"], "=", float(lg["total"]))
    print("units (total / 638) =", float(lg["total"] / 638), "; time_log2 =", log2(lg["total"] / 638))


# ---------------------------------------------------------------- 6 the prefix scan (preprocessing) and the memory layout
# The scan that selected PREFIX (proof Section 8).  Candidate i = 0, 1, 2, ... gives the first block P(i) (words w0 = i mod 2^32,
# w1 = i >> 32, the rest 0); the scan computes CV(i) = chain_value(P(i)) and tests the condition (A1 + B2) mod 2^k = 0 of
# prefix_condition (k = 32 for the shipped prefix); it stops at the first i that passes and stores i as the advice word.
# Operations per candidate on the machine of proof 3.1 (every one counted, in the same unit as the attack):
SCAN_GEN = 5          # i += 1; w0 = i AND 0xFFFFFFFF; w1 = i >> 32; 2 register moves of w0, w1 into the message registers
SCAN_INIT = 16        # the 16 state words of the compression are set (IV words, counter 0, 0, length 64, flags 1): 16 immediates/moves
SCAN_COMPRESS = 638   # C of blake3-r3: the organizer's reference count of one 3-round compression (with feed-forward), uncut
SCAN_COND = 56        # two full G calls on the CV words (1, 5) and (2, 6), at most 26 operations each = 52; A1 + B2 (1); AND with 2^k - 1 (1);
                      # compare with 0 (1); conditional branch (1)
SCAN_LOOP = 2         # unconditional jump back (1) and one spare (1): the exit is the condition branch above (no separate limit test)
SCAN_PER = SCAN_GEN + SCAN_INIT + SCAN_COMPRESS + SCAN_COND + SCAN_LOOP
SCAN_END = 1          # one store of the found i into the advice word
# Live words in the scan: 16 message + 16 state + 8 for the CV scratch and the counter = 40 <= 64 registers; no load or store in the scan.


def scan_prefix(k, start=0, limit=None):
    """First candidate i >= start whose chain value satisfies (A1 + B2) mod 2^k = 0; returns (i, candidates examined)."""
    mask = (1 << k) - 1
    i = start
    while limit is None or i < limit:
        cv = chain_value([i & M32, i >> 32] + [0] * 14)
        if prefix_condition(cv) & mask == 0:
            return i, i - start + 1
        i += 1
    return None, i - start


def scan_ops(candidates=None):
    """Operations of the full scan for the shipped prefix: (PREFIX_I + 1) candidates of SCAN_PER operations, plus the final store."""
    c = PREFIX_I + 1 if candidates is None else candidates
    return c * SCAN_PER + SCAN_END


def scan_report(k=16):
    """Reruns the same scan at the reduced condition mod 2^k and checks the shipped prefix against the full condition (mod 2^32)."""
    from math import log2
    i, n = scan_prefix(k)
    full = prefix_condition(chain_value(PREFIX)) == 0
    print("reduced scan, condition mod 2^%d: first i = %d after %d candidates (expected about 2^%d = %d); ops %d" % (k, i, n, k, 1 << k, scan_ops(n)))
    print("shipped prefix i = %d satisfies the 32-bit condition: %s" % (PREFIX_I, full))
    print("full scan: %d candidates x %d ops + %d = %d ops = %.4f units = 2^%.4f" % (PREFIX_I + 1, SCAN_PER, SCAN_END, scan_ops(),
          scan_ops() / 638, log2(scan_ops() / 638)))


def layout():
    """The concrete memory map of the abstract machine, as (name, offset, bytes, contents); offsets in bytes from 0.  Raises if it does not
    fill 2^20 bytes exactly."""
    p = plan(256)
    t = p["tmax"]
    body = body_ops(U_UNROLL, 32)
    rows, off = [], 0

    def add(name, size, what):
        nonlocal off
        rows.append((name, off, size, what))
        off += size
    add("code: main body", body * INSTR_BYTES, "%d instructions x %d bytes (opcode, registers, inline 256-bit immediate): 16 batches of %d, the grouped filter, loop control; every circuit constant, including those derived from the prefix, is an immediate here" % (body, INSTR_BYTES, PH))
    add("code: batch subroutine, recovery", RECOVERY_CODE * INSTR_BYTES, "%d instructions: the batch circuit as a subroutine (replay and recovery), the recovery walk with its equality test" % RECOVERY_CODE)
    add("code: handlers", HANDLER_CODE * INSTR_BYTES, "%d instructions: stage-2 event, window test, finished-trail store, key scan, restart, slice check, output of the two messages, halts" % HANDLER_CODE)
    add("code: replay control", REPLAY_CODE * INSTR_BYTES, "%d instructions: restore of the group's saved inputs, replay loop" % REPLAY_CODE)
    assert off == code_bytes()
    add("counters and ages", COUNTERS, "64 words, map below")
    add("register file", REGFILE, "64 registers of 32 bytes (counted as memory); the main loop uses 34, the rest hold event temporaries")
    add("advice word", ADVICE, "one 256-bit word: PREFIX_I (34 significant bits); P and CV are derived from it, the output of P is written from it")
    tab = -(-ENTRY * t // 32) * 32
    add("table block", tab, "%d entries x %d bytes = %d bytes in %d whole words, %d bytes unused; sub-map below" % (t, ENTRY, ENTRY * t, tab // 32, tab - ENTRY * t))
    assert off == MEM_LIMIT, (off, MEM_LIMIT)
    base = rows[-1][1]
    assert (8 * t) % 32 == 0 and (8 * t) % 2 == 0 and 25 * t <= tab
    table = [("keys, 8 bytes each, 4 per word", base, 8 * t),
             ("trail numbers, 2 bytes each", base + 8 * t, 2 * t),
             ("lengths, 15 bytes each", base + 10 * t, 15 * t)]
    cw = [("0", "batch counter b (256-bit)"), ("1", "stage-2 event counter"), ("2", "finished-trail count (table fill) and slice counter"),
          ("3-9", "start batch of the trail in each of the 7 lanes (age = b - start)"), ("10-16", "trail number t of each of the 7 lanes"),
          ("17", "the fresh random word r, retained for the starts r + t"), ("18", "next trail index t'"),
          ("19-20", "recovery: the two trail starts"), ("21-22", "recovery: the two lengths and the step counter"),
          ("23", "replay counter and return address of the batch subroutine"),
          ("24-27", "output buffer, message A: P (2 words, built from the advice word), 32 zero bytes, x"),
          ("28-31", "output buffer, message B: P, 32 zero bytes, y"), ("32-39", "event temporaries (window test, key, entry fields)"),
          ("40-63", "reserved: temporaries of the length straddle, the key scan and the halts")]
    return rows, table, cw


def layout_report():
    rows, table, cw = layout()
    for name, off, size, what in rows:
        print("%-36s offset %9d size %9d end %9d  %s" % (name, off, size, off + size, what))
    print("total", rows[-1][1] + rows[-1][2], "limit", MEM_LIMIT)
    base = rows[-1][1]
    for name, off, size in table:
        print("  table: %-32s offset %9d (block +%7d) size %9d" % (name, off, off - base, size))
    for w, what in cw:
        print("  counters word %-6s %s" % (w, what))


def memory_layout():
    """The table as one block of whole 256-bit words (proof section 7): keys, then trail numbers, then lengths, byte-contiguous."""
    p = plan(256)
    t = p["tmax"]
    words = -(-ENTRY * t // 32)
    fixed = code_bytes() + COUNTERS + REGFILE + ADVICE
    return dict(tmax=t, key_words=-(-t // 4), table_bytes=ENTRY * t, table_words=words, unused_bytes=32 * words - ENTRY * t,
                total_in_words=fixed + 32 * words, limit=MEM_LIMIT)


def h1_report(per_n=(("32m", 32, 60), ("40m", 40, 6))):
    """Prints the register count, the memory layout and the T3 statistics of the organizer experiments (own seeds, same code path)."""
    from math import exp, sqrt
    print("registers: one batch", peak_live(), "live values; with the group's 8 saved input words and the filter accumulator", peak_live() + 9)
    print("memory layout:", memory_layout())
    for key, n, k in per_n:
        p = plan(n, key)
        ok = halts = 0
        for i in range(k):
            a, b, obs = run_attempt("h1/%d/%d" % (n, i), n, key)
            ok += a is not None
            halts += obs["halted"]
        design = 1 - exp(-float(LAMBDA))
        birthday = 1 - exp(-p["Q"] ** 2 / (2 * p["N"]))
        se = sqrt(birthday * (1 - birthday) / k)
        print("n = %d (%s): Q = %d evaluations, %d attempts, %d successes (%.3f), %d halts; design value %.3f, pure-birthday value %.3f, z against %.3f: %.2f"
              % (n, key, p["Q"], k, ok, ok / k, halts, design, birthday, birthday, (ok / k - birthday) / se))


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    if arg == "--selftest":
        print("selftest", selftest(), "ops per batch", PH, PH_BY)
        print("prefix condition (A1 + B2) mod 2^32 =", prefix_condition(), "; CV =", CV)
        print("peak live register values in one batch", peak_live(), "; with the group's 8 saved inputs and the filter accumulator", peak_live() + 9)
        print("grouped search equals per-batch search at n=22:", equivalence())
    elif arg == "--ledger":
        _print_ledger(ledger(256))
        p = plan(256)
        print("memory bytes", ENTRY * p["tmax"] + code_bytes() + COUNTERS + REGFILE + ADVICE, "limit", MEM_LIMIT)
    elif arg == "--scan":
        scan_report()
    elif arg == "--layout":
        layout_report()
    elif arg == "--h1":
        h1_report()
    elif arg == "--loss":
        for k, v in loss(plan(256)).items():
            print(k, v)
    elif arg == "--spill":
        from math import log2
        base = ledger(256)
        for R in (64, 32, 24, 20, 16):
            sp = spill_ops(R)
            lg = ledger(256, sp, 40 if sp else 0)
            print("R =", R, "loads+stores per batch", sp, "time_log2", log2(lg["total"] / 638), "delta", log2(lg["total"] / base["total"]))
    else:
        main()
