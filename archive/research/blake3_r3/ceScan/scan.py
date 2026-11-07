import numpy as np, sys, time, json, itertools, math
from b3np import comp, U, ror
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 12345
rng = np.random.default_rng(SEED)
Z = lambda N: np.zeros(N, U)
def rw(N): return rng.integers(0, 2**32, N, dtype=np.uint64).astype(U)
def base(N): return [Z(N) for _ in range(16)]
def rotr(x, r):
    return (x >> U(r)) | (x << U(32 - r)) if r % 32 else x.copy()

PROJ = ['lo24', 'hi24', 'xor24', 'lo3each', 'hi3each', 'mid3each', 'xorrot24', 'lo28', 'xor28']
NB = {'lo24': 24, 'hi24': 24, 'xor24': 24, 'lo3each': 24, 'hi3each': 24, 'mid3each': 24, 'xorrot24': 24, 'lo28': 28, 'xor28': 28}
def projections(d):
    x = d[0].copy()
    xr = d[0].copy()
    for i, w in enumerate(d[1:], 1):
        x ^= w
        xr ^= ror(w, 5 * i % 32)
    def each(sh):
        r = np.zeros(len(d[0]), np.uint32)
        for i, w in enumerate(d): r |= ((w >> U(sh)) & U(7)) << U(3 * i)
        return r
    return {'lo24': d[0] & U(0xFFFFFF), 'hi24': d[7] >> U(8), 'xor24': x & U(0xFFFFFF), 'lo3each': each(0),
            'hi3each': each(29), 'mid3each': each(13), 'xorrot24': xr >> U(8), 'lo28': d[3] & U(0xFFFFFFF), 'xor28': (x >> U(4))}
