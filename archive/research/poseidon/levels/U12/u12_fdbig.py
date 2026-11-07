# Exact output-degree confirmation by finite differences (lane 0 of the final state), one process.
# usage: python u12_fdbig.py <r> <coords: AB|nkrho>

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

import sys, random, time
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/orchard/impl'))
import poseidon_ref as R
P, RC, CAP = R.P, R.RC, R.CAPACITY
D5 = pow(5, -1, P - 1)
r = int(sys.argv[1]); coords = sys.argv[2]
random.seed(1000 + r)
deg = 5 ** (7 + r) if coords == 'AB' else 5 ** (8 + r)
sch = R.schedule(r)
a0, b0, al, be = [random.randrange(P) for _ in range(4)]
t0 = time.time()
vals = []
for t in range(deg + 2):
    if coords == 'AB':
        A = (a0 + al * t) % P; B = (b0 + be * t) % P
        nk = (pow(A, D5, P) - RC[0][0]) % P; rho = (pow(B, D5, P) - RC[0][1]) % P
    else:
        nk = (a0 + al * t) % P; rho = (b0 + be * t) % P
    vals.append(R.perm([nk, rho, CAP], r)[0] if False else R.hash_reduced(nk, rho, r))
print('evaluated', len(vals), 'points in %.0fs' % (time.time() - t0), flush=True)


def fd(k):
    res = 0; c = 1
    for i in range(k + 1):
        res += (-c if (k - i) & 1 else c) * vals[i]
        c = c * (k - i) % P * pow(i + 1, -1, P) % P
    return res % P


hi = fd(deg + 1); lo = fd(deg)
print('r=%d coords=%s predicted degree %d: Delta^(d+1) == 0: %s ; Delta^d != 0: %s ; total %.0fs' % (r, coords, deg, hi == 0, lo != 0, time.time() - t0), flush=True)
