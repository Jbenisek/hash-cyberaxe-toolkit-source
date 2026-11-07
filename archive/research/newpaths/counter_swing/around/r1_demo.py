"""r1_demo.py - real full-message collisions of the organizer's blake3 at rounds = 1 from the leaf-vs-parent
placement (different chunk counts, flags and counter as the difference). This is only a check that the round-0
cancellation is exact on real tree nodes of real messages; at 1 round the whole state after round 0 is the output.
Messages: M1 = P || X (t full chunks + one 64-byte block), M2 = P || Y || Z (t + 2 chunks), t in {0, 2, 4, 6, 8}.
X copies the parent block CV(Y) || CV(Z) except the absorbing words of the columns whose d input differs.
Run: python -B r1_demo.py > r1_demo.txt
"""
import hashlib
import random
import struct

import org_blake3 as ob

M32 = 0xFFFFFFFF


def build(rnd, t, rounds):
    P = bytes(rnd.getrandbits(8) for _ in range(t * 1024))
    Y = bytes(rnd.getrandbits(8) for _ in range(1024))
    Z = bytes(rnd.getrandbits(8) for _ in range(rnd.randint(1, 1024)))
    cvY = ob._compress(*ob._chunk_output(Y, t, rounds), rounds)[:8]
    cvZ = ob._compress(*ob._chunk_output(Z, t + 1, rounds), rounds)[:8]
    _, pw, _, _, pfl = ob._parent_output(cvY, cvZ)
    if t == 0:
        d_par, d_leaf = (0, 0, 64, pfl | ob.ROOT), (0, 0, 64, 3 | ob.ROOT)
    else:
        d_par, d_leaf = (0, 0, 64, pfl), (t & M32, t >> 32, 64, 3)
    w = list(pw)
    for c in range(4):
        if d_par[c] == d_leaf[c]:
            continue
        a, b = ob.IV[c], ob.IV[c + 4]
        a1 = (a + b + pw[2 * c]) & M32
        a1l = a1 ^ d_par[c] ^ d_leaf[c]
        w[2 * c] = (a1l - a - b) & M32
        w[2 * c + 1] = (pw[2 * c + 1] + a1 - a1l) & M32
    X = struct.pack('<16I', *w)
    return P + X, P + Y + Z


def main():
    rnd = random.Random(1001)
    print('t | len(M1) len(M2) | rounds=1 digests equal | rounds=2 digests equal | trials')
    shown = False
    for t in (0, 2, 4, 6, 8):
        eq1 = eq2 = 0
        n = 40
        for _ in range(n):
            M1, M2 = build(rnd, t, 1)
            assert M1 != M2
            d1a, d1b = ob.blake3(M1, 1), ob.blake3(M2, 1)
            eq1 += d1a == d1b
            eq2 += ob.blake3(M1, 2) == ob.blake3(M2, 2)
            if t == 0 and not shown:
                shown = True
                ex = (M1, M2, d1a)
        print('%d | %d %d | %d/%d | %d/%d' % (t, len(M1), len(M2), eq1, n, eq2, n))
    M1, M2, d = ex
    print('\nexample (t = 0): M1 = 64 bytes (one chunk, root flags 11), M2 = %d bytes (two chunks, root parent '
          'flags 12)' % len(M2))
    print('M1 hex:', M1.hex())
    print('M2 sha256:', hashlib.sha256(M2).hexdigest(), '(M2 = Y || Z with Y = 1024 bytes)')
    print('M2 hex:', M2.hex())
    print('blake3 rounds=1 digest of both:', d.hex())


if __name__ == '__main__':
    main()
