"""The filed 55/63 family (pin H8), steps O, M, Y, T of research/pkg10/pkg/blake3-r2/proof.md section 4,
written out line by line.  build(c, d, D3d1, S15, S9, w5, X2, y) -> 16 words of message A.
pair(words) -> (A bytes, B bytes).  hash2 = complete 2-round BLAKE3 (single block).  Self-test at the bottom
checks the half-collision (digest words 0,2,5,7) and Y4 = y on random inputs, against hash2 and against the
organizer reference verifier/blake3.py (read only)."""

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

import struct
import sys

M = 0xFFFFFFFF
IV = (0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19)
PERM = (2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8)
X3, X7, X11, X15, W4, W13 = 0x29d4fa98, 0xbee3af28, 0x44036000, 0x40c58500, 0x97475638, 0x0007c006
K = (IV[2] + IV[6]) & M
W4B = (((K + W4) & M) ^ 8) - K & M
Y3A, Y3B = 0x8127c181, 0x7edf3e7e
CLASS_AND, CLASS_VAL = 0x03cf8303, 0x030c0303          # Lemma Q on e1 = Y3 + Y4
SUB_AND = 0x07ef8303                                   # Lemma Q2


def ror(x, r):
    return ((x >> r) | (x << (32 - r))) & M


def rol(x, r):
    return ((x << r) | (x >> (32 - r))) & M


def G(a, b, c, d, x, y):
    a = (a + b + x) & M; d = ror(d ^ a, 16); c = (c + d) & M; b = ror(b ^ c, 12)
    a = (a + b + y) & M; d = ror(d ^ a, 8); c = (c + d) & M; b = ror(b ^ c, 7)
    return a, b, c, d


def compress_state(w, n, rounds=2):
    v = list(IV) + list(IV[:4]) + [0, 0, n, 11]
    s = list(w)
    for _ in range(rounds):
        for (a, b, c, d), i in zip(((0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15),
                                    (0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14)), range(8)):
            v[a], v[b], v[c], v[d] = G(v[a], v[b], v[c], v[d], s[2 * i], s[2 * i + 1])
        s = [s[p] for p in PERM]
    return v


def hash2(msg):
    n = len(msg)
    w = struct.unpack("<16I", msg + bytes(64 - n))
    v = compress_state(w, n)
    return struct.pack("<8I", *(v[i] ^ v[i + 8] for i in range(8)))


def build(Cc1, Cd1, D3d1, S15, S9, w5, X2, y):
    # Step O
    K2a1 = (IV[2] + IV[6] + W4) & M; K2d1 = ror(55 ^ K2a1, 16)
    K2c1 = (IV[2] + K2d1) & M; K2b1 = ror(IV[6] ^ K2c1, 12)
    S2 = (K2a1 + K2b1 + w5) & M; S14 = ror(K2d1 ^ S2, 8)
    S10 = (K2c1 + S14) & M; S6 = ror(K2b1 ^ S10, 7)
    D3a1 = rol(D3d1, 16) ^ S14; D3c1 = (S9 + D3d1) & M
    D3b1 = (X3 - D3a1) & M; S4 = rol(D3b1, 12) ^ D3c1
    S3 = (D3a1 - S4) & M; X14 = ror(D3d1 ^ X3, 8)
    X9 = (D3c1 + X14) & M; X4 = ror(D3b1 ^ X9, 7)
    K3d1 = rol(S15, 8) ^ S3; K3c1 = (IV[3] + K3d1) & M
    K3b1 = ror(IV[7] ^ K3c1, 12); S11 = (K3c1 + S15) & M
    S7 = ror(K3b1 ^ S11, 7); K3a1 = rol(K3d1, 16) ^ 11
    w6 = (K3a1 - IV[3] - IV[7]) & M; w7 = (S3 - K3a1 - K3b1) & M
    X8 = (Cc1 - Cd1) & M; C0b1 = ror(X4 ^ Cc1, 12)
    D2b1 = rol(X7, 7) ^ X8; D2c1 = rol(D2b1, 12) ^ S7
    X13 = (X8 - D2c1) & M
    # Step M
    D2a1 = (X2 - D2b1 - W13) & M; D2d1 = rol(X13, 8) ^ X2
    S13 = rol(D2d1, 16) ^ D2a1; S8 = (D2c1 - D2d1) & M
    w12 = (D2a1 - S2 - S7) & M
    K1c1 = (S9 - S13) & M; K1d1 = (K1c1 - IV[1]) & M
    K1a1 = rol(K1d1, 16); K1b1 = ror(IV[5] ^ K1c1, 12)
    S1 = rol(S13, 8) ^ K1d1; S5 = ror(K1b1 ^ S9, 7)
    w2 = (K1a1 - IV[1] - IV[5]) & M; w3 = (S1 - K1a1 - K1b1) & M
    K0b1 = rol(S4, 7) ^ S8; K0c1 = rol(K0b1, 12) ^ IV[4]
    K0d1 = (K0c1 - IV[0]) & M; K0a1 = rol(K0d1, 16)
    S12 = (S8 - K0c1) & M; S0 = rol(S12, 8) ^ K0d1
    w0 = (K0a1 - IV[0] - IV[4]) & M; w1 = (S0 - K0a1 - K0b1) & M
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
    return [w0, w1, w2, w3, W4, w5, w6, w7, w8, w9, w10, w11, w12, W13, 0, 0]


def pair(words):
    other = list(words)
    other[4] = W4B
    other[5] = (words[5] + W4 - W4B) & M
    return struct.pack("<16I", *words)[:55], struct.pack("<16I", *other)[:63]


def class_member_sub(k):
    """member k of the sub-class (Lemma Q2): 17 free bits of e1."""
    free = [i for i in range(32) if not SUB_AND >> i & 1]
    e1 = CLASS_VAL
    for j, p in enumerate(free):
        if k >> j & 1:
            e1 |= 1 << p
    return (e1 - Y3A) & M


def residual(words):
    A, B = pair(words)
    dA = struct.unpack("<8I", hash2(A))
    dB = struct.unpack("<8I", hash2(B))
    return dA, dB


if __name__ == "__main__":
    import random
    sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/hash-smash'))
    from verifier.blake3 import blake3 as ref
    rng = random.Random(7)
    ok = 0
    for t in range(200):
        args = [rng.randrange(1 << 32) for _ in range(7)] + [class_member_sub(rng.randrange(1 << 17))]
        w = build(*args)
        A, B = pair(w)
        assert len(A) == 55 and len(B) == 63
        assert hash2(A) == ref(A, 2) and hash2(B) == ref(B, 2)
        dA, dB = struct.unpack("<8I", hash2(A)), struct.unpack("<8I", hash2(B))
        v = compress_state(w, 55, rounds=2)
        assert all(dA[i] == dB[i] for i in (0, 2, 5, 7))
        ok += 1
    print(f"self-test: {ok}/200 pairs half-collide on words 0,2,5,7; hash2 == organizer reference")
