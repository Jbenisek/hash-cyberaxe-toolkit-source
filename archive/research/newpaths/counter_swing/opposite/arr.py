"""arr.py: the counter arrangement on real 32-bit words, copied from counter\\structure\\arrange_check.py
(functions outer, inner, sub_member; constants unchanged) so that this folder is self-contained.
The referee is blake3_ref.py (a byte-identical copy of hash-smash\\verifier\\blake3.py).
"""
import struct
import sys

sys.dont_write_bytecode = True
import b3own_copy as O
import blake3_ref as V

M = 0xFFFFFFFF
IV = O.IV
ror, rol = O.ror, O.rol
X3, X7, X11, X15 = 0x29D4FA98, 0xBEE3AF28, 0x44036000, 0x40C58500
W4, W13 = 0x97475638, 0x0007C006
KK = (IV[2] + IV[6]) & M
W4B = ((((KK + W4) & M) ^ 8) - KK) & M
DELTA = (W4 - W4B) & M
FLAGS = 3
Y3A, _, Y11A, _ = O.G(X3, X7, X11, X15, W4, W13)
Y3B, _, Y11B, _ = O.G(X3, X7, X11, X15, W4B, W13)
CUBE_MASK, CUBE_VAL = 0x0E09818B, 0x02008000
SUB_MASK, SUB_VAL = 0x07EF8303, 0x030C0303
FREE_CUBE = [i for i in range(32) if not CUBE_MASK >> i & 1]


def sub_member(rng):
    e1 = SUB_VAL
    for i in range(32):
        if not SUB_MASK >> i & 1:
            e1 |= rng.getrandbits(1) << i
    return (e1 - Y3A) & M


def outer(vc, vd, d3d1, S15, S9, w5, X2, y, T_HI=0):
    v = dict(vc=vc, vd=vd, y=y, X2=X2, S15=S15, S9=S9, w5=w5)
    K2a1 = (IV[2] + IV[6] + W4) & M; K2d1 = ror(55 ^ K2a1, 16); K2c1 = (IV[2] + K2d1) & M
    K2b1 = ror(IV[6] ^ K2c1, 12)
    S2 = (K2a1 + K2b1 + w5) & M; S14 = ror(K2d1 ^ S2, 8); S10 = (K2c1 + S14) & M; S6 = ror(K2b1 ^ S10, 7)
    D3a1 = rol(d3d1, 16) ^ S14; D3c1 = (S9 + d3d1) & M; D3b1 = (X3 - D3a1) & M
    S4 = rol(D3b1, 12) ^ D3c1; S3 = (D3a1 - S4) & M; X14 = ror(d3d1 ^ X3, 8); X9 = (D3c1 + X14) & M
    X4 = ror(D3b1 ^ X9, 7)
    K3d1 = rol(S15, 8) ^ S3; K3c1 = (IV[3] + K3d1) & M; K3b1 = ror(IV[7] ^ K3c1, 12)
    S11 = (K3c1 + S15) & M; S7 = ror(K3b1 ^ S11, 7); K3a1 = rol(K3d1, 16) ^ FLAGS
    w6 = (K3a1 - IV[3] - IV[7]) & M; w7 = (S3 - K3a1 - K3b1) & M
    X8 = (vc - vd) & M; C0b1 = ror(X4 ^ vc, 12)
    D2b1 = rol(X7, 7) ^ X8; D2c1 = rol(D2b1, 12) ^ S7; X13 = (X8 - D2c1) & M
    D2a1 = (X2 - D2b1 - W13) & M; D2d1 = rol(X13, 8) ^ X2; S13 = rol(D2d1, 16) ^ D2a1
    S8 = (D2c1 - D2d1) & M; w12 = (D2a1 - S2 - S7) & M
    K1c1 = (S9 - S13) & M; K1d1 = (K1c1 - IV[1]) & M; K1a1 = rol(K1d1, 16) ^ T_HI
    K1b1 = ror(IV[5] ^ K1c1, 12); S1 = rol(S13, 8) ^ K1d1; S5 = ror(K1b1 ^ S9, 7)
    w2 = (K1a1 - IV[1] - IV[5]) & M; w3 = (S1 - K1a1 - K1b1) & M
    K0b1 = rol(S4, 7) ^ S8; K0c1 = rol(K0b1, 12) ^ IV[4]; K0d1 = (K0c1 - IV[0]) & M
    S12 = (S8 - K0c1) & M; S0 = rol(S12, 8) ^ K0d1
    Y8 = rol(y, 7) ^ C0b1; Y12 = (Y8 - vc) & M; Y0 = rol(Y12, 8) ^ vd; C0a1 = (Y0 - C0b1 - w6) & M
    X12 = rol(vd, 16) ^ C0a1
    D1c1 = (X11 - X12) & M; D1b1 = ror(S6 ^ D1c1, 12); X6 = ror(D1b1 ^ X11, 7); D1d1 = (D1c1 - S11) & M
    X1 = rol(X12, 8) ^ D1d1
    X0 = (C0a1 - X4 - w2) & M
    D0d1 = rol(X15, 8) ^ X0; D0c1 = (S10 + D0d1) & M; X10 = (D0c1 + X15) & M; D0b1 = ror(S5 ^ D0c1, 12)
    X5 = ror(D0b1 ^ X10, 7); D0a1 = rol(D0d1, 16) ^ S15; w8 = (D0a1 - S0 - S5) & M
    w9 = (X0 - D0a1 - D0b1) & M
    D1a1 = rol(D1d1, 16) ^ S12; w10 = (D1a1 - S1 - S6) & M; w11 = (X1 - D1a1 - D1b1) & M
    Y1, Y5, Y9, Y13 = O.G(X1, X5, X9, X13, w3, w10)
    C2a1 = (X2 + X6 + w7) & M; C2d1 = ror(X14 ^ C2a1, 16); C2c1 = (X10 + C2d1) & M
    C2b1 = ror(X6 ^ C2c1, 12)
    loc = dict(locals())
    for k, val in loc.items():
        if k not in v and isinstance(val, int):
            v[k] = val
    return v


