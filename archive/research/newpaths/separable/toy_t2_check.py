"""Toy check that the table rules used in the model are 'generic' (a table key determines the unknowns,
about one solution per key on average), at w = 8 and w = 12, toy BLAKE3 rotations floor(r*w/32).

(a) K1 = G(IV1, IV5, IV1, 0; m2, m3): 2-word table rule (K1.a2, K1.c2) -> (m2, m3)   [T2 rule]
(b) round-1 column with a2, c2 constant: c -> d1 through c = c2 - d1 - ((d1 ^ a2) >>> R8)   [T1 rule]
Prints the image fraction (distinct keys / domain); a random function gives ~0.632, a bijection 1.0,
a degenerate map (key not determining the unknowns) gives a tiny fraction.
"""
import numpy as np

IV = [0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19]


def run(w):
    mask = (1 << w) - 1
    R = [(r * w) // 32 for r in (16, 12, 8, 7)]
    dt = np.uint32

    def rotr(x, r):
        return ((x >> dt(r)) | (x << dt(w - r))) & dt(mask)

    def G(a, b, c, d, x, y):
        a = (a + b + x) & dt(mask); d = rotr(d ^ a, R[0]); c = (c + d) & dt(mask); b = rotr(b ^ c, R[1])
        a = (a + b + y) & dt(mask); d = rotr(d ^ a, R[2]); c = (c + d) & dt(mask); b = rotr(b ^ c, R[3])
        return a, b, c, d

    iv = [dt(v & mask) for v in IV]
    n = 1 << (2 * w)
    allv = np.arange(n, dtype=np.uint64)
    m2 = (allv & mask).astype(dt)
    m3 = (allv >> np.uint64(w)).astype(dt)
    a2, b2, c2, d2 = G(iv[1], iv[5], iv[1], dt(0), m2, m3)
    key = a2.astype(np.uint64) | (c2.astype(np.uint64) << np.uint64(w))
    fa = len(np.unique(key)) / n
    rng = np.random.default_rng(w)
    fb = []
    for _ in range(8):
        A2, C2 = dt(rng.integers(0, 1 << w)), dt(rng.integers(0, 1 << w))
        d1 = np.arange(1 << w, dtype=dt)
        d2_ = rotr(d1 ^ A2, R[2])
        c = (C2 - d1 - d2_) & dt(mask)
        fb.append(len(np.unique(c)) / (1 << w))
    print(f"w={w}: (a) K1 (a2,c2)->(m2,m3) image fraction {fa:.3f};  (b) c->d1 image fraction "
          f"mean {np.mean(fb):.3f} min {min(fb):.3f} max {max(fb):.3f}")


if __name__ == "__main__":
    for w in (8, 12):
        run(w)
