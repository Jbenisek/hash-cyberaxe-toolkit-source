"""AV section 11 reference (pure Python): section 8.2 chart, AV-FRAME, 64-seed inverse.

Constants: present pin (X3, X7, X11, W13) and BLAKE3 IV as in the filed proof 3.2.
DFLAG is the K3 d-input XORed into K3.a1: AV 8.2 prints "XOR3"; the filed
construction has v15 = 11. Both are supported (dflag argument).
"""
M = 0xFFFFFFFF
IV = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
      0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19]
X3, X7, X11, W13 = 0x29d4fa98, 0xbee3af28, 0x44036000, 0x0007c006
Y3 = 0x8127c181
CL13 = (0x03cf8303, 0x030c0303)   # rank 13, |C| = 2^19
CL15 = (0x07ef8303, 0x030c0303)   # rank 15, |C| = 2^17
QS = (0x00000000, 0x80000000)


def rol(x, r):
    r %= 32
    return ((x << r) | (x >> (32 - r))) & M if r else x


def ror(x, r):
    return rol(x, 32 - (r % 32))


def in_class(y, cl):
    return ((Y3 + y) & M & cl[0]) == cl[1]


def b_of_q(q):
    return (q - W13) & M


def chart_consts(b, z, f, dflag=11):
    """Return D=X8, K=X11-S11, u=z+f (section 8.2 / 11.1)."""
    X8 = rol(X7, 7) ^ b
    S7 = X8 ^ rol(b, 12)
    a1 = (IV[3] + IV[7] + f) & M
    d1 = ror(a1 ^ dflag, 16)
    c1 = (IV[3] + d1) & M
    b1 = ror(IV[7] ^ c1, 12)
    S11 = rol(S7, 7) ^ b1
    return X8, (X11 - S11) & M, (z + f) & M


def y_forward(b, h, z, f, dflag=11):
    """Literal section 8.2 chain: C0.a1, Y0, Y12, y."""
    X8, K, _ = chart_consts(b, z, f, dflag)
    C0a1 = rol(h, 16) ^ K
    Y0 = (C0a1 + z + f) & M
    Y12 = ror(Y0 ^ h, 8)
    return ror(((Y12 + X8 + h) & M) ^ z, 7)


def V_of(y, z, D):
    return ((rol(y, 7) ^ z) - D) & M


def av_frame(h, K, u, V):
    return ((rol(h, 16) ^ K) + u) & M == (rol((V - h) & M, 8) ^ h)


def inverse(K, u, V):
    """11.2: guess c8,c16,c24,beta8,beta16,beta24; return list of (seed, h)."""
    bit = lambda x, i: (x >> (i % 32)) & 1
    out = []
    for s in range(64):
        c = [0, s & 1, (s >> 1) & 1, (s >> 2) & 1]        # carry into bit t+8j
        bb = [0, (s >> 3) & 1, (s >> 4) & 1, (s >> 5) & 1]  # borrow into bit t+8j
        h = 0
        for t in range(8):
            D = [0] * 4
            for j in range(4):
                i = t + 8 * j
                D[j] = bit(K, i) ^ bit(u, i) ^ c[j] ^ bit(V, i - 8) ^ bb[(j + 3) & 3]
            H = [D[j] ^ D[(j + 2) & 3] ^ D[(j + 1) & 3] for j in range(4)]
            nc, nb = [0] * 4, [0] * 4
            for j in range(4):
                i = t + 8 * j
                a = H[(j + 2) & 3] ^ bit(K, i)
                ui = bit(u, i)
                nc[j] = (a & ui) | (a & c[j]) | (ui & c[j])
                nv = bit(V, i) ^ 1
                nb[j] = (nv & H[j]) | (nv & bb[j]) | (H[j] & bb[j])
                h |= H[j] << i
            c, bb = nc, nb
        if (c[0], c[1], c[2]) == (s & 1, (s >> 1) & 1, (s >> 2) & 1) and \
           (bb[0], bb[1], bb[2]) == ((s >> 3) & 1, (s >> 4) & 1, (s >> 5) & 1):
            out.append((s, h))
    return out


def f_for_K0(b, dflag=11):
    """Physical subfamily of 11.2: S11 = X11 (K=0) via the unique f inverse at fixed b."""
    X8 = rol(X7, 7) ^ b
    S7 = X8 ^ rol(b, 12)
    b1 = rol(S7, 7) ^ X11
    c1 = rol(b1, 12) ^ IV[7]
    d1 = (c1 - IV[3]) & M
    a1 = rol(d1, 16) ^ dflag
    return (a1 - IV[3] - IV[7]) & M


if __name__ == "__main__":
    import random
    rnd = random.Random(1)
    # self-check: forward y satisfies AV-FRAME at its h and inverse finds it
    for _ in range(300):
        b = b_of_q(rnd.choice(QS)); h, z, f = (rnd.getrandbits(32) for _ in range(3))
        y = y_forward(b, h, z, f)
        D, K, u = chart_consts(b, z, f)
        V = V_of(y, z, D)
        assert av_frame(h, K, u, V)
        assert h in [r for _, r in inverse(K, u, V)]
    b = b_of_q(0); f = f_for_K0(b); z = (-f) & M
    D, K, u = chart_consts(b, z, f)
    assert K == 0 and u == 0
    print("ref self-check ok")
