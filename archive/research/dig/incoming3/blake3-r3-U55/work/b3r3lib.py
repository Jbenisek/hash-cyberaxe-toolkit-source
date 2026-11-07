"""Own code for the blake3-r3 dig (units U55-U63): scalar BLAKE3 with every state constant a parameter,
and a taint-tracking copy of the FILED circuit tracer (research/blake3_r3/candidate_blake3/experiments/rho.py,
Tracer + build_hash) with the same operation rules, so that its total reproduces the filed 595 ops per 7-lane batch.
Validation (run `python b3r3lib.py`): full 7-round BLAKE3 vectors (empty input, input [0]), organizer verifier at 3 and 7
rounds for 0^32||x, filed batch() ops (595)."""
import sys, os, random, struct
M32 = 0xFFFFFFFF
IV = (0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19)
PERM = (2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8)
GCALLS = ((0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15), (0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14))
CALLNAME = ("C0", "C1", "C2", "C3", "D0", "D1", "D2", "D3")
PITCH, LANES = 36, 7
LIM = 1 << PITCH
REP = sum(1 << (PITCH * i) for i in range(LANES))
HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, *[".."] * 5))      # workspace


def ror(v, k):
    return ((v >> k) | (v << (32 - k))) & M32


def schedule(rounds=3):
    """S[r][p] = index of the message word read at position p (0..15) of round r."""
    s = list(range(16))
    out = []
    for _ in range(rounds):
        out.append(list(s))
        s = [s[i] for i in PERM]
    return out


def init_state(h=IV, iv4=IV[:4], ctr=0, blen=64, flags=11):
    return list(h) + list(iv4) + [ctr & M32, ctr >> 32, blen, flags]


def compress(m, rounds=3, state=None, perturb=None, record=None):
    """scalar compression. perturb(r, j, pos, value) -> value changes ONE read; record gets (r, j, pos, idx)"""
    v = list(state if state is not None else init_state())
    mm = list(m)
    idx = list(range(16))
    for r in range(rounds):
        for j, (a, b, c, d) in enumerate(GCALLS):
            xs = []
            for pos in (0, 1):
                val = mm[2 * j + pos]
                if record is not None:
                    record.append((r, j, pos, idx[2 * j + pos]))
                if perturb is not None:
                    val = perturb(r, j, pos, val)
                xs.append(val)
            x, y = xs
            v[a] = (v[a] + v[b] + x) & M32; v[d] = ror(v[d] ^ v[a], 16)
            v[c] = (v[c] + v[d]) & M32; v[b] = ror(v[b] ^ v[c], 12)
            v[a] = (v[a] + v[b] + y) & M32; v[d] = ror(v[d] ^ v[a], 8)
            v[c] = (v[c] + v[d]) & M32; v[b] = ror(v[b] ^ v[c], 7)
        mm = [mm[i] for i in PERM]
        idx = [idx[i] for i in PERM]
    return [v[i] ^ v[i + 8] for i in range(8)]


def digest_f(x_words, rounds=3, state=None, perturb=None):
    return compress([0] * 8 + list(x_words), rounds, state, perturb)


class Tracer:
    """Value: ('c', k, taint) constant in every lane (taint = frozenset of names it depends on), or ('v', reg, bound).
    Rules copied from the filed Tracer: add folds constants, skips a zero constant, masks when the lane bound would reach 2^36;
    xor with constant 0 is free; ror of a constant folds; ror of a variable is shr,and,shl,and,or (5 ops)."""

    def __init__(self, log=False):
        self.ops, self.by, self.k = 0, {}, 0
        self.log = [] if log else None
        self.site = None

    def emit(self, kind):
        self.k += 1
        self.ops += 1
        self.by[kind] = self.by.get(kind, 0) + 1
        return "t%d" % self.k

    def mask(self, a):
        return ("v", self.emit("and"), M32)

    def add(self, *xs):
        cs = [x for x in xs if x[0] == "c"]
        c = sum(x[1] for x in cs) & M32
        taint = frozenset().union(*[x[2] for x in cs]) if cs else frozenset()
        vs = [x for x in xs if x[0] == "v"]
        if not vs:
            return ("c", c, taint)
        acc = vs[0]
        for v in vs[1:]:
            while acc[2] + v[2] >= LIM:
                if acc[2] >= v[2]:
                    acc = self.mask(acc)
                else:
                    v = self.mask(v)
            acc = ("v", self.emit("add"), acc[2] + v[2])
        if self.log is not None and cs:
            self.log.append((self.site, "addconst", c, sorted(taint), c == 0))
        if c:
            if acc[2] + c >= LIM:
                acc = self.mask(acc)
            acc = ("v", self.emit("add"), acc[2] + c)
        return acc

    def xor(self, a, b):
        if a[0] == "c" and b[0] == "c":
            return ("c", a[1] ^ b[1], a[2] | b[2])
        if a[0] == "c":
            a, b = b, a
        if b[0] == "c":
            if self.log is not None:
                self.log.append((self.site, "xorconst", b[1], sorted(b[2]), b[1] == 0))
            if b[1] == 0:
                return a
            return ("v", self.emit("xor"), (1 << max(a[2].bit_length(), b[1].bit_length())) - 1)
        return ("v", self.emit("xor"), (1 << max(a[2].bit_length(), b[2].bit_length())) - 1)

    def ror(self, a, r):
        if a[0] == "c":
            return ("c", ror(a[1], r), a[2])
        last = None
        for kind in ("shr", "and", "shl", "and", "or"):
            last = self.emit(kind)
        return ("v", last, M32)


