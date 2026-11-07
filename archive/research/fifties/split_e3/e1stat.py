'''E1 key variation with E3 held: E1 inputs (Y12, K, w5, c1) of the GPU roots (every root rebuilt and verified on
compress2 by check.py), against uniform E1 inputs.  Side-1 outcome (beta, t, s) = (db1, da2, dc2) of E1 = G(Y1,Y6,Y11,Y12,
w12,w5) for the two blocks (Y11 -> Y11', w5 -> w5 + DELTA5).  usage: python e1stat.py <seed>'''

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

import sys, json, math, random, collections
sys.dont_write_bytecode = True
import numpy as np
from ev import hs, M
Y11, Y11B, D5 = hs.Y11, hs.Y11B, hs.DELTA5
def rol(x, n): return ((x << np.uint32(n)) | (x >> np.uint32(32 - n))) & np.uint32(M)
def ror(x, n): return rol(x, 32 - n)
def side1(Y12, K, w5, c1):
    u = lambda a: np.asarray(a, dtype=np.uint32)
    Y12, K, w5, c1 = u(Y12), u(K), u(w5), u(c1)
    d1 = c1 - np.uint32(Y11); a1 = rol(d1, 16) ^ Y12; y6 = a1 - K
    out = []
    for y11, dw in ((Y11, 0), (Y11B, D5)):
        cc = d1 + np.uint32(y11); b1 = ror(y6 ^ cc, 12); a2 = a1 + b1 + w5 + np.uint32(dw)
        d2 = ror(d1 ^ a2, 8); c2 = cc + d2
        out.append((b1, a2, c2))
    return out[0][0] ^ out[1][0], out[0][1] ^ out[1][1], out[0][2] ^ out[1][2]
P = _hca_public_path_text('__HCA_WORKSPACE__/opus_cloud\\Smash-claude-math-help-g3v211\\results\\pairs_453_weights.txt')
pairs = [(int(l.split()[0], 16), int(l.split()[1], 16)) for l in open(P)]
H = 0x830303CF
def beta_of(s): return s ^ (((s ^ H) >> 1) | ((s ^ H) << 31)) & M
BETAS = {beta_of(s) for _, s in pairs}
TSTAR, SSTAR = 0x189060a0, 0x6e203e55; BSTAR = beta_of(SSTAR)
seed = int(sys.argv[1])
rows = json.load(open('e1_%d.json' % seed))
E = np.array([r[1] for r in rows], dtype=np.uint64).astype(np.uint32)
n = len(E)
print('E3-held roots with verified E1 inputs:', n, ' distinct E1 tuples:', len({tuple(r[1]) for r in rows}),
      ' E3 tuples:', len({r[0] for r in rows}))
bits = np.zeros((4, 32))
for j in range(4):
    for i in range(32): bits[j, i] = ((E[:, j] >> np.uint32(i)) & np.uint32(1)).mean()
z = (bits - 0.5) / math.sqrt(0.25 / n)
print('E1 input bits (Y12, K, w5, c1): largest |z| over 128 bits %.2f, mean |z| %.2f, chi2/dof %.2f' %
      (abs(z).max(), abs(z).mean(), (z ** 2).mean()))
b, t, s = side1(E[:, 0], E[:, 1], E[:, 2], E[:, 3])
rng = np.random.default_rng(seed); N = 1 << 24
U = rng.integers(0, 1 << 32, size=(N, 4), dtype=np.uint64).astype(np.uint32)
bu, tu, su = side1(U[:, 0], U[:, 1], U[:, 2], U[:, 3])
def cmp(name, ev, evu):
    k, ku = int(ev.sum()), int(evu.sum()); p = ku / N; e = n * p; zz = (k - e) / math.sqrt(max(e, 1e-9))
    print('  %-44s held: %5d/%d   uniform rate 2^%.2f -> expected %.1f   z %.2f' % (name, k, n, math.log2(p) if p else -99, e, zz))
print('side-1 events, E3-held roots vs uniform E1 inputs (2^24 samples):')
cmp('beta = beta* (pair 189060a0/6e203e55)', b == BSTAR, bu == BSTAR)
cmp('beta in the 453-pair beta set', np.isin(b, list(BETAS)), np.isin(bu, list(BETAS)))
cmp('beta = beta* and t low 8 bits = t* low 8', (b == BSTAR) & ((t & 0xFF) == (TSTAR & 0xFF)), (bu == BSTAR) & ((tu & 0xFF) == (TSTAR & 0xFF)))
cmp('s low 8 bits = s* low 8 bits', (s & 0xFF) == (SSTAR & 0xFF), (su & 0xFF) == (SSTAR & 0xFF))
cmp('t low 12 bits = t* low 12 bits', (t & 0xFFF) == (TSTAR & 0xFFF), (tu & 0xFFF) == (TSTAR & 0xFFF))
print('beta* = %08x' % BSTAR)
