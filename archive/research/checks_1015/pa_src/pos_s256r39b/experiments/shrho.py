"""Birthday collision search on 39-step SHA-256 (sha256-r39, one block) with 7 packed lanes per 256-bit word and distinguished points.

The message is M(x) = PREFIX || x: a constant 20-byte prefix (20 zero bytes) followed by the 32-byte string x (a 256-bit big-endian integer), 52 bytes in all;
FIPS 180-4 padding makes it one block: words W0..W4 = the prefix, W5..W12 = x, W13 = 0x80000000, W14 = 0, W15 = 0x1A0 (416 bits).  f(x) is the 256-bit
big-endian digest integer of the first 39 steps with the standard IV and the feed-forward addition; the walk is x -> f(x), so the digest words H0..H7 are
the next input words W5..W12.  n = 256 is the claim; the organizer experiments run the same code at reduced n (the low n bits of f).
Sections: 1 scalar digest, 2 packed straight-line generator (7 lanes of 36 bits in a 256-bit word), 3 register allocation, 4 lane packing,
5 plan and ledger, 6 search and recovery, 7 organizer experiments, 8 command line (--selftest --ledger --loss --sweep --stats --gencode).
Credit: the program structure (trail-and-table search with distinguished points, handlers, recovery, ledger method) is our own earlier
blake3 round-3 entries (0a9640ed, 3356413f, cf8b0e92, B3R3PV); the packed lanes are the idea of cf8b0e92.
"""
import sys
import json
import hashlib
from fractions import Fraction
from math import isqrt, log, exp, factorial

M32 = 0xFFFFFFFF
ROUNDS = 39
IV = (0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19)
K = (0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5, 0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
     0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
     0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
     0x650a7354, 0x766a0abb, 0x81c2c92e)
PREFIX = bytes(20)                                      # the constant 20-byte prefix of every message (20 zero bytes; no selection among prefixes)
PREFIX_WORDS = tuple(int.from_bytes(PREFIX[4 * i:4 * i + 4], "big") for i in range(5))      # message words W0..W4
TAIL = (0x80000000, 0, 0x1A0)                           # message words W13..W15 of a 52-byte message (0x80 pad byte, zero, length 416 bits)
LANES, PITCH = 7, 36                                    # lane l of a packed word occupies bits 36 l .. 36 l + 35 (32 data bits, 4 guard bits)
REP = sum(1 << (PITCH * i) for i in range(LANES))
LIM = 1 << PITCH


# ---------------------------------------------------------------- 1 scalar digest
def _ror(v, k):
    return ((v >> k) | (v << (32 - k))) & M32


def digest_words(w, prefix=PREFIX_WORDS):
    """The 8 digest words of the 39-step compression of the block W0..W4 = prefix, W5..W12 = w, W13..W15 = TAIL (IV, feed-forward)."""
    ws = list(prefix) + list(w) + list(TAIL)
    for i in range(16, ROUNDS):
        x, y = ws[i - 15], ws[i - 2]
        ws.append((ws[i - 16] + (_ror(x, 7) ^ _ror(x, 18) ^ (x >> 3)) + ws[i - 7] + (_ror(y, 17) ^ _ror(y, 19) ^ (y >> 10))) & M32)
    a, b, c, d, e, f, g, h = IV
    for i in range(ROUNDS):
        t1 = (h + (_ror(e, 6) ^ _ror(e, 11) ^ _ror(e, 25)) + ((e & f) ^ (~e & g)) + K[i] + ws[i]) & M32
        t2 = ((_ror(a, 2) ^ _ror(a, 13) ^ _ror(a, 22)) + ((a & b) ^ (a & c) ^ (b & c))) & M32
        a, b, c, d, e, f, g, h = (t1 + t2) & M32, a, b, c, (d + t1) & M32, e, f, g
    return [(u + v) & M32 for u, v in zip(IV, (a, b, c, d, e, f, g, h))]


def words_of(x):
    return [(x >> (32 * (7 - i))) & M32 for i in range(8)]


def int_of(w):
    return sum(w[i] << (32 * (7 - i)) for i in range(8))


def f_scalar(x, n=256):
    """f(x): the low n bits of the digest (big-endian integer) of the 52-byte message PREFIX || x.  n = 256 is the target."""
    return int_of(digest_words(words_of(x))) & ((1 << n) - 1)


def message(x):
    return PREFIX + x.to_bytes(32, "big")


# ---------------------------------------------------------------- 2 packed straight-line generator
class Tracer:
    """Straight-line code over 256-bit words holding 7 lanes of 36 bits (32 data bits and 4 guard bits).  A value is ('c', k), the same constant in
    every lane (folded at build time, no operation), or ('v', name, bound) with bound the largest value a lane can hold.  Every emitted line is one
    machine operation (add, and, or, xor, shl, shr) on registers or on an immediate of the form REP * c (c a 32-bit constant)."""

    def __init__(self):
        self.lines, self.k, self.calls = [], 0, 0

    def emit(self, op, a, b):
        self.k += 1
        self.calls += 1
        name = "t%d" % self.k
        self.lines.append((name, op, a, b))
        return name

    def mask(self, a):
        return ("v", self.emit("&", a[1], M32), M32)

    def clean(self, a):
        return a if a[0] == "c" or a[2] <= M32 else self.mask(a)

    def add(self, *xs):
        self.calls += 1
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
            acc = ("v", self.emit("+", acc[1], v[1]), acc[2] + v[2])
        if c:
            if acc[2] + c >= LIM:
                acc = self.mask(acc)
            acc = ("v", self.emit("+", acc[1], c), acc[2] + c)
        return acc

    def xor(self, a, b):
        self.calls += 1
        if a[0] == "c" and b[0] == "c":
            return ("c", a[1] ^ b[1])
        if a[0] == "c":
            a, b = b, a
        if b[0] == "c":
            return a if b[1] == 0 else ("v", self.emit("^", a[1], b[1]), (1 << max(a[2].bit_length(), b[1].bit_length())) - 1)
        return ("v", self.emit("^", a[1], b[1]), (1 << max(a[2].bit_length(), b[2].bit_length())) - 1)

    def and_(self, a, b):
        self.calls += 1
        if a[0] == "c" and b[0] == "c":
            return ("c", a[1] & b[1])
        if a[0] == "c":
            a, b = b, a
        if b[0] == "c":
            if b[1] == 0:
                return ("c", 0)
            return ("v", self.emit("&", a[1], b[1]), min(a[2], b[1]))
        return ("v", self.emit("&", a[1], b[1]), min(a[2], b[2]))

    def ror(self, a, r):
        """Rotation of the 32-bit lane by r: two shifts, two masks, one OR (the guard bits of a need not be clear: they land outside both masks)."""
        self.calls += 1
        if a[0] == "c":
            return ("c", _ror(a[1], r))
        h = self.emit("&", self.emit(">>", a[1], r), (1 << (32 - r)) - 1)
        lo = self.emit("&", self.emit("<<", a[1], 32 - r), ((1 << r) - 1) << (32 - r))
        return ("v", self.emit("|", h, lo), M32)

    def shr(self, a, k):
        self.calls += 1
        if a[0] == "c":
            return ("c", a[1] >> k)
        return ("v", self.emit("&", self.emit(">>", a[1], k), (1 << (32 - k)) - 1), (1 << (32 - k)) - 1)


