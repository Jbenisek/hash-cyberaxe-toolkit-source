#!/usr/bin/env python3
"""verify_tree.py: independent toy BLAKE3 tree hash (research only, written separately from ctr_toy.c).

Generic in the word size W and the byte size: at W = 32 with 8-bit bytes and rotations (16,12,8,7) it is the
organizer's verifier/blake3.py with 2 rounds (checked here on random multi-chunk messages); at W = 8 it is the toy of
task5 (toy.h): IV = top 8 bits of the IV words, rotations (4,3,2,1), 2-bit toy bytes, 4 per word, block 64 toy
bytes, chunk 1024 toy bytes, counter split as (ctr mod 2^W, ctr >> W).

usage:
  python verify_tree.py selftest                      W=32 against hash-smash/verifier/blake3.py
  python verify_tree.py treetest FILE                  W=8: TT lines of ctr_toy treetest
  python verify_tree.py hits FILE [FILE ...]           W=8: every HIT line: rebuild P||A, P||B (P = t zero chunks),
                                                       hash both, require equal digests equal to the printed one
"""
import os, random, sys

IV32 = (0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19)
PERM = (2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8)
START, END, PARENT, ROOT = 1, 2, 4, 8


class Toy:
    def __init__(self, W, bbits, rots):
        self.W, self.M, self.bb, self.rots = W, (1 << W) - 1, bbits, rots
        self.bpw = W // bbits                      # bytes per word
        self.block = 16 * self.bpw                 # bytes per block
        self.chunk = 16 * self.block               # bytes per chunk
        self.iv = tuple(x >> (32 - W) for x in IV32)

    def ror(self, x, n):
        return ((x >> n) | (x << (self.W - n))) & self.M

    def g(self, v, a, b, c, d, x, y):
        M, r = self.M, self.rots
        v[a] = (v[a] + v[b] + x) & M; v[d] = self.ror(v[d] ^ v[a], r[0])
        v[c] = (v[c] + v[d]) & M;     v[b] = self.ror(v[b] ^ v[c], r[1])
        v[a] = (v[a] + v[b] + y) & M; v[d] = self.ror(v[d] ^ v[a], r[2])
        v[c] = (v[c] + v[d]) & M;     v[b] = self.ror(v[b] ^ v[c], r[3])

    def compress(self, cv, words, ctr, blen, flags):
        v = list(cv) + list(self.iv[:4]) + [ctr & self.M, (ctr >> self.W) & self.M, blen & self.M, flags & self.M]
        m = list(words)
        for _ in range(2):
            self.g(v, 0, 4, 8, 12, m[0], m[1]); self.g(v, 1, 5, 9, 13, m[2], m[3])
            self.g(v, 2, 6, 10, 14, m[4], m[5]); self.g(v, 3, 7, 11, 15, m[6], m[7])
            self.g(v, 0, 5, 10, 15, m[8], m[9]); self.g(v, 1, 6, 11, 12, m[10], m[11])
            self.g(v, 2, 7, 8, 13, m[12], m[13]); self.g(v, 3, 4, 9, 14, m[14], m[15])
            m = [m[i] for i in PERM]
        return [v[i] ^ v[i + 8] for i in range(8)]

    def words(self, blk):
        blk = list(blk) + [0] * (self.block - len(blk))
        return [sum(blk[i * self.bpw + j] << (self.bb * j) for j in range(self.bpw)) for i in range(16)]

    def chunk_output(self, ch, ctr):
        cv = self.iv
        last = max(0, (len(ch) - 1) // self.block * self.block)
        for off in range(0, last + 1, self.block):
            blk = ch[off:off + self.block]
            fl = START if off == 0 else 0
            if off == last:
                return cv, self.words(blk), ctr, len(blk), fl | END
            cv = self.compress(cv, self.words(blk), ctr, self.block, fl)

    def hash(self, data):
        n = max(1, (len(data) + self.chunk - 1) // self.chunk)
        stack = []
        for c in range(n - 1):
            cv = self.compress(*self.chunk_output(data[c * self.chunk:(c + 1) * self.chunk], c))
            tot = c + 1
            while tot & 1 == 0:
                cv = self.compress(self.iv, stack.pop() + cv, 0, self.block, PARENT)
                tot >>= 1
            stack.append(cv)
        out = self.chunk_output(data[(n - 1) * self.chunk:], n - 1)
        while stack:
            out = (self.iv, stack.pop() + self.compress(*out), 0, self.block, PARENT)
        cv, w, _, bl, fl = out
        return self.compress(cv, w, 0, bl, fl | ROOT)


def selftest():
    here = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.join(here, '..', '..', '..', '..', 'hash-smash', 'verifier'))
    import blake3 as ref
    T = Toy(32, 8, (16, 12, 8, 7))
    rng = random.Random(11)
    lens = [0, 1, 55, 63, 64, 65, 1023, 1024, 1025, 2048, 3000, 4096, 5000, 9000] + [rng.randrange(0, 12000) for _ in range(16)]
    bad = 0
    for L in lens:
        d = bytes(rng.randrange(256) for _ in range(L))
        mine = b''.join(x.to_bytes(4, 'little') for x in T.hash(list(d)))
        bad += mine != ref.blake3(d, rounds=2)
    print(f"SELFTEST W=32 against verifier/blake3.py rounds=2: {len(lens) - bad} of {len(lens)} equal (lengths up to {max(lens)} bytes)")
    return bad == 0


def toy8():
    return Toy(8, 2, (4, 3, 2, 1))


def treetest(fn):
    T, n, ok = toy8(), 0, 0
    for line in open(fn):
        if not line.startswith('TT '):
            continue
        f = line.split()
        L = int(f[1]); msg = [int(c) for c in f[2]] if L else []
        if L == 0:
            dig = [int(x, 16) for x in f[3:11]]
        else:
            dig = [int(x, 16) for x in f[4:12]]
        n += 1; ok += T.hash(msg) == dig
    print(f"TREETEST W=8 {fn}: {ok} of {n} equal to ctr_toy's tree hash")
    return ok == n


def hits(files):
    T = toy8()
    n = ok = 0
    per = {}
    for fn in files:
        for line in open(fn):
            if not line.startswith('HIT '):
                continue
            f = line.split()
            kv = {f[i]: f[i + 1] for i in range(1, len(f) - 9, 1) if f[i] in ('arr', 'set', 't', 'A', 'B')}
            arr, t = kv['arr'], int(kv['t'])
            A = [int(c) for c in kv['A']]; B = [int(c) for c in kv['B']]
            dig = [int(x, 16) for x in f[-8:]]
            P = [0] * (t * T.chunk)
            ha, hb = T.hash(P + A), T.hash(P + B)
            good = ha == hb and ha == dig and len(A) == 55 and len(B) == 63 and (arr == 'filed') == (t == 0)
            n += 1; ok += good
            per.setdefault(arr, [0, 0]); per[arr][0] += 1; per[arr][1] += good
    for a, (k, g) in sorted(per.items()):
        print(f"HITS arr {a}: {g} of {k} confirmed (full messages P||A, P||B hashed with the W=8 tree mode; equal digests = printed digest)")
    print(f"HITS all: {ok} of {n} confirmed")
    return ok == n


if __name__ == '__main__':
    if sys.argv[1] == 'selftest':
        sys.exit(0 if selftest() else 1)
    if sys.argv[1] == 'treetest':
        sys.exit(0 if treetest(sys.argv[2]) else 1)
    if sys.argv[1] == 'hits':
        import glob
        fs = [g for a in sys.argv[2:] for g in sorted(glob.glob(a)) if not g.endswith('progress.txt')]
        sys.exit(0 if hits(fs) else 1)
