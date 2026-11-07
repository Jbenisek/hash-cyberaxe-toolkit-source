"""s3-2block-capacity / experiment_D.py
Reliable, capacity-dependent replica of linstruct3's obstruction metric, at every round depth.

For round depth k, two source directions a,b are "k-round-compatible on a coset" iff the cube-sum (2nd finite
difference) of F_k over {a,b} is zero. A k-round-affine FIELD requires all its pairs compatible (necessary;
for k>=3 F_k has degree>2 on the full source, so we require compatibility at SEVERAL random cosets t -> a
direction pair that is affine on all tested cosets). We build the compatibility graph over the 320 source
coordinate directions and report: #compatible pairs, #triangles (trace(A^3)/6, exact), greedy max clique.
linstruct3's whole result was "max clique 2 / 0 triangles" at capacity 0. If a bought capacity raises the
triangle/clique count at k=3, a 3-round field of dim>=3 opens.

Everything uses the organizer round function cd.rnd (validated vs keccak.py permutation on nonzero capacity).
Usage: python experiment_D.py KDEPTHS(e.g. 2,3,4) NBASES NRANDCAPS
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

import sys, json, time, random, importlib.util
import numpy as np
CD = _hca_public_path_text('__HCA_WORKSPACE__/research/sha3r6/lowdegree/cube_degree.py')
spec = importlib.util.spec_from_file_location('cd', CD); cd = importlib.util.module_from_spec(spec); spec.loader.exec_module(cd)
U = np.uint64; MASK = (1 << 64) - 1
NB = 320

def cap_base(mode):
    C = [0] * 25
    if mode == 'zero':
        return C
    rng = random.Random(10000 + int(mode[3:]))
    for i in range(17, 25):
        C[i] = rng.getrandbits(64)
    return C

def Fk_states(srcs, C, k):
    n = len(srcs)
    uk = [np.fromiter(((s >> (64 * j)) & MASK for s in srcs), dtype=U, count=n) for j in range(5)]
    A = [np.full(n, U(C[i] & MASK)) for i in range(25)]
    for j in range(5):
        A[j] = A[j] ^ uk[j]; A[10 + j] = A[10 + j] ^ uk[j]
    A[16] = A[16] ^ U(0x86 << 56)
    for i in range(k):
        A = cd.rnd(A, i)
    return np.stack([np.asarray(a) for a in A])          # (25, n)

def compat_graph(C, k, bases):
    """A[i,j] = 1 iff cube-sum F_k over {e_i,e_j} == 0 at ALL given bases. Returns boolean adjacency (NB,NB)."""
    coords = [1 << i for i in range(NB)]
    pairs = [(i, j) for i in range(NB) for j in range(i + 1, NB)]
    adj = np.ones((NB, NB), bool); np.fill_diagonal(adj, False)
    for t in bases:
        srcs = [t] + [t ^ coords[i] for i in range(NB)] + [t ^ coords[i] ^ coords[j] for (i, j) in pairs]
        St = Fk_states(srcs, C, k)                        # (25, Npts)
        Ft = St[:, 0]
        Fi = St[:, 1:1 + NB]                              # (25, NB)
        Fij = St[:, 1 + NB:]                              # (25, Npairs)
        # cube = Ft ^ Fi ^ Fj ^ Fij ; compatible iff all 25 lanes zero
        base_col = Ft[:, None]
        for idx, (i, j) in enumerate(pairs):
            c = base_col[:, 0] ^ Fi[:, i] ^ Fi[:, j] ^ Fij[:, idx]
            if np.any(c):
                adj[i, j] = adj[j, i] = False
    return adj

def greedy_clique(adj):
    NBn = adj.shape[0]
    order = sorted(range(NBn), key=lambda v: -int(adj[v].sum()))
    clique = []
    for v in order:
        if all(adj[v, u] for u in clique):
            clique.append(v)
    return len(clique)

def analyze(adj):
    pairs = int(adj.sum() // 2)
    Ai = adj.astype(np.int64)
    tri = int(np.trace(Ai @ Ai @ Ai) // 6)
    return pairs, tri, greedy_clique(adj)

if __name__ == '__main__':
    kdepths = [int(x) for x in sys.argv[1].split(',')]
    nbases = int(sys.argv[2]); nrand = int(sys.argv[3])
    rng = random.Random(2024)
    bases = [rng.getrandbits(320) for _ in range(nbases)]
    caps = ['zero'] + ['cap%d' % s for s in range(1, nrand + 1)]
    print(json.dumps({'nbases': nbases, 'caps': caps}), flush=True)
    for k in kdepths:
        for cm in caps:
            t0 = time.time(); C = cap_base(cm)
            adj = compat_graph(C, k, bases)
            pairs, tri, clq = analyze(adj)
            print(json.dumps({'k': k, 'cap': cm, 'compatible_pairs': pairs, 'triangles': tri,
                              'greedy_max_clique': clq, 'sec': round(time.time() - t0, 1)}), flush=True)
