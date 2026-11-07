"""Join lever check for the BLAKE3 2-round parent node (grid cell basextech / mode / join).

f(L, R) = compress(IV, L || R, t=0, len=64, flags=PARENT|ROOT=12, rounds=2), 256-bit digest.
L, R are the two child CVs (8 words each).  A list / k-list (Wagner) join on f needs output bits that split
as g(L) (+) h(R).  For such a bit the second-order derivative
    D = f(L,R) ^ f(L',R) ^ f(L,R') ^ f(L',R')                   (XOR form)
    A = f(L,R) - f(L',R) - f(L,R') + f(L',R')  mod 2^32          (modular-add form, per word)
is identically 0.  Parts (all against a compression cross-checked with hash-smash/verifier/blake3.py):
  T1 random      L, L', R, R' uniform; per-bit P(D=1) over N quadruples (all 256 bits)
  T2 add         same quadruples, per-bit P(A bit = 1) and P(A word == 0)
  T3 word-pairs  L, L' differ only in word i, R, R' only in word j (64 pairs): a join over 2^32 x 2^32
                 sub-lists would need separability on that subspace
  T4 bit-pairs   L' = L ^ (1<<k in word i), R' = R ^ (1<<l in word j), k,l in {0,7,15,31} (1024 pairs):
                 low-weight differences, where 2 rounds might not have mixed L into R yet
Flag rule: |P - 1/2| >= 2^-8 and z >= Bonferroni threshold; every flagged cell is re-measured on fresh
samples (16x) and counted only if it survives.  Usage: sep_test.py LOGN [seed] -> prints, writes sep.json
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

import json
import math
import os
import struct
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/hash-smash'))
from verifier import blake3 as ref  # noqa: E402

np.seterr(over='ignore')
IV = [0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19]
PERM = [2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8]
BIAS_WIN = 2.0 ** -8


def ror(x, r):
    return (x >> np.uint32(r)) | (x << np.uint32(32 - r))


def g(v, a, b, c, d, x, y):
    v[a] = v[a] + v[b] + x; v[d] = ror(v[d] ^ v[a], 16); v[c] = v[c] + v[d]; v[b] = ror(v[b] ^ v[c], 12)
    v[a] = v[a] + v[b] + y; v[d] = ror(v[d] ^ v[a], 8); v[c] = v[c] + v[d]; v[b] = ror(v[b] ^ v[c], 7)


def compress(m, flags=12, rounds=2):          # m: (16, n) uint32, cv = IV, t = 0, block len 64
    n = m.shape[1]
    v = [np.full(n, IV[i], np.uint32) for i in range(8)] + [np.full(n, IV[i], np.uint32) for i in range(4)] + \
        [np.zeros(n, np.uint32), np.zeros(n, np.uint32), np.full(n, 64, np.uint32), np.full(n, flags, np.uint32)]
    m = [m[i] for i in range(16)]
    for _ in range(rounds):
        g(v, 0, 4, 8, 12, m[0], m[1]); g(v, 1, 5, 9, 13, m[2], m[3]); g(v, 2, 6, 10, 14, m[4], m[5]); g(v, 3, 7, 11, 15, m[6], m[7])
        g(v, 0, 5, 10, 15, m[8], m[9]); g(v, 1, 6, 11, 12, m[10], m[11]); g(v, 2, 7, 8, 13, m[12], m[13]); g(v, 3, 4, 9, 14, m[14], m[15])
        m = [m[PERM[i]] for i in range(16)]
    return np.stack([v[i] ^ v[i + 8] for i in range(8)])


def f(L, R):
    return compress(np.concatenate([L, R]))


def bitcount(X):                               # X (8, n) uint32 -> per-bit ones count (256,)
    out = np.zeros(256, np.int64)
    for w in range(8):
        for b in range(32):
            out[32 * w + b] = int(((X[w] >> np.uint32(b)) & np.uint32(1)).sum())
    return out


def rnd(rng, n):
    return rng.integers(0, 1 << 32, (8, n), dtype=np.uint64).astype(np.uint32)


def selfcheck(rng, n=50):
    ok = 0
    for _ in range(n):
        msg = rng.integers(0, 256, 2048, dtype=np.uint8).tobytes()
        d_ref = ref.blake3(msg, rounds=2)
        cv0 = ref._compress(*ref._chunk_output(msg[:1024], 0, 2), 2)[:8]
        cv1 = ref._compress(*ref._chunk_output(msg[1024:], 1, 2), 2)[:8]
        m = np.array(cv0 + cv1, dtype=np.uint32).reshape(16, 1)
        ok += struct.pack("<8I", *[int(w[0]) for w in compress(m)]) == d_ref
    # 1-round and 7-round sanity too: the same code at rounds=7 must equal the full BLAKE3 parent
    msg = rng.integers(0, 256, 2048, dtype=np.uint8).tobytes()
    cv0 = ref._compress(*ref._chunk_output(msg[:1024], 0, 7), 7)[:8]
    cv1 = ref._compress(*ref._chunk_output(msg[1024:], 1, 7), 7)[:8]
    m = np.array(cv0 + cv1, dtype=np.uint32).reshape(16, 1)
    ok7 = struct.pack("<8I", *[int(w[0]) for w in compress(m, rounds=7)]) == ref.blake3(msg, rounds=7)
    # anchor the verifier itself to the official BLAKE3 test vector for the empty input
    ok7 = ok7 and ref.blake3(b"").hex() == "af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262"
    return ok, n, bool(ok7)


def pair_quads(rng, n, kind, i, j, k=None, l=None):
    L, R = rnd(rng, n), rnd(rng, n)
    L2, R2 = L.copy(), R.copy()
    if kind == "word":
        L2[i] = rng.integers(0, 1 << 32, n, dtype=np.uint64).astype(np.uint32)
        R2[j] = rng.integers(0, 1 << 32, n, dtype=np.uint64).astype(np.uint32)
    else:
        L2[i] ^= np.uint32(1 << k)
        R2[j] ^= np.uint32(1 << l)
    return f(L, R) ^ f(L2, R) ^ f(L, R2) ^ f(L2, R2)


def scan_cells(rng, cells, n, ntests):
    """cells: list of (label, args). Returns per-cell max bias, flagged list after confirmation."""
    zthr = math.sqrt(2 * math.log(2 * ntests / 1e-3))            # Bonferroni, family error ~1e-3
    worst, flagged = (0.0, None, None), []
    for lab, args in cells:
        p = bitcount(pair_quads(rng, n, *args)) / n
        dev = np.abs(p - 0.5)
        b = int(dev.argmax())
        if dev[b] > worst[0]:
            worst = (float(dev[b]), lab, b)
        z = dev * 2 * math.sqrt(n)
        for bit in np.flatnonzero((dev >= BIAS_WIN) & (z >= zthr)):
            flagged.append((lab, args, int(bit), float(dev[bit])))
    confirmed = []
    for lab, args, bit, d0 in flagged[:4096]:
        n2 = 16 * n
        p2 = bitcount(pair_quads(rng, n2, *args))[bit] / n2
        d2 = abs(p2 - 0.5)
        if d2 >= BIAS_WIN and d2 * 2 * math.sqrt(n2) >= zthr:
            confirmed.append({"cell": lab, "bit": bit, "bias": d2, "p": p2})
    return worst, len(flagged), confirmed, zthr


def main():
    logn = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 20261011
    rng = np.random.default_rng(seed)
    out = {"logN": logn, "seed": seed}
    ok, n, ok7 = selfcheck(rng)
    out["selfcheck"] = f"{ok}/{n}"; out["selfcheck_r7"] = ok7
    print(f"self-check: parent compress (rounds=2) == verifier blake3(rounds=2) on 2-chunk messages {ok}/{n}; "
          f"rounds=7 == verifier: {ok7}", flush=True)
    if ok != n or not ok7:
        print("REFERENCE MISMATCH - abort"); sys.exit(2)

    # T1 + T2 on the same random quadruples
    N = 1 << logn
    B = min(N, 1 << 16)
    cx = np.zeros(256, np.int64); ca = np.zeros(256, np.int64); czero = np.zeros(8, np.int64)
    for _ in range(0, N, B):
        L, L2, R, R2 = rnd(rng, B), rnd(rng, B), rnd(rng, B), rnd(rng, B)
        a, b, c, d = f(L, R), f(L2, R), f(L, R2), f(L2, R2)
        cx += bitcount(a ^ b ^ c ^ d)
        A = a - b - c + d
        ca += bitcount(A)
        czero += (A == 0).sum(axis=1)
    for name, cnt in (("T1 xor", cx), ("T2 add", ca)):
        p = cnt / N; dev = np.abs(p - 0.5)
        out[name] = {"max_bias": float(dev.max()), "bit": int(dev.argmax()), "below_0.45": int((p < 0.45).sum()),
                     "sigma": 0.5 / math.sqrt(N)}
        print(f"{name}: N=2^{logn}  max |P-1/2| = {dev.max():.6f} (bit {int(dev.argmax())}, "
              f"{dev.max() / (0.5 / math.sqrt(N)):.2f} sigma)  bits with P<0.45: {int((p < 0.45).sum())}", flush=True)
    out["T2 add word==0 max frac"] = float((czero / N).max())
    print(f"T2 add: max over words of P(A word == 0) = {(czero / N).max():.3g} (separable word would give 1)", flush=True)

    # T3 word pairs
    n3 = max(1 << 10, N >> 6)
    cells = [(f"Lw{i}xRw{j}", ("word", i, j)) for i in range(8) for j in range(8)]
    worst, nf, conf, zthr = scan_cells(rng, cells, n3, len(cells) * 256)
    out["T3 word-pairs"] = {"n_per_cell": n3, "worst": worst, "flagged": nf, "confirmed": conf, "zthr": zthr}
    print(f"T3 word-pairs: 64 cells x {n3} quads; worst |P-1/2| = {worst[0]:.5f} ({worst[1]} bit {worst[2]}); "
          f"z-thr {zthr:.2f}; flagged {nf}; confirmed {len(conf)}", flush=True)

    # T4 single-bit difference pairs
    n4 = max(1 << 8, N >> 8)
    ks = (0, 7, 15, 31)
    cells = [(f"L{i}.{k}xR{j}.{l}", ("bit", i, j, k, l)) for i in range(8) for j in range(8) for k in ks for l in ks]
    worst, nf, conf, zthr = scan_cells(rng, cells, n4, len(cells) * 256)
    nbits_cells = {}
    for c in conf:
        nbits_cells.setdefault(c["cell"], 0); nbits_cells[c["cell"]] += 1
    out["T4 bit-pairs"] = {"n_per_cell": n4, "worst": worst, "flagged": nf, "confirmed_count": len(conf),
                           "cells_with_confirmed": len(nbits_cells),
                           "max_confirmed_bits_in_one_cell": max(nbits_cells.values()) if nbits_cells else 0,
                           "examples": conf[:12], "zthr": zthr}
    print(f"T4 bit-pairs: {len(cells)} cells x {n4} quads; worst |P-1/2| = {worst[0]:.5f} ({worst[1]} bit {worst[2]}); "
          f"flagged {nf}; confirmed {len(conf)} in {len(nbits_cells)} cells; max per cell "
          f"{out['T4 bit-pairs']['max_confirmed_bits_in_one_cell']}", flush=True)
    with open(os.path.join(HERE, "sep_u09.json"), "w") as fh:
        json.dump(out, fh, indent=1, default=str)


if __name__ == "__main__":
    main()
