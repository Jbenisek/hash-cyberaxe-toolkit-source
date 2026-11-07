"""Circle invariant: the parity of a word (XOR of its bits) is unchanged by every rotation and is linear under XOR;
only the modular additions disturb it (parity(x+y) = parity(x)^parity(y)^parity(carry vector)).
Test: joint distribution of the 16 message-word parities and the 8 output-word parities (24 bits) over random
messages, Walsh-Hadamard transform -> every linear relation between them; report the largest |correlation|
against the noise level 2^(-log2N/2).  Also the same with the 16 parities of the round-0 output X (one round).
Usage: python parity.py <w> <log2N> [seed]
"""
import sys
import numpy as np

sys.dont_write_bytecode = True
import toy  # noqa: E402

U = np.uint64


def wparity(x, w):
    p = np.zeros_like(x)
    for b in range(w):
        p ^= (x >> U(b)) & U(1)
    return p


def wht(a):
    a = a.astype(np.float64).copy()
    h = 1
    n = a.size
    while h < n:
        a = a.reshape(-1, 2 * h)
        x, y = a[:, :h].copy(), a[:, h:].copy()
        a[:, :h], a[:, h:] = x + y, x - y
        a = a.reshape(n)
        h *= 2
    return a


def main(w, lg, seed):
    rng = np.random.default_rng(seed)
    N = 1 << lg
    M = rng.integers(0, 1 << w, size=(16, N), dtype=U)
    t = toy.vtrace(M, w)
    out, X = t["out"], t["X"]
    km = np.zeros(N, dtype=np.int64)
    for i in range(16):
        km |= (wparity(M[i], w).astype(np.int64) << i)
    for label, words, nb in (("2-round out", out, 8), ("1-round X0..7", X[:8], 8), ("1-round X8..15", X[8:], 8)):
        ko = np.zeros(N, dtype=np.int64)
        for i in range(nb):
            ko |= (wparity(words[i], w).astype(np.int64) << i)
        key = km | (ko << 16)
        hist = np.bincount(key, minlength=1 << (16 + nb))
        spec = wht(hist) / N
        spec = spec.reshape(1 << nb, 1 << 16)       # [output mask, message mask]
        spec[0, :] = 0                               # relations not involving the output are trivial
        a = np.abs(spec)
        idx = np.unravel_index(a.argmax(), a.shape)
        print(f"w={w} N=2^{lg} {label}: max |corr| = {a.max():.5f} (noise ~ {N ** -0.5:.5f}, x{a.max() * N ** 0.5:.1f}) "
              f"at output-mask {idx[0]:#x} message-mask {idx[1]:#06x}; #>7 sigma: {(a > 7 * N ** -0.5).sum()} (pure noise max ~5.6 sigma)",
              flush=True)


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]) if len(sys.argv) > 3 else 1)
