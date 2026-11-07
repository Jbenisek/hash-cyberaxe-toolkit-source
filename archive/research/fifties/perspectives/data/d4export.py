"""Export the residual words of the D4 partial constructions in fifties/d4_local/dump_*.bin (read-only).

No completed D4 construction exists (d4_local/RESULT.md); the 1,577 dumped records each have one solved diagonal.
For every record, with the ORGANIZER blake3.py (_g traced, cross-checked against _compress, rounds=2):
  D0..D3  = (XA[k+12] ^ (XA[k]+XA[k+4]+m1A[2k])) ^ (same for B)   (verify_organizer.py formula; the D4 residual checks)
  digest A, digest B (8 words each), their XOR (8 words), and the solved-diagonal checks (b,c equal; S_k = 0).
Output d4/d4_partial.u32, 76 u32 per record:
  arm (0 none, 1 len, 2 flags), seed, record index in its file, flags, D0..D3, dXOR[8], digA[8], digB[8],
  mA[16], mB[16], hA[4], hB[4], e[4] (the C program's stored D values; meaningful only when flags bit 8 is set)
and d4/d4_partial.csv (arm, seed, idx, flags, D0..D3, dXOR0..7 in hex).
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
sys.dont_write_bytecode = True
import glob, importlib.util, os, struct

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = _hca_public_path_text('__HCA_WORKSPACE__/research/fifties/d4_local')
spec = importlib.util.spec_from_file_location("b3", _hca_public_path_text('__HCA_WORKSPACE__/hash-smash/verifier/blake3.py'))
b3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b3)
_g, IV, PERM, _compress, MASK = b3._g, b3.IV, b3.PERMUTATION, b3._compress, b3.MASK
DG = ((0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14))
COLS = ((0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15))
ARMS = {"none": 0, "len": 1, "flags": 2}


def trace(words, h):
    v = list(IV) + list(IV[:4]) + list(h)
    m = list(words)
    for j, (a, b, c, d) in enumerate(COLS):
        _g(v, a, b, c, d, m[2 * j], m[2 * j + 1])
    for k, (a, b, c, d) in enumerate(DG):
        _g(v, a, b, c, d, m[8 + 2 * k], m[9 + 2 * k])
    X = v[:]
    m1 = [m[i] for i in PERM]
    for j, (a, b, c, d) in enumerate(COLS):
        _g(v, a, b, c, d, m1[2 * j], m1[2 * j + 1])
    for k, (a, b, c, d) in enumerate(DG):
        _g(v, a, b, c, d, m1[8 + 2 * k], m1[9 + 2 * k])
    return X, m1, tuple(v[i] ^ v[i + 8] for i in range(8)) + tuple(v[i + 8] ^ IV[i] for i in range(8))


def main():
    os.makedirs(os.path.join(HERE, "d4"), exist_ok=True)
    stats = dict(records=0, trace_vs_compress_fail=0, diag_solved=0, bc_fail=0, S_fail=0, complete=0,
                 zero_D_words=0, zero_digest_xor_words=0)
    out = open(os.path.join(HERE, "d4", "d4_partial.u32"), "wb")
    csv = open(os.path.join(HERE, "d4", "d4_partial.csv"), "w")
    csv.write("arm,seed,idx,flags,D0,D1,D2,D3," + ",".join("dxor%d" % i for i in range(8)) + "\n")
    for p in sorted(glob.glob(os.path.join(SRC_DIR, "dump_*.bin"))):
        _, arm, seed = os.path.basename(p)[:-4].split("_")
        data = open(p, "rb").read()
        for r in range(len(data) // 180):
            w = struct.unpack_from("<45I", data, r * 180)
            mA, mB, hA, hB, fl, e = w[0:16], w[16:32], w[32:36], w[36:40], w[40], w[41:45]
            stats["records"] += 1
            XA, m1A, oA = trace(mA, hA)
            XB, m1B, oB = trace(mB, hB)
            for mm, hh, oo in ((mA, hA, oA), (mB, hB, oB)):
                if _compress(IV, mm, hh[0] | (hh[1] << 32), hh[2], hh[3], 2) != oo:
                    stats["trace_vs_compress_fail"] += 1
            for k in range(4):
                if fl >> k & 1:
                    stats["diag_solved"] += 1
                    a, b, c, d = DG[k]
                    stats["bc_fail"] += XA[b] != XB[b] or XA[c] != XB[c]
                    S = ((XB[k] - XA[k]) + (m1B[2 * k] - m1A[2 * k]) + (m1B[2 * k + 1] - m1A[2 * k + 1])) & MASK
                    stats["S_fail"] += S != 0
            stats["complete"] += fl >> 8 & 1
            D = [(XA[k + 12] ^ ((XA[k] + XA[k + 4] + m1A[2 * k]) & MASK)) ^
                 (XB[k + 12] ^ ((XB[k] + XB[k + 4] + m1B[2 * k]) & MASK)) for k in range(4)]
            dA, dB = oA[:8], oB[:8]
            dx = [x ^ y for x, y in zip(dA, dB)]
            stats["zero_D_words"] += sum(x == 0 for x in D)
            stats["zero_digest_xor_words"] += sum(x == 0 for x in dx)
            row = [ARMS[arm], int(seed), r, fl] + D + dx + list(dA) + list(dB) + list(mA) + list(mB) + list(hA) + list(hB) + list(e)
            assert len(row) == 76
            out.write(struct.pack("<76I", *row))
            csv.write("%s,%s,%d,%x," % (arm, seed, r, fl) + ",".join("%08x" % x for x in D + dx) + "\n")
    out.close(); csv.close()
    for k, v in stats.items():
        print("%-26s %d" % (k, v))


if __name__ == "__main__":
    main()
