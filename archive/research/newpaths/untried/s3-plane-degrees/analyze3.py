"""Round-3 'door' on special cosets: chi3 output bits that are AFFINE on a whole coset t + W40 (coset_k2: all 64 random
2-cube sums zero), explained by the chi3 input linear forms on the same coset (coset_k1: 64 random first derivatives):
chi3 out (x,y,z) = b(x) + (b(x+1)+1) b(x+2) is affine on the coset iff form(x+1) = 0, form(x+2) = 0 or form(x+1) = form(x+2)."""

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
from collections import Counter
HERE = _hca_public_path_text('__HCA_WORKSPACE__/research/newpaths/untried/s3-plane-degrees/')
R = HERE + 'runs/'
ST = ['S1', 'S2', 'B3', 'S3', 'B4', 'S4', 'B5', 'S5', 'B6', 'S6']
log = open(HERE + 'out_analysis3.txt', 'w')
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

k2, t2, s2 = readvec('coset_k2'); k1, t1, s1 = readvec('coset_k1')
assert (t1 == t2).all(), 'coset runs do not share cosets'
NC = 300
S3 = bits_of(s2, 'S3').reshape(NC, 64, 1600)
B3 = bits_of(s1, 'B3').reshape(NC, 64, 1600)       # first derivatives of the chi3 inputs, 64 random directions
aff = S3.max(axis=1) == 0                            # (coset, bit) chi3 output affine on the coset
const = B3.max(axis=1) == 0                          # (coset, bit) chi3 input constant on the coset
per = aff.sum(axis=1)
P(f'cosets: {NC}; chi3-output bits affine on the coset: total pairs {int(aff.sum())}, cosets with >=1: {int((per > 0).sum())}, '
  f'max per coset {int(per.max())}, histogram {dict(sorted(Counter(per.tolist()).items()))}')
P(f'chi3-input bits constant on the coset: total pairs {int(const.sum())}, cosets with >=1: {int((const.sum(axis=1) > 0).sum())}, '
  f'histogram {dict(sorted(Counter(const.sum(axis=1).tolist()).items()))}')
why = Counter(); bitfreq = Counter()
for c in range(NC):
    for i in np.nonzero(aff[c])[0]:
        lane, z = divmod(int(i), 64); x, y = lane % 5, lane // 5
        a = 64 * (((x + 1) % 5) + 5 * y) + z; b = 64 * (((x + 2) % 5) + 5 * y) + z
        bitfreq[(x, y, z)] += 1
        if const[c, a] and const[c, b]: why['both inputs constant'] += 1
        elif const[c, a]: why['input x+1 constant'] += 1
        elif const[c, b]: why['input x+2 constant'] += 1
        elif (B3[c, :, a] == B3[c, :, b]).all(): why['inputs x+1, x+2 equal forms'] += 1
        else: why['unexplained'] += 1
P('explanation of each affine pair:', dict(why))
P(f'distinct affine chi3-output bits: {len(bitfreq)}; (x,y,z): cosets of 300 = {dict(sorted(bitfreq.items(), key=lambda kv: -kv[1]))}')
cb = Counter()
for c in range(NC):
    for i in np.nonzero(const[c])[0]:
        lane, z = divmod(int(i), 64); cb[(lane % 5, lane // 5, z)] += 1
P(f'distinct chi3-input bits constant on some coset: {len(cb)}; top: {dict(sorted(cb.items(), key=lambda kv: -kv[1])[:40])}')
json.dump(dict(aff_pairs=int(aff.sum()), cosets_with_aff=int((per > 0).sum()), max_per_coset=int(per.max()),
               why=dict(why), aff_bits={str(k): v for k, v in bitfreq.items()},
               const_pairs=int(const.sum()), const_bits={str(k): v for k, v in cb.items()}),
          open(HERE + 'analysis3.json', 'w'), indent=1)
