# Diagnostic (COMPUTED): which j carry the survivors and the E lanes inside opened clusters, and how many of today's
# consecutive partner batches (j = 1-7, 8-14, 15-21, 22-28, 29-31) they touch.  Test seeds outside the preregistered list.

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
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/fifties/combos/crossline-XF1'))
import walk_mask as X
F = X.F
M, LB, ONES = F.M, F.LB, F.ONES
for seed in (b"xf1-9000", b"xf1-9001", b"xf1-9002"):
    _, ow = X.context(seed)
    cx = F.co_ctx(*ow, F.FLAGS)
    P = F.operands(cx)
    v, cw = X.ctx_words(ow)
    masks, chunks, tops, ok = X.build_table(v, cw[3])
    print(seed, "table entries (idx: survivor j list):")
    for idx in range(64, 128, 9):
        print("  ", idx, [j for j in range(32) if masks[idx] >> j & 1])
    batch_of = lambda j: 0 if j == 0 else (j - 1) // 7 + 1
    hb = {}
    shown = 0
    nA = (-((cx["C0_b1"] + cx["w6"] + cx["X4"] + cx["w2"] & M) >> 16) & 127) * ONES
    Pq = ((F.rol(F.X15, 24) ^ cx["S15"]) & 127) << 14
    for rb in range(0, F.REP_BATCHES, 3):
        reps = [F.cmember(g, 0) for g in range(7 * rb, min(7 * rb + 7, 1 << 14))]
        U, E = F.pack(reps)
        C0a1, D0d1, om, ov, Y0 = F.omega_side(U, E, P)
        key = ((Y0 >> 16 & F.R7) + nA & F.R7) | (E + P[15] & F.R7) << 7
        for i in range(len(reps)):
            if not F.gate(Pq | key >> LB * i & 0x3FFF):
                continue
            g = 7 * rb + i
            oms = [F.co_ref(*ow, F.cmember(g, j)[1], F.FLAGS)[0] for j in range(32)]
            ej = [j for j in range(32) if F.T2(oms[j])]
            nb = len({batch_of(j) for j in ej})
            hb[nb] = hb.get(nb, 0) + 1
            if ej and shown < 6:
                shown += 1
                print("   g %5d E-lane j: %s  omega[9..13]: %s" % (g, ej, [oms[j] >> 9 & 31 for j in ej]))
    print("  batches touched by E lanes per opened cluster (every 3rd rep batch):", dict(sorted(hb.items())))
