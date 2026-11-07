"""tb3.py - vectorized 2-round BLAKE3 compression at word width w (w = 32 is the real one), with intermediates.

Own code (folder counter_swing\\around). Toy widths scale the rotations as floor(r*w/32) and take the top w bits of
each IV word, as the team's earlier toys did. selftest() checks w = 32 against the organizer's _compress
(copied here as org_blake3.py). Run: python -B tb3.py
"""
import numpy as np

IV32 = (0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A,
        0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19)
PERM = (2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8)
CALLS = ((0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15),
         (0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14))


class Toy:
    def __init__(self, w):
        self.w = w
        self.mask = np.uint32((1 << w) - 1) if w < 32 else np.uint32(0xFFFFFFFF)
        self.rot = tuple(max(1, (r * w) // 32) for r in (16, 12, 8, 7))
        self.iv = tuple((x >> (32 - w)) for x in IV32)

    def rotr(self, x, r):
        w = self.w
        return ((x >> np.uint32(r)) | (x << np.uint32(w - r))) & self.mask

    def g(self, v, a, b, c, d, x, y):
        m = self.mask
        R1, R2, R3, R4 = self.rot
        v[a] = (v[a] + v[b] + x) & m
        v[d] = self.rotr(v[d] ^ v[a], R1)
        v[c] = (v[c] + v[d]) & m
        v[b] = self.rotr(v[b] ^ v[c], R2)
        v[a] = (v[a] + v[b] + y) & m
        v[d] = self.rotr(v[d] ^ v[a], R3)
        v[c] = (v[c] + v[d]) & m
        v[b] = self.rotr(v[b] ^ v[c], R4)

    def init_state(self, n, cv=None, ctr_lo=0, ctr_hi=0, blen=64, flags=0):
        """cv: None (= IV) or list of 8 arrays; scalars or arrays for the rest."""
        u = np.uint32
        if cv is None:
            cv = [np.full(n, u(x)) for x in self.iv]
        v = [c.copy() for c in cv] + [np.full(n, u(x)) for x in self.iv[:4]]
        for val in (ctr_lo, ctr_hi, blen, flags):
            if np.isscalar(val):
                v.append(np.full(n, u(int(val) & int(self.mask))))
            else:
                v.append((np.asarray(val, dtype=np.uint32) & self.mask).copy())
        return v

    def compress(self, v0, m, rounds=2):
        """Returns dict: X = state after round 0, Y = state after round-1 column step, V = final state,
        out = 8 folded words v[i]^v[i+8]."""
        v = [x.copy() for x in v0]
        msg = list(m)
        res = {}
        for r in range(rounds):
            for i, (a, b, c, d) in enumerate(CALLS):
                self.g(v, a, b, c, d, msg[2 * i], msg[2 * i + 1])
                if i == 3 and r == 1:
                    res['Y'] = [x.copy() for x in v]
            if r == 0:
                res['X'] = [x.copy() for x in v]
            msg = [msg[i] for i in PERM]
        res['V'] = v
        res['out'] = [v[i] ^ v[i + 8] for i in range(8)]
        res['out16'] = res['out'] + [v[i + 8] ^ v0[i] for i in range(8)]
        return res


def absorb(toy, v_base, v_other, m_base, cols):
    """Message for the OTHER state so that round-0 column calls in `cols` give equal outputs.
    Column c has a = v[c], b = v[c+4], d = v[c+12], x = m[2c], y = m[2c+1]. Requires a, b, c equal."""
    mk = toy.mask
    m = [x.copy() for x in m_base]
    for c in cols:
        a, b, d, d2 = v_base[c], v_base[c + 4], v_base[c + 12], v_other[c + 12]
        a1 = (a + b + m_base[2 * c]) & mk
        a1o = a1 ^ d ^ d2
        m[2 * c] = (a1o - a - b) & mk
        m[2 * c + 1] = (m_base[2 * c + 1] + a1 - a1o) & mk
    return m


def selftest(n=200, seed=1):
    import random
    import org_blake3 as ob
    rnd = random.Random(seed)
    toy = Toy(32)
    bad = 0
    for _ in range(n):
        cv = [rnd.getrandbits(32) for _ in range(8)]
        words = [rnd.getrandbits(32) for _ in range(16)]
        ctr = rnd.getrandbits(52)
        blen = rnd.randint(0, 64)
        flags = rnd.choice([0, 1, 2, 3, 4, 8, 10, 11, 12])
        for rounds in (1, 2):
            ref = ob._compress(tuple(cv), tuple(words), ctr, blen, flags, rounds)
            v0 = toy.init_state(1, cv=[np.array([c], dtype=np.uint32) for c in cv],
                                ctr_lo=ctr & 0xFFFFFFFF, ctr_hi=ctr >> 32, blen=blen, flags=flags)
            r = toy.compress(v0, [np.array([x], dtype=np.uint32) for x in words], rounds)
            mine = tuple(int(x[0]) for x in r['out16'])
            bad += (mine != ref)
    return bad


if __name__ == '__main__':
    print('selftest vs organizer _compress (w=32, rounds 1 and 2, 200 random inputs each): mismatches =',
          selftest())
