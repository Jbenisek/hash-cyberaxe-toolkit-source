"""S8 skeptic check: the 55/63 family in the LAST block of a two-block message (CV = chained value, flags 10).
1. build_cv(cv, flags, ...) = fam55.build with every IV word of v0..v7 replaced by cv, flags by `flags`,
   and the pins re-expressed: X3' = X3 + delta, W4' = W4 - delta, delta = (cv2+cv6) - (IV2+IV6).
   Self-check: build_cv(IV, 11) == fam55.build.
2. For random first blocks: full messages B1||A (119 bytes) and B1||B (127 bytes) hashed by the organizer
   reference verifier/blake3.py at 2 rounds: digest words 0,2,5,7 must agree.
3. C3 outputs (Y3, Y7, Y11, Y15 on A and B) and the w5 difference must equal the single-block values.
4. The residual (digest XOR on words 1,3,4,6) must equal F(seven words; Y3A, Y3B, Y11A, Y11B, dw5) - one fixed
   function, the same for every CV.  Read-only use of fam55.py and verifier/blake3.py."""

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

import random, struct, sys
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/newpaths/sidepaths'))
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/hash-smash'))
import fam55
from fam55 import ror, rol, G, IV, PERM, M
from verifier.blake3 import blake3 as ref, _compress as ref_compress

X3, X7, X11, X15, W4, W13 = fam55.X3, fam55.X7, fam55.X11, fam55.X15, fam55.W4, fam55.W13
KIV = (IV[2] + IV[6]) & M


def build_cv(cv, flags, Cc1, Cd1, D3d1, S15, S9, w5, X2, y):
    K = (cv[2] + cv[6]) & M
    delta = (K - KIV) & M
    x3 = (X3 + delta) & M
    w4 = (W4 - delta) & M
    K2a1 = (cv[2] + cv[6] + w4) & M; K2d1 = ror(55 ^ K2a1, 16)
    K2c1 = (IV[2] + K2d1) & M; K2b1 = ror(cv[6] ^ K2c1, 12)          # v10 = IV2, v6 = cv6
    S2 = (K2a1 + K2b1 + w5) & M; S14 = ror(K2d1 ^ S2, 8)
    S10 = (K2c1 + S14) & M; S6 = ror(K2b1 ^ S10, 7)
    D3a1 = rol(D3d1, 16) ^ S14; D3c1 = (S9 + D3d1) & M
    D3b1 = (x3 - D3a1) & M; S4 = rol(D3b1, 12) ^ D3c1
    S3 = (D3a1 - S4) & M; X14 = ror(D3d1 ^ x3, 8)
    X9 = (D3c1 + X14) & M; X4 = ror(D3b1 ^ X9, 7)
    K3d1 = rol(S15, 8) ^ S3; K3c1 = (IV[3] + K3d1) & M                  # v11 = IV3
    K3b1 = ror(cv[7] ^ K3c1, 12); S11 = (K3c1 + S15) & M
    S7 = ror(K3b1 ^ S11, 7); K3a1 = rol(K3d1, 16) ^ flags               # v15 = flags
    w6 = (K3a1 - cv[3] - cv[7]) & M; w7 = (S3 - K3a1 - K3b1) & M
    X8 = (Cc1 - Cd1) & M; C0b1 = ror(X4 ^ Cc1, 12)
    D2b1 = rol(X7, 7) ^ X8; D2c1 = rol(D2b1, 12) ^ S7
    X13 = (X8 - D2c1) & M
    D2a1 = (X2 - D2b1 - W13) & M; D2d1 = rol(X13, 8) ^ X2
    S13 = rol(D2d1, 16) ^ D2a1; S8 = (D2c1 - D2d1) & M
    w12 = (D2a1 - S2 - S7) & M
    K1c1 = (S9 - S13) & M; K1d1 = (K1c1 - IV[1]) & M                   # v9 = IV1
    K1a1 = rol(K1d1, 16); K1b1 = ror(cv[5] ^ K1c1, 12)
    S1 = rol(S13, 8) ^ K1d1; S5 = ror(K1b1 ^ S9, 7)
    w2 = (K1a1 - cv[1] - cv[5]) & M; w3 = (S1 - K1a1 - K1b1) & M
    K0b1 = rol(S4, 7) ^ S8; K0c1 = rol(K0b1, 12) ^ cv[4]
    K0d1 = (K0c1 - IV[0]) & M; K0a1 = rol(K0d1, 16)                    # v8 = IV0
    S12 = (S8 - K0c1) & M; S0 = rol(S12, 8) ^ K0d1
    w0 = (K0a1 - cv[0] - cv[4]) & M; w1 = (S0 - K0a1 - K0b1) & M
    Y8 = rol(y, 7) ^ C0b1; Y12 = (Y8 - Cc1) & M
    Y0 = rol(Y12, 8) ^ Cd1; C0a1 = (Y0 - C0b1 - w6) & M
    X12 = rol(Cd1, 16) ^ C0a1
    D1c1 = (X11 - X12) & M; D1b1 = ror(S6 ^ D1c1, 12)
    X6 = ror(D1b1 ^ X11, 7); D1d1 = (D1c1 - S11) & M
    X1 = rol(X12, 8) ^ D1d1
    X0 = (C0a1 - X4 - w2) & M
    D0d1 = rol(X15, 8) ^ X0; D0c1 = (S10 + D0d1) & M
    X10 = (D0c1 + X15) & M; D0b1 = ror(S5 ^ D0c1, 12)
    X5 = ror(D0b1 ^ X10, 7); D0a1 = rol(D0d1, 16) ^ S15
    w8 = (D0a1 - S0 - S5) & M; w9 = (X0 - D0a1 - D0b1) & M
    D1a1 = rol(D1d1, 16) ^ S12; w10 = (D1a1 - S1 - S6) & M
    w11 = (X1 - D1a1 - D1b1) & M
    words = [w0, w1, w2, w3, w4, w5, w6, w7, w8, w9, w10, w11, w12, W13, 0, 0]
    w4b = (((K + w4) & M) ^ 8) - K & M
    other = list(words); other[4] = w4b; other[5] = (w5 + w4 - w4b) & M
    return words, other


