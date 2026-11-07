"""Shape-family survey on toy 2-round BLAKE3 (numpy).  Owner: shape_odd agent.

families : does a geometrically shaped message family make any group of output words take FEWER values
           (collision rate above uniform)?  A family whose half-digest has collision entropy h bits gives a
           birthday cost of 2^((h + rest)/2); uniform means no gain.
           Ratio = observed colliding pairs / expected for uniform keys, among DISTINCT messages of the family.
twists   : pairs (M, tau M) for twists tau (rotation, message permutation P and powers, torus shift, transpose,
           mirror, palindrome, complement, negation, x<->y swap).  Measures: equality rate out_j(tau M) == out_i(M)
           (and == ROT(out_i(M)) for rotations), max bit correlation, max XOR/additive difference frequency,
           and the XOR-sum around the closed orbit (Moebius closure) for tau of finite order.
Usage: python shapes.py families <w> <log2N> [seed]  |  python shapes.py twists <w> <log2N> [seed]
"""
import itertools
import sys
import numpy as np

sys.dont_write_bytecode = True
import toy  # noqa: E402

U = np.uint64
PERM = toy.PERM


def perm_power(k):
    p = list(range(16))
    for _ in range(k):
        p = [p[PERM[i]] for i in range(16)]
    return p


def classes_from_perm(p):
    """orbits of i -> p[i]"""
    seen, cls = set(), []
    for i in range(16):
        if i in seen:
            continue
        orb, j = [], i
        while j not in orb:
            orb.append(j)
            j = p[j]
        seen.update(orb)
        cls.append(orb)
    return cls


def classes_from_pairs(pairs):
    parent = list(range(16))

    def f(x):
        while parent[x] != x:
            x = parent[x]
        return x
    for a, b in pairs:
        parent[f(a)] = f(b)
    groups = {}
    for i in range(16):
        groups.setdefault(f(i), []).append(i)
    return list(groups.values())


CLASS_FAMILIES = {
    "P_invariant": classes_from_perm(PERM),                                   # 2 free words
    "P2_invariant": classes_from_perm(perm_power(2)),                         # 4 free words
    "P4_invariant": classes_from_perm(perm_power(4)),                         # 8 free words
    "torus_shift2": classes_from_pairs([(i, i ^ 4) for i in range(16)]),      # m_i = m_{i^4}: 8 free
    "torus_shift1": classes_from_pairs([(i, (i & 8) | ((i + 2) & 7)) for i in range(16)]),  # 4 free
    "transpose": classes_from_pairs([(4 * r + c, 4 * c + r) for r in range(4) for c in range(4)]),  # 10 free
    "mirror_i_i+8": classes_from_pairs([(i, i + 8) for i in range(8)]),       # 8 free
    "palindrome": classes_from_pairs([(i, 15 - i) for i in range(8)]),        # 8 free
    "x_equals_y": classes_from_pairs([(2 * j, 2 * j + 1) for j in range(8)]),  # 8 free
    "all_equal": [list(range(16))],                                           # 1 free
    "msg_square_D0D3": None,   # special: only m8,m9,m14,m15 vary (the D0-D3-E2-E3 square module)
    "msg_square_K2D2": None,   # special: only m4,m5,m12,m13 vary (the K2-C3-D2-E1 square module)
    "solF_m5m8m12m15": None,   # special: only Sol's F words vary (each seen once by half A)
}


def gen_family(name, rng, N, w):
    m = (1 << w) - 1
    if name == "uniform":
        return rng.integers(0, 1 << w, size=(16, N), dtype=U)
    if name == "circle_period_half":      # every word invariant under ROT_{w/2}: the ring folded once
        h = w // 2
        z = rng.integers(0, 1 << h, size=(16, N), dtype=U)
        return z | (z << U(h))
    if name == "circle_period_quarter":   # invariant under ROT_{w/4}
        q = w // 4
        z = rng.integers(0, 1 << q, size=(16, N), dtype=U)
        return z | (z << U(q)) | (z << U(2 * q)) | (z << U(3 * q))
    if name.startswith("sphere_r"):       # Hamming ball of radius r around a random centre
        r = int(name[len("sphere_r"):])
        centre = rng.integers(0, 1 << w, size=(16, 1), dtype=U)
        M = np.repeat(centre, N, axis=1)
        for _ in range(r):
            pos = rng.integers(0, 16 * w, size=N)
            word, bit = pos // w, pos % w
            M[word, np.arange(N)] ^= (U(1) << bit.astype(U))
        return M
    if name == "msb_only":                # centre, only the top bit of each word varies (2^16 members)
        centre = rng.integers(0, 1 << w, size=(16, 1), dtype=U)
        bits = rng.integers(0, 2, size=(16, N), dtype=U)
        return (centre & U(m >> 1)) | (bits << U(w - 1))
    if name in ("msg_square_D0D3", "msg_square_K2D2", "solF_m5m8m12m15"):
        vary = {"msg_square_D0D3": (8, 9, 14, 15), "msg_square_K2D2": (4, 5, 12, 13),
                "solF_m5m8m12m15": (5, 8, 12, 15)}[name]
        centre = rng.integers(0, 1 << w, size=(16, 1), dtype=U)
        M = np.repeat(centre, N, axis=1)
        for i in vary:
            M[i] = rng.integers(0, 1 << w, size=N, dtype=U)
        return M
    cls = CLASS_FAMILIES[name]
    M = np.zeros((16, N), dtype=U)
    for c in cls:
        z = rng.integers(0, 1 << w, size=N, dtype=U)
        for i in c:
            M[i] = z
    return M


