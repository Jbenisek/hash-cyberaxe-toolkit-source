"""s3-2block-capacity / experiment_F.py  -- characterize the capacity lever with numbers.
(1) How badly a random capacity breaks the certified W40 2-round field (# of its 780 pairs that stop being
    2-round-affine), and whether that breakage is LINEAR in the capacity bits (sets the 2^c cost model).
(2) Max 3-round-affine subspace inside W40 at cap 0 and random capacities (pairwise B3 over W40, bilinear).
(3) Max 3-round-affine subspace inside a coordinate 2-round field (k=2 clique) at each capacity.
Usage: python experiment_F.py
"""

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

import json, random, importlib.util
import numpy as np
EC = importlib.util.spec_from_file_location('ec', _hca_public_path_text('__HCA_WORKSPACE__/research/newpaths/untried/s3-2block-capacity/experiment_C2.py'))
ec = importlib.util.module_from_spec(EC); EC.loader.exec_module(ec)
cd = ec.cd
U = np.uint64; MASK = (1 << 64) - 1

def capC(seed, lanes=range(17, 25)):
    C = [0] * 25; rng = random.Random(10000 + seed)
    for i in lanes: C[i] = rng.getrandbits(64)
    return C

def w40_broken_pairs(C, t):
    W = cd.W; m, M = ec.build_form(W, C, 2, t)
    return sum(1 for i in range(m) for j in range(i + 1, m) if M[i][j]) , m * (m - 1) // 2

def pair_iso_dim(dirs, C, k, t):
    """max 3-round-affine subspace via pairwise B_k (bilinear once inside a (k-1)-affine field)."""
    m, M = ec.build_form(dirs, C, k, t)
    iso = ec.max_isotropic(M, m, 40, 7)
    return ec.dim_of(iso), m

if __name__ == '__main__':
    rng = random.Random(99); t = rng.getrandbits(320)

    # (1) W40 breakage vs capacity + linearity test
    print('--- (1) W40 2-round field vs capacity ---')
    b0, tot = w40_broken_pairs([0] * 25, t)
    print(json.dumps({'cap': 'zero', 'w40_broken_pairs': b0, 'of': tot}))
    for s in range(1, 5):
        b, _ = w40_broken_pairs(capC(s), t)
        print(json.dumps({'cap': 'cap%d' % s, 'w40_broken_pairs': b, 'of': tot}))
    # linearity in capacity: is B2 over W40 pairs additive in C?  B2(C1^C2) ?= B2(C1)^B2(C2)^B2(0)
    C1 = capC(1); C2 = capC(2); C12 = [C1[i] ^ C2[i] for i in range(25)]
    _, M0 = ec.build_form(cd.W, [0] * 25, 2, t)
    _, Ma = ec.build_form(cd.W, C1, 2, t)
    _, Mb = ec.build_form(cd.W, C2, 2, t)
    _, Mab = ec.build_form(cd.W, C12, 2, t)
    m = len(cd.W)
    lin_ok = all((Mab[i][j] ^ Ma[i][j] ^ Mb[i][j] ^ M0[i][j]) == 0 for i in range(m) for j in range(i + 1, m))
    print(json.dumps({'B2_linear_in_capacity': bool(lin_ok)}))

    # (2) 3-round subspace inside W40 at each capacity
    print('--- (2) 3-round-affine subspace inside W40 ---')
    for cm, C in [('zero', [0] * 25)] + [('cap%d' % s, capC(s)) for s in range(1, 5)]:
        d3, m = pair_iso_dim(cd.W, C, 3, t)
        print(json.dumps({'cap': cm, 'round3_dim_inside_W40': d3, 'W40_dim': ec.dim_of(cd.W)}))

    # (3) 3-round subspace inside a coordinate 2-round field (k=2 clique) at each capacity
    print('--- (3) 3-round-affine subspace inside a coordinate 2-round field ---')
    import importlib.util as il
    ED = il.spec_from_file_location('ed', _hca_public_path_text('__HCA_WORKSPACE__/research/newpaths/untried/s3-2block-capacity/experiment_D.py'))
    ed = il.module_from_spec(ED); ED.loader.exec_module(ed)
    for cm, C in [('zero', [0] * 25)] + [('cap%d' % s, capC(s)) for s in range(1, 5)]:
        adj = ed.compat_graph(C, 2, [t, rng.getrandbits(320)])
        # greedy clique -> coordinate 2-round field
        order = sorted(range(ed.NB), key=lambda v: -int(adj[v].sum())); clq = []
        for v in order:
            if all(adj[v, u] for u in clq): clq.append(v)
        Vc = [1 << i for i in clq]
        d3, m = pair_iso_dim(Vc, C, 3, t) if len(Vc) >= 2 else (1, len(Vc))
        print(json.dumps({'cap': cm, 'coord_2round_clique_dim': len(clq), 'round3_dim_inside': d3}))
