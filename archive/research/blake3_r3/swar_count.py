"""SWAR (lane-parallel) BLAKE3 prefix-round evaluator with op counting (own code).
256-bit words hold LANES independent instances in PITCH-bit lanes (32 data bits + guard bits).
Primitive ops counted (one each): add, and, or, xor, shl, shr, (compare, branch counted separately by caller).
Values known at precompute time ('const' = same in every lane and independent of the chain) cost nothing.
Validation: lane results are compared with the organizer-style scalar compression (verifier/blake3.py logic) for random inputs.
"""
import random, sys, json

W256 = (1 << 256) - 1
MASK32 = 0xFFFFFFFF
IV = (0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19)
PERM = (2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8)

def scalar_digest(words, rounds, flags=11, block_len=64, counter=0):
    def ror(v, n): return ((v >> n) | (v << (32 - n))) & MASK32
    v = list(IV) + list(IV[:4]) + [counter & MASK32, counter >> 32, block_len, flags]
    m = list(words)
    def g(a, b, c, d, x, y):
        v[a] = (v[a] + v[b] + x) & MASK32; v[d] = ror(v[d] ^ v[a], 16)
        v[c] = (v[c] + v[d]) & MASK32; v[b] = ror(v[b] ^ v[c], 12)
        v[a] = (v[a] + v[b] + y) & MASK32; v[d] = ror(v[d] ^ v[a], 8)
        v[c] = (v[c] + v[d]) & MASK32; v[b] = ror(v[b] ^ v[c], 7)
    for _ in range(rounds):
        g(0, 4, 8, 12, m[0], m[1]); g(1, 5, 9, 13, m[2], m[3]); g(2, 6, 10, 14, m[4], m[5]); g(3, 7, 11, 15, m[6], m[7])
        g(0, 5, 10, 15, m[8], m[9]); g(1, 6, 11, 12, m[10], m[11]); g(2, 7, 8, 13, m[12], m[13]); g(3, 4, 9, 14, m[14], m[15])
        m = [m[i] for i in PERM]
    return tuple(v[i] ^ v[i + 8] for i in range(8))

class Machine:
    def __init__(self, pitch, mask_policy=True):
        self.pitch = pitch
        self.lanes = 256 // pitch
        self.ops = 0
        self.by = {}
        self.limit = (1 << pitch) - 1          # lane value must stay below 2^pitch
        self.rep = sum(1 << (pitch * i) for i in range(self.lanes))
        self.M32 = self.rep * MASK32
    def tick(self, name, var):
        if var:
            self.ops += 1
            self.by[name] = self.by.get(name, 0) + 1

class V:
    __slots__ = ("m", "v", "var", "bound")
    def __init__(self, m, v, var, bound):
        self.m, self.v, self.var, self.bound = m, v, var, bound
        assert bound <= m.limit, ("lane overflow", bound, m.limit)
    @staticmethod
    def const(m, x):                      # same 32-bit constant in every lane
        return V(m, m.rep * x, False, MASK32)
    @staticmethod
    def packed(m, xs):                    # one value per lane (variable)
        v = 0
        for i, x in enumerate(xs): v |= x << (m.pitch * i)
        return V(m, v, True, MASK32)
    def __add__(s, o):
        if not (s.var or o.var):
            return V.const(s.m, ((s.v & MASK32) + (o.v & MASK32)) & MASK32)
        while s.bound + o.bound > s.m.limit:
            if s.bound >= o.bound and s.var and s.bound > MASK32: s = s.mask()
            elif o.var and o.bound > MASK32: o = o.mask()
            else: raise AssertionError(("cannot fit", s.bound, o.bound, s.var, o.var))
        s.m.tick("add", s.var or o.var)
        return V(s.m, (s.v + o.v) & W256, s.var or o.var, s.bound + o.bound)
    def __xor__(s, o):
        if not (s.var or o.var):
            return V.const(s.m, (s.v & MASK32) ^ (o.v & MASK32))
        s.m.tick("xor", s.var or o.var)
        b = (1 << max(s.bound.bit_length(), o.bound.bit_length())) - 1
        return V(s.m, s.v ^ o.v, s.var or o.var, b)
    def mask(s):
        s.m.tick("and", s.var)
        return V(s.m, s.v & s.m.M32, s.var, min(s.bound, MASK32))
    def ror(s, r):
        m = s.m
        if not s.var:
            x = s.v & MASK32
            return V.const(m, ((x >> r) | (x << (32 - r))) & MASK32)
        lowm = m.rep * ((1 << r) - 1)
        highm = m.rep * (MASK32 ^ ((1 << r) - 1))
        low = s.v & lowm; high = s.v & highm
        m.tick("and", s.var); m.tick("and", s.var)
        hi2 = high >> r; lo2 = (low << (32 - r)) & W256
        m.tick("shr", s.var); m.tick("shl", s.var); m.tick("or", s.var)
        return V(m, hi2 | lo2, s.var, MASK32)

def g_call(st, a, b, c, d, x, y):
    A, B, C, D = st[a], st[b], st[c], st[d]
    # pre-mask guards so that the worst case stays inside the lane
    if not A.var:  # constants: fold (a+b) first when both constant
        pass
    A = (A + B) + x
    D = (D ^ A).ror(16)
    C = C + D
    B = (B ^ C).ror(12)
    A = (A + B) + y
    D = (D ^ A).ror(8)
    C = C + D
    B = (B ^ C).ror(7)
    st[a], st[b], st[c], st[d] = A, B, C, D

def run(pitch, rounds, free_words, trials=20, seed=1, verbose=True):
    rng = random.Random(seed)
    m = Machine(pitch)
    L = m.lanes
    const_msg = [rng.getrandbits(32) for _ in range(16)]
    lane_msgs = [[const_msg[i] if i not in free_words else rng.getrandbits(32) for i in range(16)] for _ in range(L)]
    msg = []
    for i in range(16):
        if i in free_words: msg.append(V.packed(m, [lane_msgs[l][i] for l in range(L)]))
        else: msg.append(V.const(m, const_msg[i]))
    st = [V.const(m, x) for x in IV] + [V.const(m, x) for x in IV[:4]] + [V.const(m, 0), V.const(m, 0), V.const(m, 64), V.const(m, 11)]
    mi = list(range(16))
    for r in range(rounds):
        mm = [msg[i] for i in mi]
        for j, (a, b, c, d) in enumerate([(0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15), (0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14)]):
            g_call(st, a, b, c, d, mm[2 * j], mm[2 * j + 1])
        mi = [mi[i] for i in PERM]
    dig = []
    for i in range(8):
        z = st[i] ^ st[i + 8]
        if z.bound > MASK32: z = z.mask()
        dig.append(z)
    # validate lanes
    ok = True
    for l in range(L):
        exp = scalar_digest(lane_msgs[l], rounds)
        got = tuple((dig[i].v >> (pitch * l)) & MASK32 for i in range(8))
        if exp != got: ok = False
    return m, ok

if __name__ == "__main__":
    out = {}
    for rounds in (1, 2, 3):
        for pitch in (34, 36):
            for name, free in (("m8..m15", set(range(8, 16))), ("all16", set(range(16)))):
                m, ok = run(pitch, rounds, free)
                per_batch = m.ops
                print(f"rounds={rounds} pitch={pitch} lanes={m.lanes} free={name:8s} ok={ok} ops/batch={per_batch}  ops/instance={per_batch/m.lanes:.2f}  by={m.by}")