def trace(state=None, msgconst=None, free=None, rounds=3, log=False, drop=None):
    """Trace the circuit. state: 16 initial words (constants tainted 'v<i>'). m0..m7 constants from msgconst (default 0, taint 'm<i>');
    words in `free` are variable (bound M32). drop = (r, j, pos) replaces that read by constant 0 (counterfactual).
    Returns (tracer, per) with per[(r, j)] = ops of the call, of the x-add (statement s1) and of the y-add (s5)."""
    st = state if state is not None else init_state()
    tr = Tracer(log)
    v = [("c", w & M32, frozenset(["v%d" % i])) for i, w in enumerate(st)]
    mc = msgconst if msgconst is not None else [0] * 8
    free = set(range(8, 16)) if free is None else set(free)
    m = [("v", "i%d" % i, M32) if i in free else ("c", (mc[i] if i < len(mc) else 0) & M32, frozenset(["m%d" % i])) for i in range(16)]
    per = {}
    for r in range(rounds):
        for j, (a, b, c, d) in enumerate(GCALLS):
            x, y = m[2 * j], m[2 * j + 1]
            if drop == (r, j, 0):
                x = ("c", 0, frozenset())
            if drop == (r, j, 1):
                y = ("c", 0, frozenset())
            k0 = tr.ops
            tr.site = (r, j, "s1"); v[a] = tr.add(v[a], v[b], x); k1 = tr.ops
            tr.site = (r, j, "s2"); v[d] = tr.ror(tr.xor(v[d], v[a]), 16)
            tr.site = (r, j, "s3"); v[c] = tr.add(v[c], v[d])
            tr.site = (r, j, "s4"); v[b] = tr.ror(tr.xor(v[b], v[c]), 12)
            tr.site = (r, j, "s5"); k2 = tr.ops; v[a] = tr.add(v[a], v[b], y); k3 = tr.ops
            tr.site = (r, j, "s6"); v[d] = tr.ror(tr.xor(v[d], v[a]), 8)
            tr.site = (r, j, "s7"); v[c] = tr.add(v[c], v[d])
            tr.site = (r, j, "s8"); v[b] = tr.ror(tr.xor(v[b], v[c]), 7)
            per[(r, j)] = dict(total=tr.ops - k0, xadd=k1 - k0, yadd=k3 - k2)
        m = [m[i] for i in PERM]
    for i in range(8):
        tr.site = ("out", i, "z")
        z = tr.xor(v[i], v[i + 8])
        if z[0] == "v" and z[2] > M32:
            z = tr.mask(z)
    return tr, per


def _selftest():
    sys.path.insert(0, os.path.join(WS, "research", "poseidon", "pareto_clone"))
    from verifier import blake3 as ver

    def full(data):
        w = list(struct.unpack("<16I", data.ljust(64, b"\0")))
        d = compress(w, 7, init_state(blen=len(data), flags=11))
        return struct.pack("<8I", *d).hex()
    assert full(b"") == "af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262", "empty vector"
    assert full(b"\x00") == "2d3adedff11b61f14c886e35afa036736dcd87a74d27b5c1510225d0f592e213", "len1 vector"
    rng = random.Random(5)
    for rounds in (3, 7):
        for _ in range(300):
            x = [rng.getrandbits(32) for _ in range(8)]
            data = bytes(32) + struct.pack("<8I", *x)
            assert struct.pack("<8I", *digest_f(x, rounds)).hex() == ver.blake3(data, rounds).hex()
    tr, per = trace()
    assert tr.ops == 595, tr.ops
    sys.path.insert(0, os.path.join(WS, "research", "blake3_r3", "candidate_blake3", "experiments"))
    import rho
    assert rho.PH == 595 and rho.PH_BY == tr.by, (rho.PH, rho.PH_BY, tr.by)
    print("selftest ok: 7-round vectors (empty, [0]), verifier at 3 and 7 rounds (600 cases), trace ops", tr.ops, tr.by, "= filed", rho.PH)


if __name__ == "__main__":
    _selftest()
