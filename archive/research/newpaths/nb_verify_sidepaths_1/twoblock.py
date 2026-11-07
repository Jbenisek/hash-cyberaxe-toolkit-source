"""S8 check: the filed 55/63 construction (pin H8) moved into the LAST block of a two-block message.

Block 0: 64 arbitrary bytes, flags CHUNK_START, CV = first 8 words of its 2-round compression (organizer reference).
Block 1: built like ../sidepaths/fam55.py but with v0..v7 = CV and flags = CHUNK_END|ROOT = 10.
The pin is kept in the CV-free coordinates T = X3 + X7 - K, Q = K + W4 (K = cv2 + cv6), X7, X11, X15, W13:
for a new CV, X3' = X3 + (K' - K_IV) and W4' = W4 - (K' - K_IV).
Checks (against hash-smash/verifier/blake3.py, read only):
  1. digest words 0,2,5,7 agree for 119- vs 127-byte messages (same block 0, last blocks of 55 / 63 bytes);
  2. C3's four outputs (Y3, Y7, Y11, Y15) of both messages and the w5 difference are identical for every CV;
  3. Y4 = y (the member) for every CV.
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

import random
import struct
import sys

sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/hash-smash'))
from verifier.blake3 import blake3 as ref, _compress  # noqa: E402

M = 0xFFFFFFFF
IV = (0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19)
PERM = (2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8)
X3_IV, X7, X11, X15, W4_IV, W13 = 0x29d4fa98, 0xbee3af28, 0x44036000, 0x40c58500, 0x97475638, 0x0007c006
K_IV = (IV[2] + IV[6]) & M
Q = (K_IV + W4_IV) & M
T = (X3_IV + X7 - K_IV) & M
SUB_AND, CLASS_VAL = 0x07ef8303, 0x030c0303
Y3A = 0x8127c181


def ror(x, r):
    return ((x >> r) | (x << (32 - r))) & M


def rol(x, r):
    return ((x << r) | (x >> (32 - r))) & M


def G(a, b, c, d, x, y):
    a = (a + b + x) & M; d = ror(d ^ a, 16); c = (c + d) & M; b = ror(b ^ c, 12)
    a = (a + b + y) & M; d = ror(d ^ a, 8); c = (c + d) & M; b = ror(b ^ c, 7)
    return a, b, c, d


def state(cv, w, n, flags, rounds=2):
    v = list(cv) + list(IV[:4]) + [0, 0, n, flags]
    s = list(w)
    snaps = []
    for _ in range(rounds):
        for (a, b, c, d), i in zip(((0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15),
                                    (0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14)), range(8)):
            v[a], v[b], v[c], v[d] = G(v[a], v[b], v[c], v[d], s[2 * i], s[2 * i + 1])
            if i == 3:
                snaps.append(list(v))          # after the column step of this round
        s = [s[p] for p in PERM]
    return v, snaps


def build(cv, flags, Cc1, Cd1, D3d1, S15, S9, w5, X2, y):
    K = (cv[2] + cv[6]) & M
    X3 = (T - X7 + K) & M
    W4 = (Q - K) & M
    # Step O  (v10 = IV2 and v11 = IV3 stay IV; v4..v7 are the CV)
    K2a1 = (cv[2] + cv[6] + W4) & M; K2d1 = ror(55 ^ K2a1, 16)
    K2c1 = (IV[2] + K2d1) & M; K2b1 = ror(cv[6] ^ K2c1, 12)
    S2 = (K2a1 + K2b1 + w5) & M; S14 = ror(K2d1 ^ S2, 8)
    S10 = (K2c1 + S14) & M; S6 = ror(K2b1 ^ S10, 7)
    D3a1 = rol(D3d1, 16) ^ S14; D3c1 = (S9 + D3d1) & M
    D3b1 = (X3 - D3a1) & M; S4 = rol(D3b1, 12) ^ D3c1
    S3 = (D3a1 - S4) & M; X14 = ror(D3d1 ^ X3, 8)
    X9 = (D3c1 + X14) & M; X4 = ror(D3b1 ^ X9, 7)
    K3d1 = rol(S15, 8) ^ S3; K3c1 = (IV[3] + K3d1) & M
    K3b1 = ror(cv[7] ^ K3c1, 12); S11 = (K3c1 + S15) & M
    S7 = ror(K3b1 ^ S11, 7); K3a1 = rol(K3d1, 16) ^ flags
    w6 = (K3a1 - cv[3] - cv[7]) & M; w7 = (S3 - K3a1 - K3b1) & M
    X8 = (Cc1 - Cd1) & M; C0b1 = ror(X4 ^ Cc1, 12)
    D2b1 = rol(X7, 7) ^ X8; D2c1 = rol(D2b1, 12) ^ S7
    X13 = (X8 - D2c1) & M
    # Step M
    D2a1 = (X2 - D2b1 - W13) & M; D2d1 = rol(X13, 8) ^ X2
    S13 = rol(D2d1, 16) ^ D2a1; S8 = (D2c1 - D2d1) & M
    w12 = (D2a1 - S2 - S7) & M
    K1c1 = (S9 - S13) & M; K1d1 = (K1c1 - IV[1]) & M
    K1a1 = rol(K1d1, 16); K1b1 = ror(cv[5] ^ K1c1, 12)
    S1 = rol(S13, 8) ^ K1d1; S5 = ror(K1b1 ^ S9, 7)
    w2 = (K1a1 - cv[1] - cv[5]) & M; w3 = (S1 - K1a1 - K1b1) & M
    K0b1 = rol(S4, 7) ^ S8; K0c1 = rol(K0b1, 12) ^ cv[4]
    K0d1 = (K0c1 - IV[0]) & M; K0a1 = rol(K0d1, 16)
    S12 = (S8 - K0c1) & M; S0 = rol(S12, 8) ^ K0d1
    w0 = (K0a1 - cv[0] - cv[4]) & M; w1 = (S0 - K0a1 - K0b1) & M
    # Step Y
    Y8 = rol(y, 7) ^ C0b1; Y12 = (Y8 - Cc1) & M
    Y0 = rol(Y12, 8) ^ Cd1; C0a1 = (Y0 - C0b1 - w6) & M
    X12 = rol(Cd1, 16) ^ C0a1
    D1c1 = (X11 - X12) & M; D1b1 = ror(S6 ^ D1c1, 12)
    X6 = ror(D1b1 ^ X11, 7); D1d1 = (D1c1 - S11) & M
    X1 = rol(X12, 8) ^ D1d1
    # Step T
    X0 = (C0a1 - X4 - w2) & M
    D0d1 = rol(X15, 8) ^ X0; D0c1 = (S10 + D0d1) & M
    X10 = (D0c1 + X15) & M; D0b1 = ror(S5 ^ D0c1, 12)
    X5 = ror(D0b1 ^ X10, 7); D0a1 = rol(D0d1, 16) ^ S15
    w8 = (D0a1 - S0 - S5) & M; w9 = (X0 - D0a1 - D0b1) & M
    D1a1 = rol(D1d1, 16) ^ S12; w10 = (D1a1 - S1 - S6) & M
    w11 = (X1 - D1a1 - D1b1) & M
    words = [w0, w1, w2, w3, W4, w5, w6, w7, w8, w9, w10, w11, w12, W13, 0, 0]
    W4B = ((Q ^ 8) - K) & M
    other = list(words)
    other[4] = W4B
    other[5] = (w5 + W4 - W4B) & M
    return words, other


def member(k):
    free = [i for i in range(32) if not SUB_AND >> i & 1]
    e1 = CLASS_VAL
    for j, p in enumerate(free):
        if k >> j & 1:
            e1 |= 1 << p
    return (e1 - Y3A) & M


def main():
    rng = random.Random(20261008)
    ok = 0
    c3_sets = set()
    dw5_set = set()
    ncv = 12
    per_cv = 25
    for t in range(ncv):
        if t == 0:
            b0 = None
            cv, flags = IV, 11                      # the filed single-block case
        else:
            b0 = bytes(rng.randrange(256) for _ in range(64))
            cv = _compress(IV, struct.unpack("<16I", b0), 0, 64, 1, 2)[:8]
            flags = 10                               # CHUNK_END | ROOT, not the first block
        for _ in range(per_cv):
            free = [rng.randrange(1 << 32) for _ in range(7)] + [member(rng.randrange(1 << 17))]
            wa, wb = build(cv, flags, *free)
            A = struct.pack("<16I", *wa)[:55]
            B = struct.pack("<16I", *wb)[:63]
            assert struct.unpack("<16I", A + bytes(9)) == tuple(wa)
            assert struct.unpack("<16I", B + bytes(1)) == tuple(wb)
            msgA = A if b0 is None else b0 + A
            msgB = B if b0 is None else b0 + B
            dA = struct.unpack("<8I", ref(msgA, 2))
            dB = struct.unpack("<8I", ref(msgB, 2))
            assert all(dA[i] == dB[i] for i in (0, 2, 5, 7)), (t, dA, dB)
            vA, sA = state(cv, wa, 55, flags)
            vB, sB = state(cv, wb, 63, flags)
            YA, YB = sA[1], sB[1]                  # round-1 column outputs
            assert YA[4] == free[7] and YB[4] == free[7]
            c3_sets.add((YA[3], YA[7], YA[11], YA[15], YB[3], YB[7], YB[11], YB[15]))
            dw5_set.add((wb[5] - wa[5]) & M)
            ok += 1
        print(f"cv {t:2d} flags {flags} cv0={cv[0]:08x} cv6={cv[6]:08x}: {per_cv} pairs half-collide (words 0,2,5,7) "
              f"via organizer reference")
    print(f"total {ok} pairs OK over {ncv} chaining values")
    print(f"distinct C3 output tuples (Y3,Y7,Y11,Y15 of A and B) over all CVs: {len(c3_sets)} -> "
          + " ".join(f"{x:08x}" for x in next(iter(c3_sets))))
    print(f"distinct w5 differences over all CVs: {len(dw5_set)} -> {next(iter(dw5_set)):08x}")


if __name__ == "__main__":
    main()
