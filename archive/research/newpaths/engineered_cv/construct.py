r"""Generalised free-half construction (census folder; research only).

Rewritten from counter\structure\arrange_check.py (itself from proof.md section 4) with every constant made a
parameter, so one code path builds every variant of the census:
  cv      : the 8 chaining-value words of the colliding compression (IV for a first block, a chained CV otherwise)
  lenA    : block length of message A (the shorter one); lenB: block length of message B
  flags   : v15 of the colliding compression (11 root single block, 10 root last block of a multi-block chunk,
            3 non-root single-block last chunk, 2 non-root last block of a multi-block chunk)
  t_hi    : v13 (constant)
  t_lo    : v12; either a constant ('const' mode) or solved per trial ('solve' mode, the counter lever)
  pin     : (X3, X7, X11, X15, W4, W13) of any pinned call; moved to the pair (lenA, lenB) and to the chaining value
            by the TRANSFER rule (X3 - s, W4 + s), which keeps X3 + X7 + w4 and so the pinned call itself.
Indices: v8..v11 are always IV0..IV3 (BLAKE3), v0..v7 are cv.  Messages: A carries w4A, B carries w4B,
w5B = w5A + (w4A - w4B); all other words shared; w14 = w15 = 0; W13 pinned.
"""
import struct
import b3own as O

M = 0xFFFFFFFF
IV = O.IV
ror, rol = O.ror, O.rol


def pin_orient(pin):
    """Return (u, u2, d) with C3(u) and C3(u2) equal on outputs b and d, u - u2 = d; None if not a pin."""
    X3, X7, X11, X15, W4, W13 = pin
    A = O.G(X3, X7, X11, X15, W4, W13)
    best = None
    for dd in range(1, 1 << 7):           # |delta| <= 127 covers every pin used
        for d in (dd, (-dd) & M):
            B = O.G(X3, X7, X11, X15, (W4 - d) & M, W13)
            if A[1] == B[1] and A[3] == B[3] and A != B:
                return W4, (W4 - d) & M, d
    return best


def deltas_of_x(x):
    """All values S - (S ^ x) mod 2^32 (sum over set bits i of x of +-2^i), with a bit pattern realising each."""
    bits = [i for i in range(32) if x >> i & 1]
    out = {}
    for mask in range(1 << len(bits)):
        s = 0; pat = 0
        for j, i in enumerate(bits):
            if mask >> j & 1:
                s += 1 << i; pat |= 1 << i
            else:
                s -= 1 << i
        out.setdefault(s & M, pat)
    return out


def transfer(pin, cv, lenA, lenB):
    """Move a pin to the lengths (lenA, lenB) and chaining value cv.  Returns dict or None if delta unreachable."""
    o = pin_orient(pin)
    if o is None:
        return None
    u, u2, d = o
    x = lenA ^ lenB
    KK = (cv[2] + cv[6]) & M
    dx = deltas_of_x(x)
    X3, X7, X11, X15, W4, W13 = pin
    for role, (ua, ub) in (('A=u', (u, u2)), ('A=u2', (u2, u))):
        need = (ua - ub) & M                      # w4A - w4B must equal this
        if need not in dx:
            continue
        pat = dx[need]
        # S = KK + w4A must carry pattern pat on the bits of x; other bits: keep those of KK + ua
        S = (((KK + ua) & M) & ~x | pat) & M
        w4A = (S - KK) & M
        s = (w4A - ua) & M
        w4B = (ub + s) & M
        assert ((KK + w4B) & M) == (S ^ x), 'length cancellation'
        return dict(X3=(X3 - s) & M, X7=X7, X11=X11, X15=X15, W4A=w4A, W4B=w4B, W13=W13, role=role,
                    delta=(w4A - w4B) & M, x=x)
    return None