def coll(a):
    a = np.sort(a); n = len(a)
    idx = np.flatnonzero(np.diff(a) != 0)
    ends = np.concatenate([idx + 1, [n]]); starts = np.concatenate([[0], idx + 1])
    c = (ends - starts).astype(np.int64)
    return int((c * (c - 1) // 2).sum())
def dedupe(m):
    N = len(m[0]); k = np.zeros(N, np.uint64)
    for i, w in enumerate(m):
        k = k * np.uint64(0x9E3779B97F4A7C15) + w.astype(np.uint64) + np.uint64(i + 1)
        k ^= k >> np.uint64(29)
    _, ix = np.unique(k, return_index=True)
    return [w[ix] for w in m]
def run(name, m, res, rounds=3):
    m = dedupe(m); N = len(m[0])
    d = comp(m, rounds)
    P = projections(d); out = {}
    for p in PROJ:
        n = NB[p]; e = N * (N - 1) / 2 / 2**n
        o = coll(P[p]); out[p] = (o, e, (o - e) / math.sqrt(e))
    res.append((name, N, out))
    zs = [v[2] for v in out.values()]
    print(f"{name:36s} N={N:8d} " + " ".join(f"{v[0]/v[1]:.3f}" for v in out.values()) + f" maxz={max(zs, key=abs):+.2f}", flush=True)

def fam_words(ws, N, mask=0xFFFFFFFF):
    m = base(N)
    for i in ws: m[i] = rw(N) & U(mask)
    return m
def fam_hw(N, w):
    """exactly w distinct bit positions set among the 256 bits of m8..m15 (uniform over C(256,w) up to sampling)"""
    m = base(N)
    pos = np.argsort(rng.random((N, 256)), axis=1)[:, :w]
    W = np.zeros((N, 8), np.uint64)
    for j in range(w):
        p = pos[:, j]
        W[np.arange(N), p // 32] |= np.uint64(1) << (p % 32).astype(np.uint64)
    for k in range(8): m[8 + k] = W[:, k].astype(U)
    return m

def main():
    grp = sys.argv[1]; N = 1 << 20; res = []
    t = time.time()
    if grp == 'k1':
        for i in range(16): run(f"k1 word{i}", fam_words([i], N), res)
    elif grp == 'k2':
        for a, b in itertools.combinations(range(16), 2): run(f"k2 w{a},{b}", fam_words([a, b], 1 << 19), res)
    elif grp == 'k3':
        sel = list(itertools.combinations(range(16), 3)); idx = rng.choice(len(sel), 90, replace=False)
        for i in idx: run(f"k3 w{sel[i]}", fam_words(sel[i], 1 << 19), res)
    elif grp == 'k4':
        sel = list(itertools.combinations(range(16), 4)); idx = rng.choice(len(sel), 90, replace=False)
        for i in idx: run(f"k4 w{sel[i]}", fam_words(sel[i], 1 << 19), res)
        run("k4 w8-11", fam_words([8, 9, 10, 11], 1 << 19), res)
        run("k4 w12-15", fam_words([12, 13, 14, 15], 1 << 19), res)
        run("k4 w0-3", fam_words([0, 1, 2, 3], 1 << 19), res)
        run("k8 w8-15 (filed)", fam_words(range(8, 16), N), res)
        run("k16 all", fam_words(range(16), N), res)
    elif grp == 'hw':
        for w in (1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 64, 100):
            run(f"HW{w} in m8..15", fam_hw(1 << 19, w), res)
    elif grp == 'sym':
        for r in (0, 1, 4, 8, 13, 16, 31):
            m = base(N)
            for i in range(4):
                m[8 + i] = rw(N); m[12 + i] = rotr(m[8 + i], r)
            run(f"m12+i=rot(m8+i,{r})", m, res)
        for r in (1, 8, 16):
            m = base(N)
            for i in range(4):
                m[8 + i] = rw(N); m[12 + i] = ~rotr(m[8 + i], r)
            run(f"m12+i=~rot(m8+i,{r})", m, res)
        for r in (1, 8, 16):
            m = base(N); m[8] = rw(N); m[9] = rw(N)
            for i in range(2, 8): m[8 + i] = rotr(m[8 + i - 2], r)
            run(f"chain m(i)=rot(m(i-2),{r})", m, res)
        m = base(N); x = rw(N)
        for i in range(8, 16): m[i] = x.copy()
        run("all 8 words equal", m, res)
        m = base(N)
        for i in range(4): m[8 + i] = rw(N); m[12 + i] = m[8 + i]
        run("m12+i=m8+i", m, res)
        m = base(N)
        for i in range(4): m[8 + i] = rw(N); m[12 + i] = ~m[8 + i]
        run("m12+i=~m8+i", m, res)
        m = base(N)
        for i in range(0, 8, 2): m[8 + i] = rw(N); m[9 + i] = m[8 + i]
        run("m9=m8,m11=m10,..", m, res)
        m = base(N)
        for i in range(0, 8, 2): m[8 + i] = rw(N); m[9 + i] = ~m[8 + i]
        run("m9=~m8,m11=~m10,..", m, res)
        m = base(N); a = rw(N); b = rw(N)
        for i in range(8): m[8 + i] = a if i % 2 == 0 else b
        run("alternating a,b", m, res)
        for dd in ('rand', 'pow'):
            a = rw(N); b = rw(N) if dd == 'rand' else (U(1) << rng.integers(0, 32, N).astype(U))
            m = base(N)
            for i in range(8): m[8 + i] = a + U(i) * b
            run(f"AP m8+i=a+i*d d={dd}", m, res)
        a = rw(N); b = rw(N); m = base(N)
        for i in range(8): m[8 + i] = a ^ (U(i) * b)
        run("xor-AP a^(i*d)", m, res)
        a = rw(N); b = rw(N); m = base(N)
        for i in range(16): m[i] = a + U(i) * b
        run("AP all 16 words", m, res)
        m = base(N)
        for i in range(8, 16): m[i] = rng.integers(0, 256, N).astype(U) * U(0x01010101)
        run("each word byte-replicated", m, res)
    elif grp == 'mask':
        masks = {'low16': 0xFFFF, 'high16': 0xFFFF0000, 'even': 0x55555555, 'odd': 0xAAAAAAAA, 'bytes02': 0x00FF00FF,
                 'low8': 0xFF, 'high8': 0xFF000000, 'low24': 0xFFFFFF, 'low20': 0xFFFFF, 'low4': 0xF,
                 'bit31+low15': 0x80007FFF, 'low1': 1, 'nib0': 0x0F0F0F0F, 'top+low nib': 0xF000000F}
        for k, v in masks.items(): run(f"m8..15 &{k}", fam_words(range(8, 16), N, v), res)
        for k in ('low16', 'even', 'low8', 'low4', 'low1'): run(f"m0..7 &{k}", fam_words(range(8), N, masks[k]), res)
        for k in ('low16', 'low8'): run(f"m0..15 &{k}", fam_words(range(16), N, masks[k]), res)
        for s in (4, 8, 16, 24): run(f"m8..15 low{s} bits zero", fam_words(range(8, 16), N, (0xFFFFFFFF << s) & 0xFFFFFFFF), res)
        m = base(N)
        for i in range(8, 16): m[i] = (U(1) << rng.integers(0, 32, N).astype(U)) * rng.integers(0, 2, N).astype(U)
        run("each word 0 or one-hot", m, res)
        m = base(N)
        for i in range(8, 16): m[i] = (U(1) << rng.integers(0, 32, N).astype(U)) | (U(1) << rng.integers(0, 32, N).astype(U))
        run("each word HW<=2", m, res)
        m = base(N)
        for i in range(8, 16): m[i] = U(1) << rng.integers(0, 32, N).astype(U)
        run("each word one-hot", m, res)
    print("elapsed", time.time() - t)
    json.dump(res, open(f"res_{grp}_{SEED}.json", "w"))
main()