def build_lines():
    """The 39-step compression of the 8 input words i0..i7 = W5..W12 (W0..W4, W13..W15 and the IV are constants) in the packed representation.  Returns (tracer, outputs)."""
    t = Tracer()
    W = [("c", w) for w in PREFIX_WORDS] + [("v", "i%d" % i, M32) for i in range(8)] + [("c", w) for w in TAIL]
    for i in range(16, ROUNDS):
        x, y = W[i - 15], W[i - 2]
        s0 = t.xor(t.xor(t.ror(x, 7), t.ror(x, 18)), t.shr(x, 3))
        s1 = t.xor(t.xor(t.ror(y, 17), t.ror(y, 19)), t.shr(y, 10))
        W.append(t.add(W[i - 16], s0, W[i - 7], s1))
    a, b, c, d, e, f, g, h = [("c", w) for w in IV]
    bc = t.xor(b, c)
    for i in range(ROUNDS):
        s1 = t.xor(t.xor(t.ror(e, 6), t.ror(e, 11)), t.ror(e, 25))
        ch = t.xor(g, t.and_(e, t.xor(f, g)))
        t1 = t.add(h, s1, ch, ("c", K[i]), W[i])
        s0 = t.xor(t.xor(t.ror(a, 2), t.ror(a, 13)), t.ror(a, 22))
        ab = t.xor(a, b)
        mj = t.xor(t.and_(ab, bc), b)                      # majority; a ^ b of this step is b ^ c of the next
        bc = ab
        t2 = t.add(s0, mj)
        na, ne = t.clean(t.add(t1, t2)), t.clean(t.add(d, t1))
        a, b, c, d, e, f, g, h = na, a, b, c, ne, e, f, g
    out = [t.clean(t.add(x, ("c", w))) for x, w in zip((a, b, c, d, e, f, g, h), IV)]
    return t, out


class Step:
    """The straight-line chain step: step(i0..i7) takes the 8 packed input words (lane l holds word i of the chain value of lane l) and returns the 8
    packed digest words, which are the 8 input words of the next batch.  ops = lines = machine operations."""

    def __init__(self):
        t, out = build_lines()
        assert all(o[0] == "v" and o[2] <= M32 for o in out)
        self.lines, self.gen_calls = t.lines, t.calls
        self.outs = [o[1] for o in out]
        self.ops = len(self.lines)
        self.by = {}
        for _, op, _, _ in self.lines:
            self.by[op] = self.by.get(op, 0) + 1
        nl = chr(10)

        def operand(v, op):
            return v if isinstance(v, str) else (str(v) if op in ("<<", ">>") else str(REP * v))
        body = "".join("    %s=%s%s%s" % (nm, a, op, operand(b, op)) + nl for nm, op, a, b in self.lines)
        self.src = "def step(%s):" % ",".join("i%d" % j for j in range(8)) + nl + body + "    return (%s,)" % ",".join(self.outs) + nl
        ns = {}
        exec(compile(self.src, "<packed-step>", "exec"), {}, ns)
        self.step = ns["step"]

    def _last(self):
        last = {}
        for k, (_, _, a, b) in enumerate(self.lines):
            for v in (a, b):
                if isinstance(v, str):
                    last[v] = k
        return last

    def peak_live(self):
        """Largest number of registers live after one operation (inputs live at the start, a result may reuse the register of a dying operand,
        outputs live to the end)."""
        last, outs = self._last(), set(self.outs)
        live = {"i%d" % j for j in range(8)}
        peak = len(live)
        for k, (nm, _, _, _) in enumerate(self.lines):
            live.add(nm)
            live = {v for v in live if last.get(v, -1) > k or v == nm or v in outs}
            peak = max(peak, len(live))
        return peak

    def spill_ops(self, R):
        """Loads plus stores one batch needs with R registers (Belady: farthest next use; inputs beyond R start in memory)."""
        from bisect import bisect_left
        INF = 10 ** 10
        uses = {}
        for k, (_, _, a, b) in enumerate(self.lines):
            for v in (a, b):
                if isinstance(v, str):
                    uses.setdefault(v, []).append(k)
        outs = set(self.outs)

        def nxt(v, k):
            u = uses.get(v)
            if u:
                i = bisect_left(u, k)
                if i < len(u):
                    return u[i]
            return 10 ** 9 if v in outs else INF

        reg, mem, cost = {"i%d" % j for j in range(8)}, set(), 0
        if len(reg) > R:
            for v in sorted(reg, key=lambda y: -nxt(y, 0))[:len(reg) - R]:
                reg.discard(v)
                mem.add(v)
        for k, (nm, _, a, b) in enumerate(self.lines):
            need = [v for v in {a, b} if isinstance(v, str)]
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


