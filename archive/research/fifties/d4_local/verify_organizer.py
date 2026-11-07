"""Verify dumped D4 section-7 constructions with the organizer's BLAKE3 code (rounds=2).

Record (180 bytes, little-endian u32): mA[16] mB[16] hA[4] hB[4] flags e[4]
flags: bit k = diagonal k fully solved (FIRST+SECOND), bit 4+k = FIRST had a root, bit 8 = complete.
Checks for every solved diagonal k: boundary b,c words equal after round 0 (2 words) and S_k = 0.
For complete records additionally D_0..D_3 recomputed and compared with the C value.
Also a synthetic test of the 7.3 claim (S_j + D_j + common b,c => round-1 column coalesces).
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

import glob
import importlib.util
import random
import struct
import sys

spec = importlib.util.spec_from_file_location(
    "b3", _hca_public_path_text('__HCA_WORKSPACE__/hash-smash/verifier/blake3.py'))
b3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b3)
_g, IV, PERM, _compress, MASK = b3._g, b3.IV, b3.PERMUTATION, b3._compress, b3.MASK

J = (1, 11, 12, 5, 9, 14, 15, 8)
DG = ((0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14))
COLS = ((0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15))


def trace(words, h):
    v = list(IV) + list(IV[:4]) + list(h)
    m = list(words)
    for j, (a, b, c, d) in enumerate(COLS):
        _g(v, a, b, c, d, m[2 * j], m[2 * j + 1])
    U = v[:]
    for k, (a, b, c, d) in enumerate(DG):
        _g(v, a, b, c, d, m[8 + 2 * k], m[9 + 2 * k])
    X = v[:]
    m1 = [m[i] for i in PERM]
    for j, (a, b, c, d) in enumerate(COLS):
        _g(v, a, b, c, d, m1[2 * j], m1[2 * j + 1])
    Y = v[:]
    for k, (a, b, c, d) in enumerate(DG):
        _g(v, a, b, c, d, m1[8 + 2 * k], m1[9 + 2 * k])
    out = tuple(v[i] ^ v[i + 8] for i in range(8)) + tuple(v[i + 8] ^ IV[i] for i in range(8))
    return U, X, m1, Y, out


def check_file(path, stats):
    data = open(path, "rb").read()
    n = len(data) // 180
    for r in range(n):
        w = struct.unpack_from("<45I", data, r * 180)
        mA, mB, hA, hB, fl, e = w[0:16], w[16:32], w[32:36], w[36:40], w[40], w[41:45]
        stats["records"] += 1
        if any(mA[s] != mB[s] for s in J):
            stats["fail_J"] += 1
        UA, XA, m1A, YA, oA = trace(mA, hA)
        UB, XB, m1B, YB, oB = trace(mB, hB)
        # organizer _compress must agree with the traced run
        for mm, hh, oo in ((mA, hA, oA), (mB, hB, oB)):
            ref = _compress(IV, mm, hh[0] | (hh[1] << 32), hh[2], hh[3], 2)
            if ref != oo:
                stats["fail_trace_vs_compress"] += 1
        for k in range(4):
            if not (fl >> k) & 1:
                continue
            stats["diag_solved"] += 1
            a, b, c, d = DG[k]
            if XA[b] != XB[b] or XA[c] != XB[c]:
                stats["fail_bc"] += 1
            else:
                stats["pass_bc_words"] += 2
            S = ((XB[k] - XA[k]) + (m1B[2 * k] - m1A[2 * k]) + (m1B[2 * k + 1] - m1A[2 * k + 1])) & MASK
            if S:
                stats["fail_S"] += 1
            else:
                stats["pass_S"] += 1
        if (fl >> 8) & 1:
            stats["complete"] += 1
            for k in range(4):
                Dv = (XA[k + 12] ^ ((XA[k] + XA[k + 4] + m1A[2 * k]) & MASK)) ^ (XB[k + 12] ^ ((XB[k] + XB[k + 4] + m1B[2 * k]) & MASK))
                if Dv != e[k]:
                    stats["fail_D_recompute"] += 1
            if oA == oB and (mA != mB or hA != hB):
                stats["COLLISION"] += 1


def synthetic(nt, stats):
    """7.3: with common incoming b,c, S_j and D_j hold => round-1 column outputs equal."""
    rnd = random.Random(5)
    for _ in range(nt):
        A_A, A_B, B, C, D_A, D_B, xA, yA = (rnd.getrandbits(32) for _ in range(8))
        xB = ((D_B ^ D_A ^ ((A_A + B + xA) & MASK)) - A_B - B) & MASK      # D_j
        yB = (yA - (A_B - A_A) - (xB - xA)) & MASK                          # S_j
        vA = [A_A, B, C, D_A]; vB = [A_B, B, C, D_B]
        _g(vA, 0, 1, 2, 3, xA, yA); _g(vB, 0, 1, 2, 3, xB, yB)
        stats["synthetic_trials"] += 1
        if vA != vB:
            stats["synthetic_fail"] += 1


if __name__ == "__main__":
    pattern = sys.argv[1] if len(sys.argv) > 1 else "dump_*.bin"
    stats = {k: 0 for k in ("records", "fail_J", "fail_trace_vs_compress", "diag_solved", "pass_bc_words", "fail_bc",
                            "pass_S", "fail_S", "complete", "fail_D_recompute", "COLLISION", "synthetic_trials", "synthetic_fail")}
    for p in sorted(glob.glob(pattern)):
        before = stats["records"]
        check_file(p, stats)
        print(p, "records", stats["records"] - before)
    synthetic(100000, stats)
    for k, v in stats.items():
        print(f"{k:24s} {v}")
