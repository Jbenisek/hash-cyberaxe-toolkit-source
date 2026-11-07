
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

import json, random
import os
ROOT = _hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/pareto_clone/pareto') if os.name=='nt' else _hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/pareto_clone/pareto')
p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
_d = json.load(open(os.path.join(ROOT,'orchard-pallas-constants.json')))
RC = [[int(x, 16) for x in row] for row in _d['round_constants']]
MDS = [[int(x, 16) for x in row] for row in _d['mds']]
CAP = 1 << 65
E5INV = pow(5, -1, p - 1)   # fifth root exponent (gcd(5,p-1)=1)

def mds(s):
    return [sum(MDS[i][j] * s[j] for j in range(3)) % p for i in range(3)]

def rnd(s, k, full):
    s = [(s[i] + RC[k][i]) % p for i in range(3)]
    if full: s = [pow(x, 5, p) for x in s]
    else: s[0] = pow(s[0], 5, p)
    return mds(s)

def schedule(r):
    return [(k, True) for k in range(4)] + [(4 + i, False) for i in range(r)] + [(k, True) for k in range(60, 64)]

def digest(nk, rho, r):
    s = [nk % p, rho % p, CAP]
    for k, f in schedule(r): s = rnd(s, k, f)
    return s[0]

def full_perm(s):
    sch = [(k, True) for k in range(4)] + [(k, False) for k in range(4, 60)] + [(k, True) for k in range(60, 64)]
    for k, f in sch: s = rnd(s, k, f)
    return s
