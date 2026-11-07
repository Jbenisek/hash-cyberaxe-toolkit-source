"""Birthday collision search on 3-round BLAKE3-256 (blake3-r3-prefix-v1) with 7 packed lanes and distinguished points.

The chain message is 64 bytes: 32 zero bytes (words m0..m7) followed by x (words m8..m15, little endian): one
chunk, one block, flags 11, counter 0, length 64.  f(x) is the low n bits of the 256-bit little-endian digest
integer.  n = 256 is the claim; the organizer experiments run the same code with n = 22.
Sections: 1 scalar digest, 2 tracer (packed circuit and its operation count), 3 plan (every budget and halt as
exact integers) and ledger, 4 search and recovery, 5 organizer protocol.
"""
import sys
import json
import hashlib
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
U_UNROLL = 16                      # batches per loop body; loop control is 3 operations per body
DBITS = {256: 114, 40: 12, 32: 8, 22: 4}   # trail ends at a point whose low d bits are zero
KAPPA = 12                         # trail age cap in units of 2^d
LAMBDA = Fraction(497, 1000)       # 1 - exp(-LAMBDA) = 0.39165; the proof spends 1.2e-4 of the 1.65e-3 above 0.39
INFLIGHT = 28                      # points of the 7 unfinished trails at the halt, in units of 2^d (proof, Lemma 2)
CUTLOSS = Fraction(15, 100000)     # points on trails cut at the age cap, as a fraction of Q (proof, Lemma 2)
DP_EVENT_OPS = 700                 # one finished trail: lane extraction, fingerprint, restart (upper bound)
STAGE2_OPS = 300                   # one batch whose filter word has a zero lane (upper bound)
RECOVER_EXTRA = 64                 # per recovery batch: 8 shr + 8 xor + 7 or + 1 and + compare + branch = 26, loop add + compare + branch = 3, 29 needed (proof 3.3)


def plan(n):
    d = DBITS[n]
    L, N = 1 << d, 1 << n
    s1 = min(d, 32)                                    # bits tested by the one-word filter
    ureq = isqrt(2 * N * LAMBDA.numerator // LAMBDA.denominator) + 2
    num, den = ureq + INFLIGHT * L + 1, CUTLOSS.denominator
    q = -(-num * den // (den - CUTLOSS.numerator))
    b = -(-q // LANES)
    sb = (1 << 48) if n == 256 else 4 * U_UNROLL
    c = KAPPA * L
    return dict(n=n, d=d, L=L, N=N, s1=s1, Q=b * LANES, B=b, Sb=sb, c=c, capr=c + sb,
                tmax=(1 << 14) + (1 << 11) if n == 256 else 4 * (b * LANES // L) + 64,
                e2max=2 * b * LANES // (1 << s1) + 64)


def ledger(n=256):
    """Operation budget in word operations (exact Fractions); units are operations / 638 (C of blake3-r3)."""
    p = plan(n)
    stage1 = 4 + (1 if p["s1"] < 32 else 0)            # [and] add and compare branch
    per_body = U_UNROLL * (PH + stage1) + 3
    main = Fraction(per_body, U_UNROLL) * p["B"]
    parts = dict(main=main,
                 slices=-(-p["B"] // p["Sb"]) * 100,
                 stage2=p["e2max"] * STAGE2_OPS,
                 events=p["tmax"] * (DP_EVENT_OPS + 3 * p["tmax"]),
                 recovery=p["capr"] * (PH + RECOVER_EXTRA) + 600,
                 init=2000)                                    # setup: 1 random word, 7 starts <= 287, counters <= 25, folded constants <= 336 (proof 3.3)
    return dict(parts=parts, total=sum(parts.values()), plan=p, per_body=per_body)


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


def search(p, r):
    """One attempt with the fresh random word r: (pair or None, counters).  Raises Halt at a budget."""
    n, d, mask = p["n"], p["d"], p["N"] - 1
    bit32, s1mask, rep_ff = REP << 32, REP * ((1 << p["s1"]) - 1), REP * M32
    table, births, ts = {}, [0] * LANES, list(range(LANES))
    nxt = LANES
    cnt = dict(batches=0, stage2=0, finished=0, cut=0)
    inp = pack_x([(r + t) & mask for t in ts])
    while cnt["batches"] < p["B"]:
        z = batch(*inp)
        cnt["batches"] += 1
        if ((z[0] & s1mask) + rep_ff) & bit32 != bit32:       # filter: some lane has its tested bits zero
            cnt["stage2"] += 1
            if cnt["stage2"] > p["e2max"]:
                raise Halt("stage-2 budget")
            for l in range(LANES):
                x = lane_x(z, l) & mask
                if x & ((1 << d) - 1) == 0:
                    key, length = (x >> d) & ((1 << 64) - 1), cnt["batches"] - births[l]
                    cnt["finished"] += 1
                    if key in table:
                        res = recover(p, r, table[key], (ts[l], length))
                        if res is None:
                            raise Halt("recovery found no pair")
                        return res, cnt
                    if len(table) >= p["tmax"]:
                        raise Halt("table full")
                    table[key] = (ts[l], length)
                    ts[l], nxt, births[l] = nxt, nxt + 1, cnt["batches"]
                    z = set_lane(z, l, (r + ts[l]) & mask)
        if cnt["batches"] % p["Sb"] == 0:
            for l in range(LANES):
                if cnt["batches"] - births[l] >= p["c"]:
                    cnt["cut"] += 1
                    ts[l], nxt, births[l] = nxt, nxt + 1, cnt["batches"]
                    z = set_lane(z, l, (r + ts[l]) & mask)
        inp = feed(z, n)
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


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
        print("selftest", selftest(), "ops per batch", PH, PH_BY)
    elif len(sys.argv) > 1 and sys.argv[1] == "--ledger":
        from math import log2
        lg = ledger(256)
        print(lg["plan"])
        print("operations per 16 batches", lg["per_body"])
        for k, v in lg["parts"].items():
            print(k, v, "=", float(v))
        print("total operations", lg["total"], "=", float(lg["total"]))
        print("units (total / 638) =", float(lg["total"] / 638), "; time_log2 =", log2(lg["total"] / 638))
    else:
        main()