def state(cv, w, n, flags):
    """state after round 1, plus Y (state after C0..C3) for inspection"""
    v = list(cv) + list(IV[:4]) + [0, 0, n, flags]
    s = list(w); Y = None
    for r in range(2):
        for k, (a, b, c, d) in enumerate(((0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15),
                                          (0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14))):
            v[a], v[b], v[c], v[d] = G(v[a], v[b], v[c], v[d], s[2 * k], s[2 * k + 1])
            if r == 1 and k == 3:
                Y = list(v)
        s = [s[p] for p in PERM]
    return v, Y


def seven_words(cv, w, flags):
    """E1: d1, b1, a2 on A; E3: Y4, Y9, w8, h1 on A."""
    _, Y = state(cv, w, 55, flags)
    a1 = (Y[1] + Y[6] + w[12]) & M; d1 = ror(Y[12] ^ a1, 16); c1 = (Y[11] + d1) & M; b1 = ror(Y[6] ^ c1, 12)
    a2 = (a1 + b1 + w[5]) & M
    e1 = (Y[3] + Y[4]) & M; h1 = ror(Y[14] ^ e1, 16)
    return d1, b1, a2, Y[4], Y[9], w[8], h1


def F(d1, b1, a2, Y4, Y9, w8, h1, Y3A, Y3B, Y11A, Y11B, dw5):
    """residual (XOR of digest words 1,3,4,6 between A and B) from the seven words and the constants only"""
    def e1side(Y11, b1v, a2v):
        c1 = (Y11 + d1) & M
        d2 = ror(d1 ^ a2v, 8); c2 = (c1 + d2) & M; b2 = ror(b1v ^ c2, 7)
        return a2v, b2, c2, d2
    c1A = (Y11A + d1) & M; Y6 = rol(b1, 12) ^ c1A
    c1B = (Y11B + d1) & M; b1B = ror(Y6 ^ c1B, 12)
    a2B = (a2 + b1B - b1 + dw5) & M
    EA = e1side(Y11A, b1, a2); EB = e1side(Y11B, b1B, a2B)
    e1A = (Y3A + Y4) & M; Y14 = rol(h1, 16) ^ e1A
    def e3side(Y3):
        e1 = (Y3 + Y4) & M; h = ror(Y14 ^ e1, 16); g1 = (Y9 + h) & M; f1 = ror(Y4 ^ g1, 12)
        e2 = (e1 + f1 + w8) & M; h2 = ror(h ^ e2, 8); g2 = (g1 + h2) & M; f2 = ror(f1 ^ g2, 7)
        return e2, f2, g2, h2
    TA = e3side(Y3A); TB = e3side(Y3B)
    oA = (EA[0] ^ TA[2], TA[0] ^ EA[2], TA[1] ^ EA[3], EA[1] ^ TA[3])
    oB = (EB[0] ^ TB[2], TB[0] ^ EB[2], TB[1] ^ EB[3], EB[1] ^ TB[3])
    return tuple(x ^ y for x, y in zip(oA, oB))


