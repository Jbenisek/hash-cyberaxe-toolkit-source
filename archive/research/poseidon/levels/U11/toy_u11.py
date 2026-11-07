"""U11 toy experiments: collisions = bijection + truncation. Exhaustive over all q^2 inputs.
Toy: 3 lanes over F_q, x^5, rounds R0..R3 full, r partial, R60..R63 full, Cauchy MDS, random constants.
Usage: python toy_u11.py q seed r   (single process)"""
import sys, random, numpy as np
from math import gcd

def make_toy(q, seed):
    rnd = random.Random(seed)
    while True:
        xs = [rnd.randrange(q) for _ in range(3)]; ys = [rnd.randrange(q) for _ in range(3)]
        if len(set(xs)) == 3 and len(set(ys)) == 3 and all((x + y) % q for x in xs for y in ys):
            break
    M = [[pow(xs[i] + ys[j], -1, q) for j in range(3)] for i in range(3)]
    RC = [[rnd.randrange(q) for _ in range(3)] for _ in range(64)]
    return M, RC

def sched(r): return list(range(4)) + list(range(4, 4 + r)) + list(range(60, 64))

def run(q, M, RC, r, nk, rho, cap):
    """vectorised; returns list of (idx, state_after_M [3 arrays]) for each round"""
    s = [nk.copy(), rho.copy(), np.full_like(nk, cap % q)]
    out = []
    for idx in sched(r):
        full = idx < 4 or idx >= 60
        s = [(s[i] + RC[idx][i]) % q for i in range(3)]
        for i in (range(3) if full else range(1)):
            x = s[i]; x2 = x * x % q; x4 = x2 * x2 % q; s[i] = x4 * x % q
        s = [(M[i][0] * s[0] + M[i][1] * s[1] + M[i][2] * s[2]) % q for i in range(3)]
        out.append((idx, [a.copy() for a in s]))
    return out

def pairs_equal(keys):
    _, c = np.unique(keys, return_counts=True)
    c = c.astype(np.int64)
    return int((c * (c - 1) // 2).sum())

def main(q, seed, r):
    assert gcd(5, q - 1) == 1
    M, RC = make_toy(q, seed)
    cap = (1 << 65) % q
    N = q * q
    nk, rho = np.meshgrid(np.arange(q, dtype=np.int64), np.arange(q, dtype=np.int64), indexing='ij')
    nk = nk.ravel(); rho = rho.ravel()
    lv = run(q, M, RC, r, nk, rho, cap)
    names = [f"R{i}" for i, _ in lv]
    P = N * (N - 1) // 2
    print(f"## q={q} seed={seed} r={r} N={N} pairs={P} E[pairs equal in lane0 per level]={P/q:.1f}")
    # --- 1/2. full-state injectivity, fibres
    L = lv[-1][1]
    key3 = (L[0] * q + L[1]) * q + L[2]
    print("distinct full 3-lane outputs:", len(np.unique(key3)), "of", N, "(X1: must equal N)")
    key01 = L[0] * q + L[1]; key02 = L[0] * q + L[2]; key12 = L[1] * q + L[2]
    print("distinct (lane0,lane1):", len(np.unique(key01)), " (lane0,lane2):", len(np.unique(key02)),
          " (lane1,lane2):", len(np.unique(key12)), " lane0:", len(np.unique(L[0])))
    # inside fibres: pairs equal in lane0 AND lane1 / AND lane2 / AND both
    print("pairs equal lane0&lane1:", pairs_equal(key01), " lane0&lane2:", pairs_equal(key02),
          " (expected random ", P/q**2, ") lane0&lane1&lane2:", pairs_equal(key3))
    c = np.bincount(L[0], minlength=q)
    print("fibre sizes: min", c.min(), "max", c.max(), "mean", c.mean(), "var/mean", round(c.var() / c.mean(), 3), "empty", int((c == 0).sum()))
    # --- 4. per level pair agreement, cumulative chain, joint with final
    print("level | pairs equal lane0 | ratio vs P/q | cumulative-chain pairs (equal at all levels so far) | expected P/q^k | joint(level,final) | expected P/q^2")
    cum = np.zeros(N, dtype=np.int64)
    fin = L[0]
    for k, (idx, s) in enumerate(lv):
        e = pairs_equal(s[0])
        cum = cum * q + s[0] if k < 5 else cum  # only use first few levels (int64 safe)
        ch = pairs_equal(cum) if k < 5 else -1
        j = pairs_equal(s[0] * q + fin)
        print(f"{names[k]:>4} | {e} | {e/(P/q):.5f} | {ch} | {P/q**(k+1):.2f} | {j} | {P/q**2:.2f}")
    # --- exact: R0 fibres
    c0 = np.bincount(lv[0][1][0], minlength=q)
    print("R0.M lane0 fibre sizes: min", c0.min(), "max", c0.max(), "(PROVED: all q, a line in (A,B))")
    return M, RC, lv, cap

if __name__ == '__main__':
    q = int(sys.argv[1]); seed = int(sys.argv[2]); r = int(sys.argv[3])
    main(q, seed, r)
