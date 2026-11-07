"""absorb32.py - real 32-bit check, on the organizer's own functions (org_blake3.py = verifier/blake3.py copy),
that a leaf (last chunk, one 64-byte block) and a parent node can be made to agree on the whole state after
round 0, for every leaf-vs-parent placement the tree allows (tree_align.py), by copying the parent's message
(the two child CVs) and changing only the absorbing words of the columns whose d input differs.

Node descriptors come from the organizer's _chunk_output (leaf at chunk index t) and _parent_output (parent over
child chunks t and t+1, their CVs computed with _chunk_output/_compress at their true indices). Round-0 equality is
tested as equality of all 16 words of _compress(..., rounds=1): with cv = IV on both sides those 16 words fix the
state after round 0.
Run: python -B absorb32.py [trials]
"""
import random
import struct
import sys

import org_blake3 as ob

M32 = 0xFFFFFFFF
IV = ob.IV


def absorb_words(par_words, d_par, d_leaf, cols):
    """d_par / d_leaf: the 4 d inputs (v12..v15) of parent and leaf. Returns leaf words."""
    w = list(par_words)
    for c in cols:
        a, b = IV[c], IV[c + 4]                      # v0..v7 = IV on both sides (cv = IV)
        a1 = (a + b + par_words[2 * c]) & M32
        a1l = a1 ^ d_par[c] ^ d_leaf[c]
        w[2 * c] = (a1l - a - b) & M32
        w[2 * c + 1] = (par_words[2 * c + 1] + a1 - a1l) & M32
    return w


def one(rnd, t, root_level=False):
    """Returns (round0_equal, n_equal_cv_words_after_2_rounds, leaf_bytes_ok)."""
    if root_level:
        # M1 = one 64-byte chunk (root, flags 11); M2 = two chunks, root parent (flags 12) over chunk 0, chunk 1
        Y = bytes(rnd.getrandbits(8) for _ in range(1024))
        Z = bytes(rnd.getrandbits(8) for _ in range(rnd.randint(1, 1024)))
        cvY = ob._compress(*ob._chunk_output(Y, 0, 2), 2)[:8]
        cvZ = ob._compress(*ob._chunk_output(Z, 1, 2), 2)[:8]
        pcv, pw, pctr, plen, pfl = ob._parent_output(cvY, cvZ)
        pfl |= ob.ROOT
        d_par = (0, 0, plen, pfl)
        d_leaf = (0, 0, 64, 1 | 2 | ob.ROOT)
        cols = [3]
        lw = absorb_words(pw, d_par, d_leaf, cols)
        X = struct.pack('<16I', *lw)
        lcv, lwords, lctr, llen, lfl = ob._chunk_output(X, 0, 2)
        lfl |= ob.ROOT
        lctr = 0
    else:
        Y = bytes(rnd.getrandbits(8) for _ in range(1024))
        Z = bytes(rnd.getrandbits(8) for _ in range(rnd.randint(1, 1024)))
        cvY = ob._compress(*ob._chunk_output(Y, t, 2), 2)[:8]
        cvZ = ob._compress(*ob._chunk_output(Z, t + 1, 2), 2)[:8]
        pcv, pw, pctr, plen, pfl = ob._parent_output(cvY, cvZ)
        d_par = (pctr & M32, pctr >> 32, plen, pfl)
        d_leaf = (t & M32, t >> 32, 64, 3)
        cols = [c for c in range(4) if d_par[c] != d_leaf[c]]
        lw = absorb_words(pw, d_par, d_leaf, cols)
        X = struct.pack('<16I', *lw)
        lcv, lwords, lctr, llen, lfl = ob._chunk_output(X, t, 2)
    desc_ok = (lcv == IV and tuple(lwords) == tuple(lw) and llen == 64)
    r1p = ob._compress(pcv, pw, pctr, plen, pfl, 1)
    r1l = ob._compress(lcv, lwords, lctr, llen, lfl, 1)
    r2p = ob._compress(pcv, pw, pctr, plen, pfl, 2)[:8]
    r2l = ob._compress(lcv, lwords, lctr, llen, lfl, 2)[:8]
    neq = sum(1 for i in range(8) if r2p[i] == r2l[i])
    diffwords = [i for i in range(16) if pw[i] != lwords[i]]
    return r1p == r1l, neq, desc_ok, diffwords, (lctr, lfl, pctr, pfl)


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 500
    rnd = random.Random(8)
    cases = [
        ('root level: chunk root (flags 11) vs parent root (flags 12), t = 0', None),
        ('non-root, t = 2 (v12 differs)', 2),
        ('non-root, t = 2^31 (v12 differs)', 1 << 31),
        ('non-root, t = 2^32, k = 1 (v13 differs)', 1 << 32),
        ('non-root, t = 5 * 2^32 (v13 = 5)', 5 << 32),
        ('non-root, t = 2^50 (v13 = 2^18)', 1 << 50),
        ('non-root, t = 2^32 + 2 (v12 and v13 differ)', (1 << 32) + 2),
        ('non-root, t = (2^19 - 1) * 2^32 (largest k)', ((1 << 19) - 1) << 32),
    ]
    print('trials per case: %d' % n)
    for label, t in cases:
        eq = 0
        dok = 0
        hist = [0] * 9
        dws = set()
        info = None
        for _ in range(n):
            r0, neq, d_ok, dw, info = one(rnd, t if t is not None else 0, root_level=(t is None))
            eq += r0
            dok += d_ok
            hist[neq] += 1
            dws.add(tuple(dw))
        print('%-60s round-0 state equal %d/%d | leaf descriptor from _chunk_output ok %d/%d'
              % (label, eq, n, dok, n))
        print('    leaf (counter, flags) = (%d, %d), parent (counter, flags) = (%d, %d); message words that differ: %s'
              % (info[0], info[1], info[2], info[3], sorted(dws)[:3]))
        print('    after 2 rounds, number of the 8 CV/digest words equal: %s' % hist)


if __name__ == '__main__':
    main()