def outer(P, cv, lenA, flags, t_hi, vc, vd, d3d1, S15, S9, w5, X2, y):
    """Outer step of the construction: everything except w0, w1 (and K0.a1), as proof.md section 4."""
    X3, X7, X11, X15, W4, W13 = P['X3'], P['X7'], P['X11'], P['X15'], P['W4A'], P['W13']
    v = {}
    K2a1 = (cv[2] + cv[6] + W4) & M; K2d1 = ror(lenA ^ K2a1, 16); K2c1 = (IV[2] + K2d1) & M
    K2b1 = ror(cv[6] ^ K2c1, 12)
    S2 = (K2a1 + K2b1 + w5) & M; S14 = ror(K2d1 ^ S2, 8); S10 = (K2c1 + S14) & M; S6 = ror(K2b1 ^ S10, 7)
    D3a1 = rol(d3d1, 16) ^ S14; D3c1 = (S9 + d3d1) & M; D3b1 = (X3 - D3a1) & M
    S4 = rol(D3b1, 12) ^ D3c1; S3 = (D3a1 - S4) & M; X14 = ror(d3d1 ^ X3, 8); X9 = (D3c1 + X14) & M
    X4 = ror(D3b1 ^ X9, 7)
    K3d1 = rol(S15, 8) ^ S3; K3c1 = (IV[3] + K3d1) & M; K3b1 = ror(cv[7] ^ K3c1, 12)
    S11 = (K3c1 + S15) & M; S7 = ror(K3b1 ^ S11, 7); K3a1 = rol(K3d1, 16) ^ flags
    w6 = (K3a1 - cv[3] - cv[7]) & M; w7 = (S3 - K3a1 - K3b1) & M
    X8 = (vc - vd) & M; C0b1 = ror(X4 ^ vc, 12)
    D2b1 = rol(X7, 7) ^ X8; D2c1 = rol(D2b1, 12) ^ S7; X13 = (X8 - D2c1) & M
    D2a1 = (X2 - D2b1 - W13) & M; D2d1 = rol(X13, 8) ^ X2; S13 = rol(D2d1, 16) ^ D2a1
    S8 = (D2c1 - D2d1) & M; w12 = (D2a1 - S2 - S7) & M
    K1c1 = (S9 - S13) & M; K1d1 = (K1c1 - IV[1]) & M; K1a1 = rol(K1d1, 16) ^ t_hi
    K1b1 = ror(cv[5] ^ K1c1, 12); S1 = rol(S13, 8) ^ K1d1; S5 = ror(K1b1 ^ S9, 7)
    w2 = (K1a1 - cv[1] - cv[5]) & M; w3 = (S1 - K1a1 - K1b1) & M
    K0b1 = rol(S4, 7) ^ S8; K0c1 = rol(K0b1, 12) ^ cv[4]; K0d1 = (K0c1 - IV[0]) & M
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
    for k, val in dict(locals()).items():
        if isinstance(val, int):
            v[k] = val
    return v


def words_of(P, o, w0, w1):
    wa = [w0, w1, o['w2'], o['w3'], P['W4A'], o['w5'], o['w6'], o['w7'], o['w8'], o['w9'], o['w10'],
          o['w11'], o['w12'], P['W13'], 0, 0]
    wb = list(wa); wb[4] = P['W4B']; wb[5] = (wa[5] + P['W4A'] - P['W4B']) & M
    return wa, wb


def inner_solve(P, o, cv, d1):
    """Counter lever: E1.d1 prescribed, t (v12) solved."""
    a1 = rol(d1, 16) ^ o['Y12']
    Y6 = (a1 - o['Y1'] - o['w12']) & M
    Y10 = rol(Y6, 7) ^ o['C2b1']
    Y14 = (Y10 - o['C2c1']) & M
    Y2 = rol(Y14, 8) ^ o['C2d1']
    w0 = (Y2 - o['C2a1'] - o['C2b1']) & M
    K0a1 = (cv[0] + cv[4] + w0) & M
    t = rol(o['K0d1'], 16) ^ K0a1
    w1 = (o['S0'] - K0a1 - o['K0b1']) & M
    wa, wb = words_of(P, o, w0, w1)
    return t, wa, wb


def inner_const(P, o, cv, t_lo):
    """Constant counter: K0.a1 follows from t, so w0 and w1 are outer-step words (one trial per outer step here)."""
    K0a1 = rol(o['K0d1'], 16) ^ t_lo
    w0 = (K0a1 - cv[0] - cv[4]) & M
    w1 = (o['S0'] - K0a1 - o['K0b1']) & M
    return words_of(P, o, w0, w1)


def block_bytes(words, blen):
    full = struct.pack('<16I', *words)
    return full[:blen], full[blen:] == bytes(64 - blen)
