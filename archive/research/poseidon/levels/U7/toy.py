import numpy as np, random
from math import gcd
def inv_mod(x, q): return pow(int(x), -1, q)
def make_toy(q, seed, r):
    """toy copy: width 3, x^5, rounds 0-3 full, r partial, 4 full; random constants; random Cauchy MDS (all minors nonzero)."""
    rnd = random.Random(seed)
    assert gcd(5, q-1) == 1
    while True:
        xs = [rnd.randrange(q) for _ in range(3)]; ys = [rnd.randrange(q) for _ in range(3)]
        if len(set(xs)) == 3 and len(set(ys)) == 3 and all((x+y) % q for x in xs for y in ys): break
    M = [[inv_mod(x+y, q) for y in ys] for x in xs]
    nr = 8+r
    RCt = [[rnd.randrange(q) for _ in range(3)] for _ in range(nr)]
    full = [True]*4+[False]*r+[True]*4
    return dict(q=q, M=M, RC=RCt, full=full, cap=pow(2, 65, q), r=r, seed=seed)
def toy_trace(T, nk, rho, record=None):
    """vectorised over numpy arrays nk, rho; returns final 3 lanes; if record is a list, appends (round,stage,state) after each step and S-box inputs."""
    q = T['q']; M = np.array(T['M'], dtype=np.int64)
    s = [np.asarray(nk, dtype=np.int64) % q, np.asarray(rho, dtype=np.int64) % q, np.full(np.shape(nk), T['cap'], dtype=np.int64)]
    for ri, (rc, f) in enumerate(zip(T['RC'], T['full'])):
        s = [(s[i]+rc[i]) % q for i in range(3)]
        if record is not None: record.append(('sin', ri, [x.copy() for x in s]))
        lanes = range(3) if f else [0]
        for i in lanes:
            x = s[i]; x2 = x*x % q; x4 = x2*x2 % q; s[i] = x4*x % q
        s = [(M[i, 0]*s[0]+M[i, 1]*s[1]+M[i, 2]*s[2]) % q for i in range(3)]
        if record is not None: record.append(('out', ri, [x.copy() for x in s]))
    return s
def sqrt_m1(q):
    for x in range(2, q):
        if x*x % q == q-1: return x
    return None