FAMILIES = ["uniform", "circle_period_half", "circle_period_quarter", "sphere_r2", "sphere_r3", "msb_only",
            "P_invariant", "P2_invariant", "P4_invariant", "torus_shift2", "torus_shift1", "transpose",
            "mirror_i_i+8", "palindrome", "x_equals_y", "all_equal",
            "msg_square_D0D3", "msg_square_K2D2", "solF_m5m8m12m15"]


def dedupe(M, w):
    """keep distinct messages (columns)"""
    per = 64 // w
    keys = np.zeros((M.shape[1], -(-16 // per)), dtype=U)
    for i in range(16):
        keys[:, i // per] |= M[i] << U((i % per) * w)
    _, idx = np.unique(keys, axis=0, return_index=True)
    return M[:, np.sort(idx)]


def pairs_equal(key):
    s = np.sort(key)
    eq = s[1:] == s[:-1]
    if not eq.any():
        return 0
    # run lengths of equal keys
    d = np.diff(np.concatenate(([0], eq.astype(np.int8), [0])))
    starts, ends = np.where(d == 1)[0], np.where(d == -1)[0]
    L = (ends - starts + 1).astype(np.float64)
    return float((L * (L - 1) / 2).sum())


def pack(out, words, w):
    k = np.zeros(out.shape[1], dtype=U)
    for t, i in enumerate(words):
        k |= out[i] << U(t * w)
    return k


def families(w, lg, seed):
    rng = np.random.default_rng(seed)
    N = 1 << lg
    print(f"# families w={w} N=2^{lg} seed={seed}; ratio = colliding pairs / uniform expectation (distinct msgs D)")
    print("# columns: family D | halfA(0,2,5,7) halfB(1,3,4,6) | single words min..max | worst pair | "
          "worst 4-group (w<=8 only) | full-digest collisions (w=8)")
    groups4 = list(itertools.combinations(range(8), 4)) if 4 * w <= 32 else []
    pairs2 = list(itertools.combinations(range(8), 2))
    for name in FAMILIES:
        M = dedupe(gen_family(name, rng, N, w), w)
        D = M.shape[1]
        out = toy.vout(M, w)
        npairs = D * (D - 1) / 2

        def ratio(words):
            bits = w * len(words)
            if bits > 64:
                return None, None
            obs = pairs_equal(pack(out, words, w))
            exp = npairs / 2.0 ** bits
            return obs / exp if exp > 0 else float("nan"), (obs, exp)
        hA, cA = ratio((0, 2, 5, 7))
        hB, cB = ratio((1, 3, 4, 6))
        singles = [ratio((i,))[0] for i in range(8)]
        pr = [(ratio(p)[0], p) for p in pairs2]
        pmax = max(pr)
        line = (f"{name:24s} D=2^{np.log2(D):5.2f} | A {hA:7.3f} ({cA[0]:.0f}/{cA[1]:.1f}) B {hB:7.3f} "
                f"({cB[0]:.0f}/{cB[1]:.1f}) | single {min(singles):.3f}..{max(singles):.3f} | "
                f"pair max {pmax[0]:.3f} {pmax[1]}")
        if groups4:
            g = [(ratio(q)[0], q) for q in groups4]
            gm = max(g)
            gmin = min(g)
            line += f" | 4grp max {gm[0]:.3f} {gm[1]} min {gmin[0]:.3f}"
        if 8 * w <= 64:
            fullobs = pairs_equal(pack(out, range(8), w))
            line += f" | full {fullobs:.0f} (exp {npairs / 2.0 ** (8 * w):.2e})"
        print(line, flush=True)


# ---------------------------------------------------------------- twists
def twist(name, M, w):
    m = U((1 << w) - 1)
    if name == "rot1":
        return toy.vrotr(M, 1, w)
    if name == "rot_half":
        return toy.vrotr(M, w // 2, w)
    if name.startswith("P"):
        k = {"P": 1, "Pinv": 7, "P2": 2, "P4": 4}[name]
        p = perm_power(k)
        return M[p]
    if name == "torus_shift2":
        return M[[i ^ 4 for i in range(16)]]
    if name == "torus_shift1":
        return M[[(i & 8) | ((i + 2) & 7) for i in range(16)]]
    if name == "transpose":
        return M[[4 * (i % 4) + i // 4 for i in range(16)]]
    if name == "mirror":
        return M[[(i + 8) % 16 for i in range(16)]]
    if name == "palindrome":
        return M[[15 - i for i in range(16)]]
    if name == "swap_xy":
        return M[[i ^ 1 for i in range(16)]]
    if name == "complement":
        return M ^ m
    if name == "negation":
        return (U(0) - M) & m
    if name == "random":
        return None
    raise ValueError(name)


TWISTS = {"rot1": 0, "rot_half": 2, "P": 8, "Pinv": 8, "P2": 4, "P4": 2, "torus_shift2": 2, "torus_shift1": 4,
          "transpose": 2, "mirror": 2, "palindrome": 2, "swap_xy": 2, "complement": 2, "negation": 2, "random": 0}


def bits_pm(out, w):
    B = np.empty((out.shape[1], 8 * w), dtype=np.float32)
    for i in range(8):
        for b in range(w):
            B[:, i * w + b] = ((out[i] >> U(b)) & U(1)).astype(np.float32) * 2 - 1
    return B


def twists(w, lg, seed):
    rng = np.random.default_rng(seed)
    N = 1 << lg
    m = (1 << w) - 1
    M = rng.integers(0, 1 << w, size=(16, N), dtype=U)
    out = toy.vout(M, w)
    Bo = bits_pm(out, w)
    sig = 1 / np.sqrt(N)
    print(f"# twists w={w} N=2^{lg} seed={seed}.  eq = max_ij Pr[out_j(tM)==out_i(M)] * 2^w (uniform 1); "
          f"rot-eq for rotations: == ROT(out_i(M)); corr = max |bit correlation| / sigma (sigma=2^-{lg / 2:.0f}); "
          "xdiff/adiff = max_i max_delta Pr[diff=delta]*2^w; orbit = XOR of out over the closed orbit: max |bit bias|/sigma")
    for name, order in TWISTS.items():
        if name == "random":
            M2 = rng.integers(0, 1 << w, size=(16, N), dtype=U)
        else:
            M2 = twist(name, M, w)
        out2 = toy.vout(M2, w)
        same_msg = np.all(M2 == M, axis=0).mean()
        eq = np.zeros((8, 8))
        for i in range(8):
            for j in range(8):
                eq[i, j] = (out2[j] == out[i]).mean() * (1 << w)
        line = f"{name:13s} msg-fixed {same_msg:.4f} | eq max {eq.max():6.3f} at {np.unravel_index(eq.argmax(), eq.shape)}"
        if name in ("rot1", "rot_half"):
            r = 1 if name == "rot1" else w // 2
            req = max((out2[j] == toy.vrotr(out[i], r, w)).mean() * (1 << w) for i in range(8) for j in range(8))
            rdiag = [(out2[i] == toy.vrotr(out[i], r, w)).mean() * (1 << w) for i in range(8)]
            line += f" | rot-eq max {req:6.3f} diag {min(rdiag):.3f}..{max(rdiag):.3f}"
        B2 = bits_pm(out2, w)
        C = (Bo.T @ B2) / N
        line += f" | corr {np.abs(C).max() / sig:5.2f}"
        xd = ad = 0.0
        for i in range(8):
            x = out[i] ^ out2[i]
            a = (out2[i] - out[i]) & U(m)
            xd = max(xd, np.bincount(x.astype(np.int64), minlength=1 << w).max() / N * (1 << w))
            ad = max(ad, np.bincount(a.astype(np.int64), minlength=1 << w).max() / N * (1 << w))
        line += f" | xdiff {xd:6.3f} adiff {ad:6.3f}"
        if order >= 2 and name != "random":
            S = out.copy()
            Mt = M
            for _ in range(order - 1):
                Mt = twist(name, Mt, w)
                S ^= toy.vout(Mt, w)
            Bs = bits_pm(S, w)
            bias = np.abs(Bs.mean(axis=0)).max() / sig
            zero = (S == 0).mean() * (1 << w)
            line += f" | orbit(k={order}) bias {bias:5.2f} Pr[word=0]*2^w {zero:6.3f}"
        print(line, flush=True)


if __name__ == "__main__":
    cmd, w, lg = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    {"families": families, "twists": twists}[cmd](w, lg, seed)
