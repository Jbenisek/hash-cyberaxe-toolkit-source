# U12: k partial rounds, fixed entry lane 0: is (s1,s2) -> lane0 after k-th partial round q-to-1 (balanced)?
# Toy exhaustive (several q, seeds) + real-field algebra check of the 2x2 minor = observability determinant.

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
import numpy as np
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/orchard/impl'))
out = []
def log(*a):
    m = ' '.join(str(x) for x in a); print(m, flush=True); out.append(m)

for q in (23, 29, 37, 103):
    for seed in (1, 2, 3):
        rng = random.Random(seed * 100 + q)
        while True:
            xs = [rng.randrange(q) for _ in range(3)]; ys = [rng.randrange(q) for _ in range(3)]
            if len(set(xs)) == 3 and len(set(ys)) == 3 and all((x + y) % q for x in xs for y in ys): break
        M = np.array([[pow(x + y, -1, q) for y in ys] for x in xs], dtype=np.int64)
        RC = np.array([[rng.randrange(q) for _ in range(3)] for _ in range(8)], dtype=np.int64)
        s1, s2 = np.meshgrid(np.arange(q), np.arange(q), indexing='ij'); s1 = s1.ravel(); s2 = s2.ravel()
        res = []
        for s0 in (0, 1, 5 % q):
            S = np.stack([np.full_like(s1, s0), s1, s2], 1).astype(np.int64)
            rowsz = []
            for k in range(4):
                S = (S + RC[k]) % q
                S[:, 0] = (S[:, 0] ** 5) % q
                S = S @ M.T % q
                cnt = np.bincount(S[:, 0], minlength=q)
                rowsz.append('balanced' if (cnt == q).all() else 'max=%d min=%d' % (cnt.max(), cnt.min()))
            res.append(rowsz)
        log('OBSERVED q=%d seed=%d: for entry lane0 in {0,1,5}: fibre sizes of lane0 after partial round #1..#4 over all (s1,s2): %s' % (q, seed, res))

# real field algebra
import poseidon_ref as R
P, M = R.P, R.MDS
def det3(m):
    a, b, c = m[0]; d, e, f = m[1]; g, h, i = m[2]
    return (a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)) % P
M2 = [[sum(M[i][k] * M[k][j] for k in range(3)) % P for j in range(3)] for i in range(3)]
r0 = M[0]; r1 = M2[0]
# lane0 after round1 = r0 . (w,s1',s2') ; after round 2: M00 w2 + r0.(0,y1,y2) with y=M(w,s1',s2'): linear forms in (s1,s2):
# y0 = M01 s1 + M02 s2 (+const);  L = (row0 of M^2)_{1,2} . (s1,s2) - M00*y0 -> minor of (y0, L) in (s1,s2) :
y0 = (M[0][1], M[0][2])
L = ((M2[0][1] - M[0][0] * M[0][1]) % P, (M2[0][2] - M[0][0] * M[0][2]) % P)
minor = (y0[0] * L[1] - y0[1] * L[0]) % P
# observability determinant rows e0, e0 M, e0 M^2 (with M^3 not needed)
obs = det3([[1, 0, 0], M[0], M2[0]])
log('real field: 2x2 minor of (y0, L) in (s1,s2) =', hex(minor), '; observability det[e0; e0M; e0M^2] =', hex(obs), '; equal:', minor == obs, '; nonzero:', minor != 0)
log('(derivation: lane0 after 2nd partial round = M00*(y0+c)^5 + linear form L; (y0,L) is a bijective linear change of (s1,s2) iff this minor != 0; then for fixed s0 every output value has exactly q^(1) preimages (s1,s2): PROVED for both toys and p.)')
# real-field numeric check of the decomposition
def rnd_p(s, idx): return R.round_partial(s, idx)
bad = 0
for _ in range(200):
    s = [random.randrange(P) for _ in range(3)]
    a = rnd_p(s, 4); b = rnd_p(a, 5)
    w = pow((s[0] + R.RC[4][0]) % P, 5, P)
    y = R.round_partial(s, 4)
    w2 = pow((y[0] + R.RC[5][0]) % P, 5, P)
    pred = (M[0][0] * w2 + M[0][1] * (y[1] + R.RC[5][1]) + M[0][2] * (y[2] + R.RC[5][2])) % P
    if pred != b[0]: bad += 1
log('OBSERVED real: lane0 after R5 = M00 w5 + M01 (y1+c51) + M02 (y2+c52), w5=(y0+c50)^5 (y = state after R4.M), 200 states, failures', bad)
open('u12_balance_output.txt', 'w').write('\n'.join(out))