def main():
    rng = random.Random(20261008)
    # 1. self-check against fam55.build
    for _ in range(200):
        args = [rng.randrange(1 << 32) for _ in range(7)] + [fam55.class_member_sub(rng.randrange(1 << 17))]
        wa, _ = build_cv(IV, 11, *args)
        assert wa == fam55.build(*args)
    print("1. build_cv(IV, 11) == fam55.build on 200 random inputs: OK")
    # reference constants from the single-block family
    args = [rng.randrange(1 << 32) for _ in range(7)] + [fam55.class_member_sub(0)]
    wa, wb = build_cv(IV, 11, *args)
    _, YA = state(IV, wa, 55, 11); _, YB = state(IV, wb, 63, 11)
    ref_c3 = (YA[3], YB[3], YA[7], YB[7], YA[11], YB[11], YA[15], YB[15], (wb[5] - wa[5]) & M)
    print("   single block C3 outputs Y3A Y3B Y7A Y7B Y11A Y11B Y15A Y15B dw5:", " ".join(f"{x:08x}" for x in ref_c3))
    assert ref_c3[0] == fam55.Y3A and ref_c3[1] == fam55.Y3B and ref_c3[2] == ref_c3[3] and ref_c3[6] == ref_c3[7]
    assert (ref_c3[5] - ref_c3[4]) & M == 0x0a08818b
    Y3A, Y3B, Y11A, Y11B, dw5 = ref_c3[0], ref_c3[1], ref_c3[4], ref_c3[5], ref_c3[8]
    # 2-4. two-block messages with random first blocks
    n_cv, n_per = 40, 50
    hc = fmatch = c3same = 0
    for i in range(n_cv):
        B1 = bytes(rng.randrange(256) for _ in range(64))
        cv = ref_compress(IV, struct.unpack("<16I", B1), 0, 64, 1, 2)[:8]
        for _ in range(n_per):
            args = [rng.randrange(1 << 32) for _ in range(7)] + [fam55.class_member_sub(rng.randrange(1 << 17))]
            wa, wb = build_cv(cv, 10, *args)
            mA = B1 + struct.pack("<16I", *wa)[:55]; mB = B1 + struct.pack("<16I", *wb)[:63]
            assert len(mA) == 119 and len(mB) == 127 and mA != mB
            assert struct.pack("<16I", *wa)[55:] == bytes(9) and struct.pack("<16I", *wb)[63:] == bytes(1)
            dA = struct.unpack("<8I", ref(mA, 2)); dB = struct.unpack("<8I", ref(mB, 2))
            vA, YA = state(cv, wa, 55, 10); vB, YB = state(cv, wb, 63, 10)
            assert tuple(vA[k] ^ vA[k + 8] for k in range(8)) == dA     # own compression == reference
            if all(dA[k] == dB[k] for k in (0, 2, 5, 7)):
                hc += 1
            c3 = (YA[3], YB[3], YA[7], YB[7], YA[11], YB[11], YA[15], YB[15], (wb[5] - wa[5]) & M)
            if c3 == ref_c3 and YA[4] == args[7]:
                c3same += 1
            R = tuple(dA[k] ^ dB[k] for k in (1, 3, 4, 6))
            if F(*seven_words(cv, wa, 10), Y3A, Y3B, Y11A, Y11B, dw5) == R:
                fmatch += 1
    tot = n_cv * n_per
    print(f"2. two-block 119/127-byte pairs, {n_cv} random first blocks x {n_per}: half-collision on words 0,2,5,7 "
          f"(organizer reference, 2 rounds): {hc}/{tot}")
    print(f"3. C3 outputs and dw5 identical to the single-block values, Y4 = y: {c3same}/{tot}")
    print(f"4. residual == F(seven words; single-block constants): {fmatch}/{tot}")
    # same F check on single block
    ok = 0
    for _ in range(500):
        args = [rng.randrange(1 << 32) for _ in range(7)] + [fam55.class_member_sub(rng.randrange(1 << 17))]
        wa, wb = build_cv(IV, 11, *args)
        dA = struct.unpack("<8I", ref(struct.pack("<16I", *wa)[:55], 2))
        dB = struct.unpack("<8I", ref(struct.pack("<16I", *wb)[:63], 2))
        R = tuple(dA[k] ^ dB[k] for k in (1, 3, 4, 6))
        ok += F(*seven_words(IV, wa, 11), Y3A, Y3B, Y11A, Y11B, dw5) == R
    print(f"   single block control: residual == F: {ok}/500")


if __name__ == "__main__":
    main()
