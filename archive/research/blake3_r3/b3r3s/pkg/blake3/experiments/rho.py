"""Birthday collision search on 3-round BLAKE3-256 (blake3-r3-prefix-v1) with 7 packed lanes and distinguished points.

The chain message is 64 bytes: 32 zero bytes (words m0..m7) followed by x (words m8..m15, little endian): one
chunk, one block, flags 11, counter 0, length 64.  f(x) is the low n bits of the 256-bit little-endian digest
integer.  n = 256 is the claim; the organizer experiments run the same code with n = 22.
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


def digest_words(m, rounds=ROUNDS, flags=11, blen=64, counter=0):
    """Root compression of one 64-byte block: 16 message words -> 8 digest words."""
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


def f_scalar(x, n):
    """f(x): the low n bits of the digest of the message 0^32 || x."""
    d = digest_words([0] * 8 + [(x >> (32 * i)) & M32 for i in range(8)])
    return sum(d[i] << (32 * i) for i in range(8)) & ((1 << n) - 1)


def message(x):
    return bytes(32) + x.to_bytes(32, "little")


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
    """Trace the 3-round digest of 0^32 || x for 7 lanes: source of batch(), operation count, count by kind."""
    tr = Tracer()
    v = [("c", w) for w in IV] + [("c", w) for w in IV[:4]] + [("c", 0), ("c", 0), ("c", 64), ("c", 11)]
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
MEM_LIMIT = 1 << 20
TAIL_LOG2 = -40                    # table-capacity abort probability at most 2^-40
# Mixed distinguished points: x ends a trail iff its low s1 bits are zero and F = (x >> s1) mod 2^W is below Tp;
# density theta = Tp / 2^(s1 + W) and L = 1 / theta.  The key is the kb bits above the window followed by the fb low bits of F.
CFG = {256: dict(s1=32, W=90), 40: dict(s1=12, W=0, Tp=1), 32: dict(s1=8, W=0, Tp=1), 22: dict(s1=4, W=4, Tp=12, U=2)}


def body_ops(U, s1):
    """Operations of one loop body (U batches): batches, grouped filter, loop control and one move (proof 3.3)."""
    group = U * (1 + (1 if s1 < 32 else 0)) + (U - 1) + 3     # U adds [and U ands if s1 < 32], U-1 ands, 1 and, compare, branch
    return U * PH + group + 3 + 1


def _plan(n, Tp, tmax):
    c = CFG[n]
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


def plan(n):
    if n != 256:
        p = _plan(n, CFG[n]["Tp"], 0)
        p["tmax"] = 4 * (p["Q"] // int(p["L"])) + 64
        return p
    tmax = (MEM_LIMIT - code_bytes() - COUNTERS - REGFILE) // ENTRY
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


def main():
    req = json.load(sys.stdin)
    out = []
    for t in req["trials"]:
        a, b, obs = run_trial(t["seed"])
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


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    if arg == "--selftest":
        print("selftest", selftest(), "ops per batch", PH, PH_BY)
        print("peak live register values in one batch", peak_live(), "; with the group's 8 saved inputs and the filter accumulator", peak_live() + 9)
        print("grouped search equals per-batch search at n=22:", equivalence())
    elif arg == "--ledger":
        _print_ledger(ledger(256))
        p = plan(256)
        print("memory bytes", ENTRY * p["tmax"] + code_bytes() + COUNTERS + REGFILE, "limit", MEM_LIMIT)
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
