#!/usr/bin/env python3
# Independent recheck (2026-10-09): distinct (P, D) over all 2^19 class members in 5 fresh contexts,
# and the additive-X1 claim on 10,000 fresh cases. Pure computation; writes nothing.
# P, D come from movers.consts() (black box) applied to outer.scalar_outer of each member,
# and separately from a numpy re-derivation; the two must agree member by member.

# Publication path adapter: resolve data paths from the extracted source tree.
def _hca_public_path_text(value):
    if "__HCA_WORKSPACE__/" not in value:
        return value
    import os as _hca_os
    from pathlib import Path as _hca_Path
    root = _hca_os.environ.get("HASHCYBERAXE_WORKSPACE")
    if root is None:
        here = _hca_Path(__file__).resolve().parent
        root = next((str(p) for p in (here, *here.parents) if (p / "research").is_dir()), None)
    if root is None:
        raise FileNotFoundError("Extract the research source tree, or set HASHCYBERAXE_WORKSPACE to its archive directory.")
    return value.replace("__HCA_WORKSPACE__/", str(_hca_Path(root).resolve()).replace("\\", "/") + "/")

import os, sys, random, time
from multiprocessing import Pool
import numpy as np
R = _hca_public_path_text('__HCA_WORKSPACE__/research')
sys.path.insert(0, os.path.join(R, "fifties", "movers")); sys.path.insert(0, os.path.join(R, "impl"))
import movers, outer
M32 = 0xFFFFFFFF
FREE = [i for i in range(32) if outer.FREE_MASK >> i & 1]
assert len(FREE) == 19

def W_of(m):
    w = 0
    for n, i in enumerate(FREE):
        w |= ((m >> n) & 1) << i
    return w

def blackbox(ctx):
    'All 2^19 members through scalar_outer + consts; returns P, D arrays (uint32), K-check failures.'
    P = np.empty(1 << 19, np.uint32); D = np.empty(1 << 19, np.uint32); kbad = 0
    for m in range(1 << 19):
        o = outer.scalar_outer(list(ctx) + [W_of(m)])
        c = movers.consts(o); P[m] = c["P"]; D[m] = c["D"]
        if m % 64 == 0:
            kbad += movers.K(o["D2.a1"], c) != (o["Y1"] + o["w12"]) & M32
    return P, D, kbad

def u(x): return np.uint32(x & M32)
def rot_r(v, n): return (v >> np.uint32(n)) | (v << np.uint32(32 - n))

def numpy_PD(ctx):
    'Own derivation: Y4 -> Y8 -> Y12 -> Y0 -> C0.a1 = P; X12 -> D1.c1 -> D1.d1 = D.'
    o0 = outer.scalar_outer(list(ctx) + [0])
    C0d1, S11, w6 = ctx[0], ctx[3], ctx[6]
    C0b1, C0c1 = o0["C0.b1"], o0["C0.c1"]
    ms = np.arange(1 << 19, dtype=np.uint64); W = np.zeros(1 << 19, np.uint64)
    for n, i in enumerate(FREE):
        W |= ((ms >> np.uint64(n)) & np.uint64(1)) << np.uint64(i)
    e1 = (W | np.uint64(outer.CLASS_VALUE)).astype(np.uint32)
    y = e1 - u(outer.Y3)
    Y8 = rot_r(y, 25) ^ u(C0b1)
    Y12 = Y8 - u(C0c1)
    Y0 = rot_r(Y12, 24) ^ u(C0d1)
    P = Y0 - u(C0b1) - u(w6)
    X12 = rot_r(u(C0d1), 16) ^ P
    D = u(outer.X11) - X12 - u(S11)
    return P, D

def job(ctx):
    t = time.time(); P, D, kbad = blackbox(ctx); Pn, Dn = numpy_PD(ctx)
    mism = int(np.count_nonzero((P != Pn) | (D != Dn)))
    pd = (P.astype(np.uint64) << np.uint64(32)) | D.astype(np.uint64)
    return dict(ctx=[hex(x) for x in ctx], P=len(np.unique(P)), D=len(np.unique(D)), PD=len(np.unique(pd)),
                mism=mism, kbad=kbad, sec=round(time.time() - t, 1))

def additive(n, seed):
    rnd = random.Random(seed); changed = equal = 0
    for i in range(n):
        if i % 2 == 0:
            c = {k: rnd.getrandbits(32) for k in movers.NAMES}
        else:   # constants from a real outer step
            ctx = [rnd.getrandbits(32) for _ in range(7)]
            c = movers.consts(outer.scalar_outer(ctx + [rnd.getrandbits(32)]))
        x1 = rnd.getrandbits(32) or 1
        c0 = dict(c, X1=0); c1 = dict(c, X1=x1)
        g1, g2 = rnd.getrandbits(32), rnd.getrandbits(32)
        d1 = (movers.K(g1, c1) - movers.K(g1, c0)) & M32
        d2 = (movers.K(g2, c1) - movers.K(g2, c0)) & M32
        changed += d1 != d2; equal += (d1 == x1 and d2 == x1)
    return changed, equal

if __name__ == "__main__":
    rnd = random.Random(0x50C0FFEE)
    ctxs = [tuple(rnd.getrandbits(32) for _ in range(7)) for _ in range(5)]
    with Pool(6) as pool:
        ar = pool.apply_async(additive, (10000, 0x5EED50))
        for r in pool.map(job, ctxs):
            print(r)
        ch, eq = ar.get()
    print(f"additive X1: diff changed with g in {ch}/10000, equalled X1 (both g) in {eq}/10000")
