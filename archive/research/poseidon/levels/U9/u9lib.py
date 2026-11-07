"""U9 shared library. Exact arithmetic with python-flint. Reads constants/MDS as data via poseidon_ref (validated 11/11)."""

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

import sys, time, random
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/orchard/impl'))
import poseidon_ref as R
from flint import fmpz_mod_ctx, fmpz_mod_poly_ctx, nmod_poly
P = R.P; RC = R.RC; M = [list(r) for r in R.MDS]; CAP = R.CAPACITY
T0 = time.time()
def log(*a): print(*a, flush=True)
def schedule(r): return R.schedule(r)
def kind(idx): return 'full' if (idx < 4 or idx >= 60) else 'partial'

class Ring:
    """univariate polynomial ring over F_mod (flint)"""
    def __init__(self, mod):
        self.mod = mod
        if mod > 2**62:
            self.PR = fmpz_mod_poly_ctx(fmpz_mod_ctx(mod)); self.mk = lambda l: self.PR(l)
        else:
            self.mk = lambda l: nmod_poly(l, mod)
    def const(self, c): return self.mk([c % self.mod])
    def x(self): return self.mk([0, 1])
    def xpow(self, n): return self.mk([0]*n + [1])
    BLOCK = 1 << 20
    LIMIT = 3_000_000
    def mul(self, f, g):
        # flint 0.9.0 fmpz_mod_poly segfaults for 255-bit products of length above about 4-8 million; split into blocks
        if self.mod < 2**62 or f.length() + g.length() <= self.LIMIT: return f*g
        B = self.BLOCK
        nf = (f.length() + B - 1)//B; ng = (g.length() + B - 1)//B
        fb = [f.right_shift(i*B).truncate(B) for i in range(nf)]
        gb = [g.right_shift(j*B).truncate(B) for j in range(ng)]
        acc = None
        for i in range(nf):
            for j in range(ng):
                t = (fb[i]*gb[j]).left_shift((i+j)*B)
                acc = t if acc is None else acc + t
        return acc
    def pow5(self, f):
        f2 = self.mul(f, f); f4 = self.mul(f2, f2); return self.mul(f4, f)
    def lin(self, row, lanes):
        acc = lanes[0]*row[0]
        for j in range(1, len(lanes)): acc = acc + lanes[j]*row[j]
        return acc
    def nz_index(self, f):
        cs = f.coeffs()
        return [k for k, c in enumerate(cs) if c != 0], len(cs)

def apply_round(ring, lanes, idx, Mx, RCx, knd=None):
    knd = knd or kind(idx)
    lanes = [lanes[i] + RCx[idx][i] % ring.mod for i in range(3)]
    lanes = [ring.pow5(l) if (knd == 'full' or i == 0) else l for i, l in enumerate(lanes)]
    return [ring.lin(Mx[i], lanes) for i in range(3)]

def stats2(idxs, W):
    """bivariate support from Kronecker indices"""
    import numpy as np
    a = np.array(idxs, dtype=np.int64)
    if a.size == 0: return dict(n=0)
    i = a % W; j = a // W
    d = int((i+j).max())
    return dict(n=int(a.size), deg=d, degx=int(i.max()), degy=int(j.max()), tri=(d+1)*(d+2)//2, full=(a.size == (d+1)*(d+2)//2), i=i, j=j)
