"""Analysis of the GPU cube-sum runs (runs/*.counts.txt, runs/*.vec.bin).
Per stage and cube dimension k: per-bit fraction of cubes with nonzero sum (a bit whose k-cube sums are all zero has degree < k).
Rank of the top-degree parts: GF(2) rank of the matrix of k-cube-sum vectors (rows = cubes, columns = bits of the stage);
columns - rank = number of independent bit COMBINATIONS whose degree is < k. Per-coset and t-dependence tests on the shared runs."""

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

import struct, json, sys
import numpy as np
HERE = _hca_public_path_text('__HCA_WORKSPACE__/research/newpaths/untried/s3-plane-degrees/')
R = HERE + 'runs/'
ST = ['S1', 'S2', 'B3', 'S3', 'B4', 'S4', 'B5', 'S5', 'B6', 'S6']
DEG = {'S1': 1, 'S2': 1, 'B3': 1, 'S3': 2, 'B4': 2, 'S4': 4, 'B5': 4, 'S5': 8, 'B6': 8, 'S6': 16}
# column sets (bit index = 64*lane + z)
SEL = {s: list(range(1600)) for s in ST}
SEL['B6row0'] = list(range(320))          # B[x,z], x = 0..4 (lanes 0..4), z = 0..63
SEL['S6dig'] = list(range(256))           # digest lanes 0..3
SEL['B6key'] = [64 * x + z for x in range(5) for z in range(35)]   # D19 key cone: 175 planes
SRC = {'B6row0': 'B6', 'S6dig': 'S6', 'B6key': 'B6'}
out = {}
log = open(HERE + 'out_analysis.txt', 'w')
def P(*a):
    s = ' '.join(str(x) for x in a); print(s); log.write(s + '\n'); log.flush()

def counts(name):
    L = open(R + name + '.counts.txt').read().split('\n')
    meta = L[0].split(); n = int(meta[1])
    C = {ST[i]: np.array([int(x) for x in L[1 + i].split()]) for i in range(10)}
    return n, C

def readvec(name, maxn=None):
    b = open(R + name + '.vec.bin', 'rb').read()
    magic, k, n, nst = struct.unpack('<4i', b[:16])
    if maxn: n = min(n, maxn)
    rec = 40 + 40 * k + 8 * k + 8 * 25 * nst
    arr = np.frombuffer(b, dtype=np.uint8, count=n * rec, offset=16).reshape(n, rec)
    sums = arr[:, 40 + 48 * k:].copy().view('<u8').reshape(n, nst, 25)
    return k, sums

def bits_of(sums, stage):  # -> (n, 1600) uint8 bit matrix, column 64*lane + z
    i = ST.index(stage)
    w = sums[:, i, :]                       # (n, 25) uint64
    by = w.view(np.uint8).reshape(len(w), 25 * 8)
    return np.unpackbits(by, axis=1, bitorder='little')

def gf2_rank_null(M):
    """rank and null-space dimension of 0/1 matrix M (rows x cols); returns (rank, null basis as list of int bitmasks over cols)."""
    rows, cols = M.shape
    piv = {}                                  # pivot col -> row int (reduced so pivot col is its top bit)
    packed = np.packbits(M[:, ::-1], axis=1, bitorder='big')   # col j -> bit j of the int
    for r in range(rows):
        x = int.from_bytes(packed[r].tobytes(), 'big') >> (packed.shape[1] * 8 - cols)
        while x:
            t = x.bit_length() - 1
            if t in piv: x ^= piv[t]
            else: piv[t] = x; break
    rank = len(piv)
    # RREF back-substitution to get the null space
    pcs = sorted(piv)
    for c in pcs:                              # make each pivot row clear of other pivot columns
        for c2 in pcs:
            if c2 > c and (piv[c2] >> c) & 1: piv[c2] ^= piv[c]
    free = [c for c in range(cols) if c not in piv]
    null = []
    for f in free:
        v = 1 << f
        for c in pcs:
            if (piv[c] >> f) & 1: v |= 1 << c
        null.append(v)
    return rank, null

# ---------- 1. per-bit degree tests (span directions, fresh coset per cube) ----------
P('== 1. per-bit cube-sum statistics (span directions, fresh random coset per cube) ==')
P('columns: stage, k, cubes, bits tested, bits with ALL k-cube sums zero (degree < k), min / median / max nonzero fraction')
runs = {k: 'span_k%d' % k for k in (1, 2, 3, 4, 5, 6, 7, 8, 9, 15, 16, 17)}
basis = {k: 'basis_k%d' % k for k in (2, 4, 7, 8, 16)}
tab = {}
for mode, rr in (('span', runs), ('basis', basis)):
    for k, name in rr.items():
        n, C = counts(name)
        for sel in ST + ['B6row0', 'S6dig', 'B6key']:
            src = SRC.get(sel, sel)
            c = C[src][SEL[sel]]
            f = c / n
            rec = dict(cubes=n, bits=len(c), zero_bits=int((c == 0).sum()), min=round(float(f.min()), 4),
                       med=round(float(np.median(f)), 4), max=round(float(f.max()), 4), min_count=int(c.min()))
            tab[(mode, sel, k)] = rec
