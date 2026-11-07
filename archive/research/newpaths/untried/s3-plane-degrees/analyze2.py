"""Per-coset rank of the top-degree parts (runs/pcrank_k*.vec.bin): on ONE fixed coset, the GF(2) rank of the matrix of
k-cube-sum vectors = dimension of the span of the degree-k parts on that coset; cols - rank = combinations of degree < k there.
Also: individually low-degree bits on each coset, and whether the null spaces of different cosets intersect."""

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

import struct, json
import numpy as np
HERE = _hca_public_path_text('__HCA_WORKSPACE__/research/newpaths/untried/s3-plane-degrees/')
R = HERE + 'runs/'
ST = ['S1', 'S2', 'B3', 'S3', 'B4', 'S4', 'B5', 'S5', 'B6', 'S6']
SEL = {s: list(range(1600)) for s in ST}
SEL['B6row0'] = list(range(320)); SEL['S6dig'] = list(range(256))
SEL['B6key'] = [64 * x + z for x in range(5) for z in range(35)]
SRC = {'B6row0': 'B6', 'S6dig': 'S6', 'B6key': 'B6'}
log = open(HERE + 'out_analysis2.txt', 'w')
def P(*a):
    s = ' '.join(str(x) for x in a); print(s); log.write(s + '\n'); log.flush()

def readvec(name):
    b = open(R + name + '.vec.bin', 'rb').read()
    magic, k, n, nst = struct.unpack('<4i', b[:16])
    rec = 40 + 40 * k + 8 * k + 8 * 25 * nst
    arr = np.frombuffer(b, dtype=np.uint8, count=n * rec, offset=16).reshape(n, rec)
    t = arr[:, :40].copy().view('<u8')
    sums = arr[:, 40 + 48 * k:].copy().view('<u8').reshape(n, nst, 25)
    return k, t, sums

def bits_of(sums, stage):
    w = sums[:, ST.index(stage), :]
    return np.unpackbits(w.view(np.uint8).reshape(len(w), 200), axis=1, bitorder='little')

def gf2_rank_null(M):
    rows, cols = M.shape
    piv = {}
    packed = np.packbits(M[:, ::-1], axis=1, bitorder='big')
    sh = packed.shape[1] * 8 - cols
    for r in range(rows):
        x = int.from_bytes(packed[r].tobytes(), 'big') >> sh
        while x:
            t = x.bit_length() - 1
            if t in piv: x ^= piv[t]
            else: piv[t] = x; break
    pcs = sorted(piv)
    for c in pcs:
        for c2 in pcs:
            if c2 > c and (piv[c2] >> c) & 1: piv[c2] ^= piv[c]
    null = []
    for f in range(cols):
        if f in piv: continue
        v = 1 << f
        for c in pcs:
            if (piv[c] >> f) & 1: v |= 1 << c
        null.append(v)
    return len(piv), null

def rank_ints(vs):
    piv = {}
    for x in vs:
        while x:
            t = x.bit_length() - 1
            if t in piv: x ^= piv[t]
            else: piv[t] = x; break
    return len(piv)

out = {}
for name, sels, per in (('pcrank_k2', ['S3', 'B4'], 2400), ('pcrank_k4', ['S4', 'B5'], 2400),
                        ('pcrank_k7', ['S5', 'B6', 'B6row0', 'B6key'], 2400), ('pcrank_k8', ['S5', 'B6', 'B6row0', 'B6key'], 2400),
                        ('pcrank_k16', ['S6dig'], 600)):
    k, t, sums = readvec(name)
    nc = len(sums) // per
    for sel in sels:
        M = bits_of(sums, SRC.get(sel, sel))[:, SEL[sel]]
        res = []; nulls = []
        for c in range(nc):
            Mc = M[c * per:(c + 1) * per]
            assert (t[c * per:(c + 1) * per] == t[c * per]).all()
            r, null = gf2_rank_null(Mc)
            zero_cols = int((Mc.max(axis=0) == 0).sum())
            res.append((r, len(null), zero_cols)); nulls.append(null)
        inter = ''
        if all(len(nl) > 0 for nl in nulls) and nc >= 2:
            # dimension of the intersection of the null spaces of coset 0 and coset 1: dim A + dim B - dim(A+B)
            a, b = nulls[0], nulls[1]
            inter = f'; null(coset0) cap null(coset1) dim = {len(a) + len(b) - rank_ints(a + b)}'
        P(f'{name} {sel:7s} k={k:2d} cols={M.shape[1]:4d} rows/coset={per}: per coset (rank, null_dim, bits individually of degree<k) = {res}{inter}')
        out[f'{name}|{sel}'] = dict(k=k, cols=M.shape[1], rows_per_coset=per, per_coset=res)
json.dump(out, open(HERE + 'analysis2.json', 'w'), indent=1)