def inner(o, d1):
    a1 = rol(d1, 16) ^ o['Y12']
    Y6 = (a1 - o['Y1'] - o['w12']) & M
    Y10 = rol(Y6, 7) ^ o['C2b1']
    Y14 = (Y10 - o['C2c1']) & M
    Y2 = rol(Y14, 8) ^ o['C2d1']
    w0 = (Y2 - o['C2a1'] - o['C2b1']) & M
    K0a1 = (IV[0] + IV[4] + w0) & M
    t = rol(o['K0d1'], 16) ^ K0a1
    w1 = (o['S0'] - K0a1 - o['K0b1']) & M
    words = [w0, w1, o['w2'], o['w3'], W4, o['w5'], o['w6'], o['w7'], o['w8'], o['w9'], o['w10'],
             o['w11'], o['w12'], W13, 0, 0]
    return dict(E1a1=a1, Y6=Y6, Y10=Y10, Y14=Y14, Y2=Y2, w0=w0, K0a1=K0a1, t=t, w1=w1), words


def words_b(words):
    wb = list(words); wb[4] = W4B; wb[5] = (words[5] + DELTA) & M
    return wb


def draw_c1(rng):
    c1 = CUBE_VAL
    for i in FREE_CUBE:
        c1 |= rng.getrandbits(1) << i
    return c1


def random_outer(rng, T_HI=0):
    return outer(*[rng.getrandbits(32) for _ in range(7)], sub_member(rng), T_HI=T_HI)


def trial(rng, o=None):
    """One trial: returns (o, ii, wordsA, wordsB, t, blockA bytes (55), blockB bytes (63))."""
    if o is None:
        o = random_outer(rng)
    d1 = (draw_c1(rng) - Y11A) & M
    ii, w = inner(o, d1)
    wb = words_b(w)
    A = struct.pack('<16I', *w)[:55]
    B = struct.pack('<16I', *wb)[:63]
    return o, ii, w, wb, ii['t'], A, B


def cv_last(block, t, rounds=2):
    """Organizer: CV of a one-block last chunk at counter t (non-root, flags 3)."""
    out = V._chunk_output(block, t, rounds)
    return V._compress(*out, rounds)[:8], out