# ---------------------------------------------------------------- 3 register allocation
def allocate(st):
    """Register assignment of the straight line: input word j and output word j both live in register j (the chain feed is renaming, no moves);
    temporaries take the lowest free register above 7.  Returns (instructions (name, op, dst, a, b) with register numbers, immediates as ('#', c),
    number of registers used).  Raises if output j would have to be written while input j is still needed."""
    import heapq
    last, free, nxt = st._last(), [], 8
    reg = {"i%d" % j: j for j in range(8)}
    outpin = {nm: j for j, nm in enumerate(st.outs)}
    code, top = [], 8
    for k, (nm, op, a, b) in enumerate(st.lines):
        ra = reg[a]
        rb = reg[b] if isinstance(b, str) else ("#", b)
        for v in {a, b}:
            if isinstance(v, str) and v in reg and last.get(v, -1) == k and v not in outpin:
                if reg[v] >= 8:
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
        code.append((nm, op, reg[nm], ra, rb))
    return code, top


def run_allocated(code, ws):
    """Execute the allocated code on a register file; returns the first 8 registers (the next input words)."""
    regs = [0] * (max(c[2] for c in code) + 1)
    regs[:8] = ws
    for (nm, op, d, ra, rb) in code:
        va = regs[ra]
        if isinstance(rb, tuple):
            vb = rb[1] if op in ("<<", ">>") else REP * rb[1]
        else:
            vb = regs[rb]
        regs[d] = (va + vb if op == "+" else va & vb if op == "&" else va | vb if op == "|" else va ^ vb if op == "^" else va >> vb if op == ">>" else va << vb)
    return regs[:8]


_STEP = []


def step256():
    if not _STEP:
        _STEP.append(Step())
    return _STEP[0]


# ---------------------------------------------------------------- 4 lane packing
def pack_lanes(xs):
    """The 8 packed words for up to 7 chain values (lane l holds xs[l])."""
    return [sum(((x >> (32 * (7 - i))) & M32) << (PITCH * l) for l, x in enumerate(xs)) for i in range(8)]


def lanes_of(ws, count=LANES):
    return [sum(((ws[i] >> (PITCH * l)) & M32) << (32 * (7 - i)) for i in range(8)) for l in range(count)]


def lane_value(ws, l, n=256):
    return sum(((ws[i] >> (PITCH * l)) & M32) << (32 * (7 - i)) for i in range(8)) & ((1 << n) - 1)


def set_lane(ws, l, x):
    sh = PITCH * l
    keep = ~(M32 << sh)
    return [(ws[i] & keep) | (((x >> (32 * (7 - i))) & M32) << sh) for i in range(8)]


# ---------------------------------------------------------------- 5 plan and ledger
LAMBDA = Fraction(497, 1000)       # 1 - exp(-LAMBDA) = 0.39165
CUTLOSS = Fraction(15, 100000)     # allowance for cut-trail points, as a fraction of Q
TAIL_AGES = 1e-6                   # probability that the unfinished trails hold more than M * L points
CMAX = 2                           # halt when more than CMAX trails are cut (more is charged as failure)
STAGE1_BITS = 32
# machine charges (proof 3.3)
LOOP_OPS = 3                       # batch counter increment, compare with the slice limit, branch
FILT_OPS = 4                       # stage-1 test: add, AND, compare, branch
HIT_OPS = 400                      # a stage-1 hit lane: lane number, extraction of the words needed for the window and key, window test, bookkeeping
EVENT_OPS = 800                    # a finished trail: key, entry, new start inserted in the lane, bookkeeping
CUT_OPS = 800                      # a cut trail: age scan share, new start inserted in the lane, bookkeeping
SLICE_OPS = 120                    # slice check: 7 ages
RECOVER_EXTRA = 64                 # per recovery batch beyond the kernel (the exact test and loop need 29; call and 8 moves 10)
INSTR_BYTES = 36                   # opcode, registers and an inline 256-bit immediate
GEN_CODE = 1190                    # instructions of the runtime generator (1,190 bytecode instructions, `python3 shrho.py --gencode`)
OTHER_CODE = 600                   # instructions besides the main body and the recovery copy of the kernel: handlers, key scan, cut and slice checks, setup
REGISTERS = 64                     # declared register file of 256-bit words, counted as memory
REGFILE = REGISTERS * 32
COUNTERS = 6144                    # trail numbers, births, counters, the lane arrays used by the handlers (about 2,048) and a reserve of 4,096 bytes for the stack, alignment and anything not itemised
ENTRY = 25
MEM_LIMIT = 1 << 20
ADVICE = 0
TAIL_LOG2 = -40
KAPPA_256 = 12
GEN_FACTOR = 400                   # word operations charged per generator call and per emitted line (the C port needs 1,267,939 wasm operations)
GEN_SCRATCH = 16384                # bytes of scratch of the runtime generator (measured 13,848 in the C port, proof 3.6)
SETUP_FIXED = 7 * 400 + 2000       # 7 starts inserted in the lanes, random word, counters
# reduced widths: s1 (low zero bits of a DP), W (window bits), Tp, kappa, Sb (slice length in batches)
CFG = {18: dict(s1=2, W=0, Tp=1, kappa=12, Sb=4), 20: dict(s1=2, W=0, Tp=1, kappa=12, Sb=4), 30: dict(s1=4, W=0, Tp=1, kappa=12, Sb=16),
       40: dict(s1=6, W=4, Tp=1, kappa=12, Sb=64), 48: dict(s1=8, W=6, Tp=1, kappa=12, Sb=256),
       256: dict(s1=32, W=90, kappa=KAPPA_256, Sb=1 << 48)}


def stage1(z, s1):
    """Lanes whose s1 low bits of the chain value are zero.  z = packed word 7 (the low 32 bits of the next chain value, guard bits clear).  For
    s1 = 32 this is 3 operations on the kernel's output: z + REP * M32, AND REP << 32, XOR REP << 32 (zero when no lane is a hit)."""
    m = (1 << s1) - 1
    y = ((z & (REP * m) if s1 < 32 else z) + REP * m) & (REP << s1)
    hit = y ^ (REP << s1)
    return [l for l in range(LANES) if (hit >> (PITCH * l + s1)) & 1]


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


def machine_constants(st=None, R=REGISTERS):
    """(kernel ops, filter ops, body ops, code bytes, tmax) of the n = 256 program with R registers (spill loads and stores added to the body and
    to the recovery copy of the kernel)."""
    st = st or step256()
    ph = st.ops
    spill = st.spill_ops(R) if R < st.peak_live() else 0
    body = ph + spill + FILT_OPS + LOOP_OPS
    code = (body + (ph + spill + RECOVER_EXTRA) + OTHER_CODE) * INSTR_BYTES
    tmax = (MEM_LIMIT - code - R * 32 - COUNTERS - ADVICE) // ENTRY
    return ph, FILT_OPS, body, code, tmax


