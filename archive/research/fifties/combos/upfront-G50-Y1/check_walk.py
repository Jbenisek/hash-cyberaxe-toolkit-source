"""Cross-check the vectorized gate / E-lane / pass / fill counts against frontline_full.walk() itself.

walk(seed) walks representative batches 0..3 and 2340 (TRIAL_REPS = 5) with every opened cluster's partners.
For the same outer words we recompute, with the screen_ck2 vector code, the opened count, E lanes, passes,
solver calls and fills over exactly those batches, and compare with walk's observations.
usage: python check_walk.py NSEEDS
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

import sys
import os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/tools/build_pkg/scratch/pkgCJ/work'))
import frontline_full as F  # noqa: E402

M, U64 = F.M, np.uint64
KK = np.arange(1 << 19, dtype=np.uint64)
E1 = U64(F.CLASS_VALUE) | np.array(F.SPL, dtype=np.uint64)[KK & U64(1023)] | np.array(F.SPH, dtype=np.uint64)[KK >> U64(10)]
YY = (E1 - U64(F.Y3)) & U64(M)
NEED = F.closure(["Y9", "w8", "C2.c1", "C2.b1", "Y0"])
vecf = F.compile_lines("vecf", F.ARGS + ["Y4", "fl"], [n for n, _ in F.LINES if n in NEED],
                       "Y0, w8, Y9, C2_c1, C2_b1, C0_b1, w6, X4, w2, S0, S5, S15")
F1A, F2A = np.array(F.F1, dtype=np.int64), np.array(F.F2, dtype=np.int64)
VM = np.array(F.VMASK, dtype=np.int64)
S7A = np.array([F.S7 >> i & 1 for i in range(128)], dtype=np.int64)


def tlook(f, x):
    x = x.astype(np.int64)
    s = f[x & 255]
    s = f[s + (x >> 8 & 255)]
    s = f[s + (x >> 16 & 255)]
    return f[s + (x >> 24)]


bad = 0
for n in range(int(sys.argv[1])):
    seed = b"upfront-check-%d" % n
    ow, first, o = F.walk(seed)
    Y0, w8, Y9, C2c, C2b, C0b1, w6, X4, w2, S0, S5, S15 = vecf(*ow, YY, F.FLAGS)
    om = (U64(F.Y3) + YY + w8) & U64(M)
    m2 = tlook(F2A, om)
    x = tlook(F1A, Y9) & m2
    Q, e1i = Y9.astype(np.int64), E1.astype(np.int64)
    nu = (((((((Q >> 16) ^ e1i) & 4) ^ 7) + C2c.astype(np.int64)) & M) ^ C2b.astype(np.int64) ^ 1) & 7
    T = x & VM[nu]
    A = (C0b1 + w6 + X4 + w2) & M
    nA, P15, q = (-(A >> 16)) & 127, (-(S0 + S5)) & M, (F.rol(F.X15, 24) ^ S15) & 127
    reps = [g for rb in (0, 1, 2, 3, 2340) for g in range(7 * rb, min(7 * rb + 7, 1 << 14))]
    opened = calls = e_l = ps = fills = 0
    for rb in (0, 1, 2, 3, 2340):
        rep_fill = False
        for g in range(7 * rb, min(7 * rb + 7, 1 << 14)):
            k = g & 63 | (g >> 6) << 11
            a = ((int(Y0[k]) >> 16 & 127) + nA) & 127
            c = (int(E1[k]) + P15) & 127
            if not (S7A[((a ^ q) + c) & 127] | S7A[((((a - 1) & 127) ^ q) + c) & 127]):
                continue
            opened += 1
            rep_fill |= bool(m2[k])
            for lo, hi in ((0, 1), (1, 8), (8, 15), (15, 22), (22, 29), (29, 32)):
                ks = [g & 63 | j << 6 | (g >> 6) << 11 for j in range(lo, hi)]
                e_l += sum(bool(m2[kk]) for kk in ks)
                ps += sum(bool(x[kk]) for kk in ks)
                calls += sum(bool(T[kk]) for kk in ks)
                if lo:
                    fills += any(bool(m2[kk]) for kk in ks)
        fills += rep_fill
    mine = dict(opened=opened, e_lanes=e_l, passes=ps, solver_calls=calls, fills=fills)
    theirs = {k: o[k] for k in mine}
    ok = mine == theirs and o["halted"] == 0
    bad += not ok
    print(n, "walk", theirs, "halted", o["halted"], "mismatches", o["mismatches"], "| vector", mine,
          "OK" if ok else "DIFF", flush=True)
print("contexts with a difference:", bad)