for sel in ['S1', 'S2', 'B3', 'S3', 'B4', 'S4', 'B5', 'S5', 'B6', 'B6row0', 'B6key', 'S6', 'S6dig']:
    d = DEG[SRC.get(sel, sel)]
    for mode, rr in (('span', runs), ('basis', basis)):
        for k in sorted(rr):
            if k < max(1, d - 2) or k > d + 1: continue
            r = tab[(mode, sel, k)]
            P(f'{sel:7s} {mode:5s} k={k:2d} cubes={r["cubes"]:6d} bits={r["bits"]:4d} zero={r["zero_bits"]:4d} '
              f'frac min/med/max={r["min"]:.4f}/{r["med"]:.4f}/{r["max"]:.4f} (min count {r["min_count"]})')
out['per_bit'] = {f'{m}|{s}|{k}': v for (m, s, k), v in tab.items()}

# z positions whose 5 chi6-input planes all have degree < k
n8, C8 = counts('span_k8'); n7, C7 = counts('span_k7')
zq = {}
for k, C in ((8, C8), (7, C7)):
    zq[k] = [z for z in range(64) if all(C['B6'][64 * x + z] == 0 for x in range(5))]
    P(f'z with all 5 planes B[0..4,z] of degree <= {k-1} (k={k} sums all zero): {len(zq[k])} -> {zq[k]}')
out['z_qualify'] = {str(k): v for k, v in zq.items()}

# ---------- 2. rank of the top-degree parts ----------
P('\n== 2. GF(2) rank of the k-cube-sum matrix = dimension of the span of the degree-k parts; cols - rank = combinations of degree < k ==')
rk = {}
for sel, name, k, maxn in (('S1', 'span_k1', 1, 4000), ('S2', 'span_k1', 1, 4000), ('B3', 'span_k1', 1, 4000),
                           ('S3', 'span_k2', 2, 4000), ('B4', 'span_k2', 2, 4000),
                           ('S4', 'span_k4', 4, 4000), ('B5', 'span_k4', 4, 4000),
                           ('S5', 'span_k8', 8, 6000), ('B6', 'span_k8', 8, 6000), ('B6row0', 'span_k8', 8, 6000),
                           ('B6key', 'span_k8', 8, 6000),
                           ('S6dig', 'span_k16', 16, 2000), ('S6', 'span_k16', 16, 2000),
                           ('S5', 'span_k7', 7, 4000), ('B6row0', 'span_k7', 7, 4000)):
    kk, sums = readvec(name, maxn)
    M = bits_of(sums, SRC.get(sel, sel))[:, SEL[sel]]
    r, null = gf2_rank_null(M)
    rk[f'{sel}|k{k}'] = dict(rows=int(M.shape[0]), cols=int(M.shape[1]), rank=r, null_dim=len(null))
    extra = ''
    if 0 < len(null) <= 400 and sel in ('B6row0', 'B6key', 'S6dig'):
        wts = sorted(bin(v).count('1') for v in null)
        extra = f' null-vector weights (first 20): {wts[:20]}'
    P(f'{sel:7s} k={k:2d}: rows={M.shape[0]} cols={M.shape[1]} rank={r} null_dim={len(null)}{extra}')
out['rank'] = rk

# ---------- 3. per-coset: 300 cosets x 64 cubes ----------
P('\n== 3. per-coset test: 300 random cosets, 64 random span cubes each; (coset, bit) pairs with all 64 sums zero ==')
pc = {}
for name, k in (('coset_k2', 2), ('coset_k4', 4), ('coset_k7', 7), ('coset_k8', 8)):
    kk, sums = readvec(name)
    for sel in ST + ['B6row0']:
        src = SRC.get(sel, sel)
        if DEG[src] < k: continue
        M = bits_of(sums, src)[:, SEL[sel]].reshape(300, 64, -1)
        anyn = M.max(axis=1)                    # (300, cols): 1 if some cube nonzero on that coset
        z = int((anyn == 0).sum()); tot = anyn.size
        bits_somewhere = int(((anyn == 0).sum(axis=0) > 0).sum())
        pc[f'{sel}|k{k}'] = dict(pairs=tot, zero_pairs=z, bits_zero_on_some_coset=bits_somewhere)
        P(f'{sel:7s} k={k}: (coset,bit) pairs {tot}, all-zero pairs {z}, bits all-zero on at least one coset {bits_somewhere}')
out['per_coset'] = pc

# ---------- 4. t-dependence of the top-degree part: 500 direction sets x 16 cosets ----------
P('\n== 4. t-dependence: same k directions on 16 random cosets; fraction of (direction set, bit) pairs whose sum differs across cosets ==')
td = {}
for name, k in (('tdep_k2', 2), ('tdep_k4', 4), ('tdep_k8', 8), ('tdep_k16', 16)):
    kk, sums = readvec(name)
    g = len(sums) // 16
    for sel in ST + ['B6row0', 'S6dig']:
        src = SRC.get(sel, sel)
        if DEG[src] < k: continue
        M = bits_of(sums, src)[:, SEL[sel]].reshape(g, 16, -1)
        var = (M.max(axis=1) != M.min(axis=1))
        nz = M.max(axis=1) > 0
        td[f'{sel}|k{k}'] = dict(groups=g, varying_frac=round(float(var.mean()), 4), nonzero_frac=round(float(nz.mean()), 4))
        P(f'{sel:7s} k={k:2d}: direction sets {g}; pairs varying with t {var.mean():.4f}; pairs nonzero on some coset {nz.mean():.4f}')
out['t_dependence'] = td
json.dump(out, open(HERE + 'analysis.json', 'w'), indent=1)
P('\nwritten analysis.json')