def phase_bytes(code, tmax):
    """(setup phase, search phase) resident bytes.  Setup: the main code as the generator writes it (counted at its final size), the counters, the
    generator's code image (GEN_CODE instructions) and its scratch.  Search: code, advice, table, register file, counters.  The generator is never called
    after setup; its image and scratch are overwritten by the table and the register file."""
    return code + ADVICE + COUNTERS + GEN_CODE * INSTR_BYTES + GEN_SCRATCH, code + ADVICE + COUNTERS + REGFILE + ENTRY * tmax


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
    best = None
    for t in range(1, 8193):                              # the largest Tp whose table-capacity tail is within 2^TAIL_LOG2
        p = _plan(256, t, kappa, tmax, CFG[256]["Sb"])
        mean = float(p["Q"] / p["L"])
        if mean < tmax + 1 and tail_log2(mean, tmax + 1) <= TAIL_LOG2:
            best = p
    return best


def ledger(p=None, st=None, R=REGISTERS):
    """Operation budget in word operations (exact integers); the unit is the reference count C(sha256-r39) = 2812 operations."""
    st = st or step256()
    p = p or plan(256, None, None, R)
    ph, filt, body, code, _ = machine_constants(st, R)
    spill = st.spill_ops(R) if R < st.peak_live() else 0
    gen = GEN_FACTOR * (st.gen_calls + st.ops)
    parts = dict(main=body * p["B"],
                 slices=-(-p["B"] // p["Sb"]) * SLICE_OPS,
                 stage1_hits=p["e2max"] * HIT_OPS,
                 events=p["tmax"] * (EVENT_OPS + 3 * p["tmax"]),
                 cuts=p["cmax"] * CUT_OPS,
                 recovery=p["capr"] * (ph + spill + RECOVER_EXTRA) + 600,
                 setup=SETUP_FIXED + gen)
    return dict(parts=parts, total=sum(parts.values()), plan=p, body=body, gen=gen)


def loss(p):
    """The probability losses of proof Section 4 (floats): the terms, their sum and the lower bound on the success probability."""
    N, Q, L = p["N"], p["Q"], p["L"]
    x = float(LAMBDA)
    trails = float(Q / L)
    f1 = float((p["c"] + p["Sb"]) / Q)                        # one cut trail, as a fraction of Q
    mu = trails * exp(-p["kappa"])
    pk = [exp(-mu) * mu ** j / factorial(j) for j in range(p["cmax"] + 1)]
    slope = 2 * x * exp(-x)
    cut = sum(pk[j] * max(0.0, j * f1 - float(CUTLOSS)) * slope for j in range(1, p["cmax"] + 1)) + (1 - sum(pk)) * (1 - exp(-x))
    t = dict(unfinished=TAIL_AGES, cut_deficit=cut, inside_trail=float(Q * L / N),
             key_false_match=p["tmax"] * (p["tmax"] - 1) / 2 * 2.0 ** -(p["kb"] + log(p["Tp"], 2)),
             table_capacity=2.0 ** tail_log2(trails, p["tmax"] + 1), recovery_no_pair=2.0 ** -100)
    t["sum"] = sum(t.values())
    t["P_lower"] = 1 - exp(-x) - t["sum"]
    t["mean_cut_trails"], t["trails"], t["cut_one_trail"] = mu, trails, f1
    return t


# ---------------------------------------------------------------- 6 search and recovery
class Halt(Exception):
    pass


class Engine:
    """The chain function f (the low n bits of the digest) in two forms: step(ws) for 7 lanes and f2(xs) for the recovery (the same kernel)."""

    def __init__(self, n):
        self.n = n
        self.st = step256()
        km = []
        for i in range(8):
            lo = 32 * (7 - i)
            km.append(0 if lo >= n else (M32 if lo + 32 <= n else (1 << (n - lo)) - 1))
        self.km = None if n == 256 else [REP * v for v in km]

    def step(self, *ws):
        out = self.st.step(*ws)
        return out if self.km is None else tuple(o & k for o, k in zip(out, self.km))

    def f2(self, xs):
        out = self.step(*pack_lanes(xs))
        return [lane_value(out, l, self.n) for l in range(len(xs))]

    def g_scalar(self, x):
        return f_scalar(x, self.n)


class IdealEngine:
    """An ideal function of the same width (keyed blake2b) used as the control of the search experiment."""

    def __init__(self, n, key):
        self.n, self.key = n, key
        self.nb = (n + 7) // 8

    def g(self, v):
        h = hashlib.blake2b(v.to_bytes(self.nb, "little"), key=self.key, digest_size=self.nb).digest()
        return int.from_bytes(h, "little") & ((1 << self.n) - 1)

    def step(self, *ws):
        return tuple(pack_lanes([self.g(v) for v in lanes_of(ws)]))

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
    trail moves alone for l1 - l2 steps, then both move together (two lanes of the same kernel)."""
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
    n, mask = p["n"], p["N"] - 1
    table, births, ts, nxt = {}, [0] * LANES, list(range(LANES)), LANES
    ws = pack_lanes([(r + t) & mask for t in ts])
    cnt["inserts"] += LANES
    batches = 0
    while batches < p["B"]:
        ws = list(eng.step(*ws))
        batches += 1
        cnt["batches"] += 1
        for l in stage1(ws[7], p["s1"]):
            cnt["stage1_hits"] += 1
            if cnt["stage1_hits"] > p["e2max"]:
                raise Halt("stage-1 budget")
            x = lane_value(ws, l, n)
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
                ws = set_lane(ws, l, (r + ts[l]) & mask)
                cnt["inserts"] += 1
        if batches % p["Sb"] == 0:
            for l in range(LANES):
                if batches - births[l] >= p["c"]:
                    cnt["cut"] += 1
                    if cnt["cut"] > p["cmax"]:
                        raise Halt("cut budget")
                    ts[l], nxt, births[l] = nxt, nxt + 1, batches
                    ws = set_lane(ws, l, (r + ts[l]) & mask)
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
    except Halt:
        cnt["halt"] += 1
        res = None
    return res, cnt


# ---------------------------------------------------------------- 7 organizer experiments
N_T3 = 18                          # width of the search experiment and of the ideal control
N_T1 = 10                          # width of the family-law runs (fresh key)
M_T2, B_T2 = 448, 16               # points per trial (64 batches of 7 lanes), projection width (event: low 16 bits of the digest)
T2_NAMES = ("w0", "w3", "w7", "xor8", "sum8", "p01", "p23")


def t1_run(seed, n=N_T1):
    """Family law, fresh random key K (20 bytes in the prefix words W0..W4): steps until the first repeat of x -> low n bits of digest(K || 0^24 || x)."""
    kw = words_of(derive(seed, "k", 160))[3:]
    x, seen = derive(seed, "s", n), set()
    while x not in seen:
        seen.add(x)
        x = int_of(digest_words([0] * 6 + [(x >> 32) & M32, x & M32], kw)) & ((1 << n) - 1)
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


_M16 = (1 << B_T2) - 1
_F16 = sum(_M16 << (32 * i) for i in range(8))
_KS = sum(1 << (32 * i) for i in range(8))


def t2_columns(digs):
    """The seven projections (T2_NAMES) of each 256-bit digest integer, as seven lists of B_T2-bit values: the low bits, the bits at 96 and at 224,
    the xor of the 8 words, the sum of the 8 words, and two concatenations of two 8-bit pieces."""
    m = _M16
    folded = [d ^ (d >> 128) for d in digs]
    folded = [d ^ (d >> 64) for d in folded]
    return [[d & m for d in digs], [(d >> 96) & m for d in digs], [(d >> 224) & m for d in digs],
            [(d ^ (d >> 32)) & m for d in folded],
            [(((d & _F16) * _KS) >> 224) & m for d in digs],
            [((d & 0xFF) | (((d >> 32) & 0xFF) << 8)) & m for d in digs],
            [(((d >> 64) & 0xFF) | (((d >> 107) & 0xFF) << 8)) & m for d in digs]]


def e2_trial(seed, tr):
    """T2: M_T2 points of the target function at width 256 (source by trial index: uniform inputs, counter r + i, or iterates of f from 7 random
    starts), the digests f(x) from the packed kernel, equal pairs in seven 16-bit projections.  w0 (the low 16 bits) is the checked event."""
    eng = Engine(256)
    src = tr % 3
    xs, digs = [], []
    if src == 0:
        xs = [derive(seed, "u%d" % i) for i in range(M_T2)]
    elif src == 1:
        r = derive(seed, "r")
        xs = [(r + i) & ((1 << 256) - 1) for i in range(M_T2)]
    if xs:
        for b in range(M_T2 // LANES):
            digs += lanes_of(eng.step(*pack_lanes(xs[b * LANES:(b + 1) * LANES])))
    else:
        cur = [derive(seed, "c%d" % l) for l in range(LANES)]
        for b in range(M_T2 // LANES):
            xs += cur
            cur = lanes_of(eng.step(*pack_lanes(cur)))
            digs += cur
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
    if eid == "shrho-n18":
        eng = Engine(N_T3)
        for t in req["trials"]:
            a, b, obs = e1_trial(t["seed"], eng, IdealEngine)
            out.append({"trial": t["trial"], "message_a_hex": a.hex() if a else None, "message_b_hex": b.hex() if b else None, "observations": obs})
    elif eid == "proj-k0-w256":
        for t in req["trials"]:
            a, b, obs = e2_trial(t["seed"], t["trial"])
            out.append({"trial": t["trial"], "message_a_hex": a.hex() if a else None, "message_b_hex": b.hex() if b else None, "observations": obs})
    else:
        raise ValueError("unknown experiment")
    return {"schema_version": 1, "trials": out}


# ---------------------------------------------------------------- 8 command line
def selftest():
    import random
    ok = True
    rnd = random.Random(3)
    st = step256()
    print("n=256 step: ops", st.ops, st.by, "peak live", st.peak_live(), "spill_ops(%d)" % REGISTERS, st.spill_ops(REGISTERS))
    code, regs = allocate(st)
    print("allocation: registers used", regs, "moves 0 (output word j in register j)")
    ws0 = [rnd.getrandbits(252) for _ in range(8)]
    good = run_allocated(code, ws0) == list(st.step(*ws0))
    print("allocated code on a register file equals the step:", good)
    ok &= good
    # regression of the kernel against the scalar 39-step compression: 4,102 lanes (586 batches of 7), the full 256-bit f
    good, tot = True, 0
    for _ in range(586):
        xs = [rnd.getrandbits(256) for _ in range(LANES)]
        out = lanes_of(st.step(*pack_lanes(xs)))
        good &= all(out[l] == f_scalar(xs[l]) for l in range(LANES))
        tot += LANES
    print("%d lanes, full 256-bit f, kernel vs scalar compression: %s" % (tot, good))
    ok &= good
    for xs in ([0] * LANES, [(1 << 256) - 1] * LANES):
        good = lanes_of(st.step(*pack_lanes(xs))) == [f_scalar(x) for x in xs]
        print("extreme inputs (all zero / all ones):", good)
        ok &= good
    cur = list(xs)
    ws = pack_lanes(xs)
    for _ in range(4):
        ws = list(st.step(*ws))
        cur = [f_scalar(x) for x in cur]
    good = lanes_of(ws) == cur
    print("4 chained steps (7 lanes):", good)
    ok &= good
    e = Engine(N_T3)
    xs = [rnd.getrandbits(N_T3) for _ in range(LANES)]
    ws = pack_lanes(xs)
    for _ in range(5):
        ws = list(e.step(*ws))
        xs = [e.g_scalar(x) for x in xs]
    good = lanes_of(ws) == xs
    print("n=%d chain, 5 steps, 7 lanes:" % N_T3, good)
    ok &= good
    xs = [rnd.getrandbits(256) for _ in range(5)]
    good = Engine(256).f2(xs) == [f_scalar(x) for x in xs]
    print("recovery form f2 (5 values in one kernel call) vs scalar:", good)
    ok &= good
    xs = [rnd.getrandbits(256) for _ in range(LANES)]
    ws = pack_lanes(xs)
    good = lanes_of(ws) == xs and all(lane_value(ws, l) == xs[l] for l in range(LANES)) and lanes_of(set_lane(ws, 3, xs[0]))[3] == xs[0]
    print("lane packing:", good)
    ok &= good
    z = pack_lanes([0, 5, 0, 1 << 32, 7, 0, 9])
    good = stage1(z[7], 32) == [0, 2, 3, 5] and stage1(z[7], 4) == [0, 2, 3, 5] and stage1(pack_lanes([8, 16, 1, 0, 3, 0, 32])[7], 4) == [1, 3, 5, 6]
    print("stage-1 test:", good)
    ok &= good
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
    print("time_log2 = %.5f (unrounded %.8f)" % (log2(lg["total"] / 2812) + 5e-6, log2(lg["total"] / 2812)))


def stats(trials=256):
    """Run the two experiments locally on pseudo-random seeds and print the counts (descriptive only, no inference is drawn from them)."""
    from math import sqrt, pi
    seeds = [hashlib.sha256(("stats/%d" % i).encode()).hexdigest() for i in range(trials)]
    rows = serve({"experiment_id": "shrho-n18", "trials": [{"trial": i, "seed": s} for i, s in enumerate(seeds)]})["trials"]
    N1 = 1 << N_T1
    tt = sum(r["observations"]["target_ok"] for r in rows)
    ii = sum(r["observations"]["ideal_ok"] for r in rows)
    print("T3 n=%d: attempts returning a verified pair: target %d of %d, ideal function %d of %d" % (N_T3, tt, trials, ii, trials))
    ts = [r["observations"]["t1_steps"] for r in rows]
    print("T1 n=%d fresh K: %d runs, mean first repeat %.2f (sqrt(pi N/2) = %.2f)" % (N_T1, trials, sum(ts) / trials, sqrt(pi * N1 / 2)))
    seedl = [hashlib.sha256(("stats2/%d" % i).encode()).hexdigest() for i in range(trials)]
    r2 = serve({"experiment_id": "proj-k0-w256", "trials": [{"trial": i, "seed": s} for i, s in enumerate(seedl)]})["trials"]
    lam = M_T2 * (M_T2 - 1) / 2 / (1 << B_T2)
    print("T2 width 256: %d points, %d-bit projections, equal pairs per trial if uniform %.4f, trials with a pair if uniform %.4f" % (M_T2, B_T2, lam, 1 - exp(-lam)))
    for s in range(3):
        sel = [r for r in r2 if r["observations"]["source"] == s]
        line = []
        for name in T2_NAMES:
            line.append("%s %d (uniform reference %.1f)" % (name, sum(r["observations"]["dup_" + name] for r in sel), lam * len(sel)))
        hit = sum(1 for r in sel if r["message_a_hex"])
        print("  source %s (%d trials): returned pairs %d (uniform reference %.1f); " % (("uniform", "counter", "iterates")[s], len(sel), hit, (1 - exp(-lam)) * len(sel)) + "; ".join(line))
    return rows, r2



# ---------------------------------------------------------------- 9 the circuit generator in C
# The generator of sections 2 and 3 (Tracer, build_lines, allocate) written in freestanding C.  It was compiled to WebAssembly and run in a sandbox with
# 16 pages (1,048,576 bytes) of guest memory: it emits the same program as Tracer/Step/allocate (proof 3.6).  `--gen-c` prints it.
GEN_C = r'''/* Freestanding C port of the shrho.py circuit generator (Tracer / build_lines / allocate).
   No libc, no malloc, no imports.  Exports: run(), info_ptr(), code_ptr().
   Static memory map:
     code region   final main-code size of the entry, 36-byte records: op, dst, a, b (u16 LE), b-is-immediate flag, 32-bit immediate, zero padding
     counters      6,144 B
     scratch       last-use u16 and register u16 per instruction, free-register flags, the schedule words and the state (16 B per value)      */
typedef unsigned char u8; typedef unsigned short u16; typedef unsigned int u32; typedef unsigned long long u64;

#ifndef NMAX
#define NMAX 2560
#endif
#define REC 36
#ifndef CODE_BYTES
#define CODE_BYTES 182988
#endif
#define CTR_BYTES 6144
#define ROUNDS 39
#define M32 0xFFFFFFFFull
#define LIM (1ull << 36)

static u8 code[CODE_BYTES];
__attribute__((used)) static u8 counters[CTR_BYTES];
static struct { u16 last[NMAX + 8]; u16 reg[NMAX + 8]; u8 isfree[256]; u8 outpin[NMAX + 8]; } S;
typedef struct { u8 kind; u8 pad; u16 name; u32 c; u64 bound; } V;       /* kind 0: constant c; kind 1: register value name, bound */
static V W[ROUNDS];
static u32 nin, calls, err;
static struct { u32 ninst, nreg, calls, err, sz_code, sz_ctr, sz_scratch, sz_values; } info;

static const u32 IV[8] = {0x6A09E667u,0xBB67AE85u,0x3C6EF372u,0xA54FF53Au,0x510E527Fu,0x9B05688Cu,0x1F83D9ABu,0x5BE0CD19u};
static const u32 K[ROUNDS] = {
0x428a2f98u,0x71374491u,0xb5c0fbcfu,0xe9b5dba5u,0x3956c25bu,0x59f111f1u,0x923f82a4u,0xab1c5ed5u,0xd807aa98u,0x12835b01u,0x243185beu,0x550c7dc3u,
0x72be5d74u,0x80deb1feu,0x9bdc06a7u,0xc19bf174u,0xe49b69c1u,0xefbe4786u,0x0fc19dc6u,0x240ca1ccu,0x2de92c6fu,0x4a7484aau,0x5cb0a9dcu,0x76f988dau,
0x983e5152u,0xa831c66du,0xb00327c8u,0xbf597fc7u,0xc6e00bf3u,0xd5a79147u,0x06ca6351u,0x14292967u,0x27b70a85u,0x2e1b2138u,0x4d2c6dfcu,0x53380d13u,
0x650a7354u,0x766a0abbu,0x81c2c92eu};
static const u32 PREFIX_W[5] = {0, 0, 0, 0, 0};                      /* message words W0..W4: the constant 20-byte prefix (20 zero bytes) */
static const u32 TAIL_W[3] = {0x80000000u, 0, 0x1A0u};              /* message words W13..W15 of a 52-byte message */

/* operations: '+' '&' '|' '^' '<' (shl) '>' (shr); a is always a register value, b a register value or an immediate */
static u32 emit(char op, u32 a, u32 b, int bimm) {
  calls++;
  if (nin >= NMAX) { err = 1; return 0; }
  u8 *rec = code + (u32)REC * nin;
  rec[0] = (u8)op;
  rec[1] = (u8)(nin + 8); rec[2] = (u8)((nin + 8) >> 8);                /* destination: SSA name, rewritten to a register by the allocator */
  rec[3] = (u8)a; rec[4] = (u8)(a >> 8);
  if (bimm) { rec[5] = rec[6] = 0; rec[7] = 1; rec[8] = (u8)b; rec[9] = (u8)(b >> 8); rec[10] = (u8)(b >> 16); rec[11] = (u8)(b >> 24); }
  else { rec[5] = (u8)b; rec[6] = (u8)(b >> 8); rec[7] = 0; rec[8] = rec[9] = rec[10] = rec[11] = 0; }
  return 8 + nin++;
}
static int bitlen(u64 x) { int n = 0; while (x) { n++; x >>= 1; } return n; }
static V cst(u32 c) { V v; v.kind = 0; v.pad = 0; v.name = 0; v.c = c; v.bound = 0; return v; }
static V var(u32 name, u64 bound) { V v; v.kind = 1; v.pad = 0; v.name = (u16)name; v.c = 0; v.bound = bound; return v; }

static V mask(V a) { return var(emit('&', a.name, (u32)M32, 1), M32); }
static V clean(V a) { return (a.kind == 0 || a.bound <= M32) ? a : mask(a); }

static V add(int n, const V *xs) {
  calls++;
  u32 c = 0; V acc; int have = 0;
  for (int i = 0; i < n; i++) if (xs[i].kind == 0) c += xs[i].c;
  for (int i = 0; i < n; i++) {
    if (xs[i].kind == 0) continue;
    if (!have) { acc = xs[i]; have = 1; continue; }
    V v = xs[i];
    while (acc.bound + v.bound >= LIM) { if (acc.bound >= v.bound) acc = mask(acc); else v = mask(v); }
    acc = var(emit('+', acc.name, v.name, 0), acc.bound + v.bound);
  }
  if (!have) return cst(c);
  if (c) {
    if (acc.bound + c >= LIM) acc = mask(acc);
    acc = var(emit('+', acc.name, c, 1), acc.bound + c);
  }
  return acc;
}
static V add2(V a, V b) { V x[2]; x[0] = a; x[1] = b; return add(2, x); }
static V add3(V a, V b, V c) { V x[3]; x[0] = a; x[1] = b; x[2] = c; return add(3, x); }
static V add4(V a, V b, V c, V d) { V x[4]; x[0] = a; x[1] = b; x[2] = c; x[3] = d; return add(4, x); }
static V add5(V a, V b, V c, V d, V e) { V x[5]; x[0] = a; x[1] = b; x[2] = c; x[3] = d; x[4] = e; return add(5, x); }

static V xorv(V a, V b) {
  calls++;
  if (a.kind == 0 && b.kind == 0) return cst(a.c ^ b.c);
  if (a.kind == 0) { V t = a; a = b; b = t; }
  if (b.kind == 0) {
    if (b.c == 0) return a;
    int m = bitlen(a.bound) > bitlen(b.c) ? bitlen(a.bound) : bitlen(b.c);
    return var(emit('^', a.name, b.c, 1), (1ull << m) - 1);
  }
  int m = bitlen(a.bound) > bitlen(b.bound) ? bitlen(a.bound) : bitlen(b.bound);
  return var(emit('^', a.name, b.name, 0), (1ull << m) - 1);
}
static V andv(V a, V b) {
  calls++;
  if (a.kind == 0 && b.kind == 0) return cst(a.c & b.c);
  if (a.kind == 0) { V t = a; a = b; b = t; }
  if (b.kind == 0) {
    if (b.c == 0) return cst(0);
    return var(emit('&', a.name, b.c, 1), a.bound < b.c ? a.bound : b.c);
  }
  return var(emit('&', a.name, b.name, 0), a.bound < b.bound ? a.bound : b.bound);
}
static u32 ror32(u32 v, int k) { return (v >> k) | (v << (32 - k)); }
static V ror(V a, int r) {
  calls++;
  if (a.kind == 0) return cst(ror32(a.c, r));
  u32 s1 = emit('>', a.name, (u32)r, 1);
  u32 h = emit('&', s1, (u32)((1ull << (32 - r)) - 1), 1);
  u32 s2 = emit('<', a.name, (u32)(32 - r), 1);
  u32 lo = emit('&', s2, (u32)((((1ull << r) - 1) << (32 - r)) & M32), 1);
  return var(emit('|', h, lo, 0), M32);
}
static V shr(V a, int k) {
  calls++;
  if (a.kind == 0) return cst(a.c >> k);
  u32 s1 = emit('>', a.name, (u32)k, 1);
  u64 m = (1ull << (32 - k)) - 1;
  return var(emit('&', s1, (u32)m, 1), m);
}

static V outv[8];
static void build(void) {
  for (int i = 0; i < 5; i++) W[i] = cst(PREFIX_W[i]);
  for (int i = 5; i < 13; i++) W[i] = var((u32)(i - 5), M32);
  for (int i = 13; i < 16; i++) W[i] = cst(TAIL_W[i - 13]);
  for (int i = 16; i < ROUNDS; i++) {
    V x = W[i - 15], y = W[i - 2];
    V r7 = ror(x, 7); V r18 = ror(x, 18);
    V p0 = xorv(r7, r18);
    V h3 = shr(x, 3);
    V s0 = xorv(p0, h3);
    V r17 = ror(y, 17); V r19 = ror(y, 19);
    V p1 = xorv(r17, r19);
    V h10 = shr(y, 10);
    V s1 = xorv(p1, h10);
    W[i] = add4(W[i - 16], s0, W[i - 7], s1);
  }
  V a = cst(IV[0]), b = cst(IV[1]), c = cst(IV[2]), d = cst(IV[3]), e = cst(IV[4]), f = cst(IV[5]), g = cst(IV[6]), h = cst(IV[7]);
  V bc = xorv(b, c);
  for (int i = 0; i < ROUNDS; i++) {
    V e6 = ror(e, 6); V e11 = ror(e, 11);
    V pe = xorv(e6, e11);
    V e25 = ror(e, 25);
    V s1 = xorv(pe, e25);
    V fg = xorv(f, g);
    V an = andv(e, fg);
    V ch = xorv(g, an);
    V t1 = add5(h, s1, ch, cst(K[i]), W[i]);
    V a2 = ror(a, 2); V a13 = ror(a, 13);
    V pa = xorv(a2, a13);
    V a22 = ror(a, 22);
    V s0 = xorv(pa, a22);
    V ab = xorv(a, b);
    V an2 = andv(ab, bc);
    V mj = xorv(an2, b);
    bc = ab;
    V t2 = add2(s0, mj);
    V na = clean(add2(t1, t2));
    V ne = clean(add2(d, t1));
    h = g; g = f; f = e; e = ne; d = c; c = b; b = a; a = na;
  }
  V st[8]; st[0] = a; st[1] = b; st[2] = c; st[3] = d; st[4] = e; st[5] = f; st[6] = g; st[7] = h;
  for (int i = 0; i < 8; i++) outv[i] = clean(add2(st[i], cst(IV[i])));
}

static void put16(u8 *p, u32 v) { p[0] = (u8)v; p[1] = (u8)(v >> 8); }
static u32 get16(const u8 *p) { return (u32)p[0] | ((u32)p[1] << 8); }

__attribute__((export_name("info_ptr"))) u32 info_ptr(void) { return (u32)(unsigned long)&info; }
__attribute__((export_name("code_ptr"))) u32 code_ptr(void) { return (u32)(unsigned long)code; }

__attribute__((export_name("run"))) int run(void) {
  err = 0; nin = 0; calls = 0;
  info.sz_code = sizeof code; info.sz_ctr = sizeof counters; info.sz_scratch = sizeof S; info.sz_values = sizeof W + sizeof outv;
  build();
  info.calls = calls;
  if (err) { info.err = err; return 1; }
  for (int i = 0; i < 8; i++) if (outv[i].kind != 1 || outv[i].bound > M32) { info.err = 3; return 3; }
  /* last use of every name */
  for (u32 k = 0; k < NMAX + 8; k++) { S.last[k] = 0xFFFF; S.reg[k] = 0; }
  for (u32 k = 0; k < nin; k++) {
    u8 *rec = code + (u32)REC * k;
    S.last[get16(rec + 3)] = (u16)k;
    if (!rec[7]) S.last[get16(rec + 5)] = (u16)k;
  }
  /* outputs: output j is pinned to register j */
  for (u32 k = 0; k < NMAX + 8; k++) S.outpin[k] = 0;            /* 1 + j for the name that is output j */
  for (int j = 0; j < 8; j++) S.outpin[outv[j].name] = (u8)(1 + j);
  for (int j = 0; j < 8; j++) S.reg[j] = (u16)j;
  for (int j = 0; j < 256; j++) S.isfree[j] = 0;
  u32 nxt = 8, top = 8;
  for (u32 k = 0; k < nin; k++) {
    u8 *rec = code + (u32)REC * k;
    u32 nm = get16(rec + 1), a = get16(rec + 3), b = get16(rec + 5), bimm = rec[7];
    u32 ra = S.reg[a], rb = bimm ? 0 : S.reg[b];
    if (S.last[a] == k && !S.outpin[a] && S.reg[a] >= 8) S.isfree[S.reg[a]] = 1;
    if (!bimm && b != a && S.last[b] == k && !S.outpin[b] && S.reg[b] >= 8) S.isfree[S.reg[b]] = 1;
    u32 d;
    if (S.outpin[nm]) {
      d = (u32)S.outpin[nm] - 1;
      if (S.last[d] != 0xFFFF && S.last[d] > k) { info.err = 4; return 4; }
    } else {
      d = 0;
      for (u32 r = 8; r < nxt; r++) if (S.isfree[r]) { d = r; break; }
      if (d) S.isfree[d] = 0; else d = nxt++;
    }
    S.reg[nm] = (u16)d;
    if (d + 1 > top) top = d + 1;
    put16(rec + 1, d); put16(rec + 3, ra);
    if (!bimm) put16(rec + 5, rb);
  }
  info.ninst = nin; info.nreg = top; info.err = err;
  return err;
}
'''

if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    if arg == "--selftest":
        sys.exit(0 if selftest() else 1)
    elif arg == "--ledger":
        from math import log2
        print_ledger(ledger())
        for R in (32, 16):
            lgR = ledger(None, None, R)
            print("fallback R = %d: spill ops per batch %d, body %d, tmax %d, Tp %d, time_log2 %.5f" % (
                R, step256().spill_ops(R), lgR["body"], lgR["plan"]["tmax"], lgR["plan"]["Tp"], log2(lgR["total"] / 2812)))
        st = step256()
        ph, filt, body, code, tmax = machine_constants(st)
        print("kernel", ph, "filter", filt, "body", body, "code bytes", code, "tmax", tmax, "generator calls", st.gen_calls)
        print("memory bytes", ENTRY * tmax + code + REGFILE + COUNTERS + ADVICE, "limit", MEM_LIMIT)
    elif arg == "--gencode":
        import dis, types

        def cnt(co):
            return sum(1 for _ in dis.get_instructions(co)) + sum(cnt(x) for x in co.co_consts if isinstance(x, types.CodeType))
        fs = (Tracer.__init__, Tracer.emit, Tracer.mask, Tracer.clean, Tracer.add, Tracer.xor, Tracer.and_, Tracer.ror, Tracer.shr, build_lines, allocate)
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
            print("kappa", kappa, "Tp", p["Tp"], "tmax", p["tmax"], "time_log2 %.5f" % log2(lg["total"] / 2812), "P_lower %.5f" % ls["P_lower"])
    elif arg == "--stats":
        stats()
    else:
        json.dump(serve(json.load(sys.stdin)), sys.stdout)
