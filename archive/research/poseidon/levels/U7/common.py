
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

import sys, random
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/orchard/impl'))
import poseidon_ref as PR
import gmpy2
from gmpy2 import mpz
P = PR.P
RC = PR.RC; MDS = PR.MDS
def inv(x, q=P): return int(gmpy2.invert(x, q))
def leg(x, q=P):
    x %= q
    if x == 0: return 0
    return 1 if pow(x, (q-1)//2, q) == 1 else -1
def sqrt_mod(a, q=P):
    """Tonelli-Shanks; returns a root or None"""
    a %= q
    if a == 0: return 0
    if leg(a, q) != 1: return None
    s = 0; Q = q-1
    while Q % 2 == 0: Q //= 2; s += 1
    z = 2
    while leg(z, q) != -1: z += 1
    M = s; c = pow(z, Q, q); t = pow(a, Q, q); R = pow(a, (Q+1)//2, q)
    while t != 1:
        i = 0; tt = t
        while tt != 1: tt = tt*tt % q; i += 1
        b = pow(c, 1 << (M-i-1), q)
        M = i; c = b*b % q; t = t*c % q; R = R*b % q
    return R
I_ = sqrt_mod(P-1)           # a fixed sqrt(-1)
def matvec(M, v, q=P): return [sum(M[i][j]*v[j] for j in range(3)) % q for i in range(3)]
