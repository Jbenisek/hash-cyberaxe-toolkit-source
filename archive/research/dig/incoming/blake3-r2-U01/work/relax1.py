# Q2 for blake3-r2 C1/Y9: relax filter (1) and the packed prefilter PF; recount pass counts and SHARE.

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

import sys, random, time, json
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/tools/traillab/b3atlas'))
from rows_dp import ror, rol, sig, ETA, taus, rows, stats, M
import numpy as np
TAU = 0x285020a0
THETA = rol(sig(TAU), 12)
assert THETA == 0x830F03C7, hex(THETA)
out = {}
t0 = time.time()
# ---- control: reproduce package numbers with the existing DP
A, B, SH = stats([3, 14])
print('control (1)=%d (2)=%d SHARE=%d' % (A, B, SH)); assert A == 14110208 and B == 63633856 and SH == 897886944002048
out['control'] = dict(A=A, E_COUNT=B, SHARE=SH)

def alive_counts(relax=0, nmax=32, nola=False):
    """single pass over bits of x. relax = bitmask of theta bits whose output condition is NOT enforced.
    returns list cnt[n] = number of n-bit prefixes of x with non-empty witness set after bit n-1."""
    st = {frozenset([(0, 0)]): 1}
    cnt = [1]
    for i in range(nmax):
        e = (ETA >> i) & 1; t = (THETA >> i) & 1; free = (relax >> i) & 1
        nst = {}
        for S, c in st.items():
            for xi in (0, 1):
                out_ = set()
                for (ca, cb) in S:
                    if (not free) and (e ^ ca ^ cb) != t: continue
                    for hi in (0, 1):
                        out_.add(((xi + hi + ca) >> 1, (xi + (hi ^ e) + cb) >> 1))
                if out_:
                    k = frozenset(out_); nst[k] = nst.get(k, 0) + c
        st = nst
        if nola:
            cnt.append(sum(st.values()))
        elif i < 31:
            e2 = (ETA >> (i+1)) & 1; t2 = (THETA >> (i+1)) & 1; f2 = (relax >> (i+1)) & 1
            cnt.append(sum(c for S, c in st.items() if f2 or any((e2 ^ ca ^ cb) == t2 for (ca, cb) in S)))
        else:
            cnt.append(sum(st.values()))
    return cnt

# ---- validation 1: automaton prefix sets vs brute force over h at width n (known answer), n = 8..14
def brute_alive(n):
    mask = (1 << n) - 1
    xs = np.arange(1 << n, dtype=np.uint64)
    ok = np.zeros(1 << n, dtype=bool)
    hs = np.arange(1 << n, dtype=np.uint64)
    for h in range(1 << n):
        d = ((xs + np.uint64(h)) ^ (xs + np.uint64(h ^ (ETA & mask)))) & np.uint64(mask)
        ok |= (d == np.uint64(THETA & mask))
    return int(ok.sum())
cnt = alive_counts()
cnt_nola = alive_counts(nola=True)
val = {}
for n in range(4, 15):
    b = brute_alive(n); val[n] = (b, cnt_nola[n]); assert b == cnt_nola[n], (n, b, cnt_nola[n])
print('validation (brute force over h vs automaton), n:(brute,auto)', val, ' %.1fs' % (time.time() - t0))
out['validation'] = {str(k): v for k, v in val.items()}
assert cnt[10] == 14 and cnt[32] == 14110208
# ---- A_n curve (relax = ignore all conditions on bits >= n)
curve = {}
for n in range(0, 33):
    An = cnt[n] * (1 << (32 - n)); curve[n] = An
print('prefix-n relax: n, accepted words, fraction, x(1) count')
for n in (0, 1, 2, 4, 6, 8, 10, 12, 14, 16, 20, 24, 28, 31, 32):
    print(n, curve[n], '%.6f' % (curve[n] / 2**32), 'x%.2f' % (curve[n] / 14110208))
out['prefix_curve'] = {str(n): curve[n] for n in curve}
# PF as packed (7 bits fixed, 2 patterns)
PF_ACC = 2 * 2**25
# exact enumerate PF via mask rule on low 10 bits vs automaton prefixes
pf_low = [p for p in range(1024) if (p & 0x3c7) in (0x004, 0x3c4)]
assert len(pf_low) == 16 and PF_ACC == 16 * 2**22
# automaton prefixes (14) subset of PF low10
alive10 = []
for p in range(1024):
    pass
out['PF'] = dict(accepted=PF_ACC, frac=PF_ACC / 2**32, exact_prefix10=curve[10], over_exact=PF_ACC / 14110208)
print('PF accepted words', PF_ACC, 'frac 1/%.1f' % (2**32 / PF_ACC), ' exact (1) 1/%.1f' % (2**32 / 14110208), ' PF/exact x%.4f' % (PF_ACC / 14110208))
# ---- relax one theta bit i
single = {}
for i in range(32):
    c = alive_counts(relax=1 << i)[32]
    single[i] = c
print('relax theta bit i -> accepted words (x exact)')
print({i: (single[i], round(single[i] / 14110208, 3)) for i in range(32)})
out['single_bit_relax'] = {str(i): single[i] for i in range(32)}
# relax groups of 8 bits
grp = {}
for g in range(4):
    m = 0xff << (8 * g); grp[g] = alive_counts(relax=m)[32]
print('relax byte g:', grp)
out['byte_relax'] = {str(g): grp[g] for g in grp}
out['all_relaxed'] = 2**32
# SHARE (pairs passing both) under each relaxation = accepted * E_COUNT
E = 63633856
out['SHARE_exact'] = 14110208 * E
json.dump(out, open('relax1_out.json', 'w'), indent=1)
print('done %.1fs' % (time.time() - t0))
