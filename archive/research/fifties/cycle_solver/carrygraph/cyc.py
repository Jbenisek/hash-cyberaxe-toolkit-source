'''The 21-equation cycle of split_e3 (design C0.b1, params P[0..13] as in split_e3/solve.cu), in two forms:
  ref(P, g)      straight transcription of solve.cu (returns the check word; root <=> 0)
  ADDS(P)        the same cycle as 9 modular additions over XOR/rotation operands (the carry-graph model):
                 each addition  Z = sum_k OP_k + CONST  (mod 2^32), OP_k = XOR of ROL(word, r) terms ^ xconst;
                 the last addition 'chk' must be 0.
Words: 'g' (the unknown) and the outputs of the additions.'''
M = 0xFFFFFFFF
def rol(x, n): n %= 32; return ((x << n) | (x >> (32 - n))) & M if n else x & M

def ref(P, g, full=False):
    Y8 = rol(P[11], 7) ^ g
    c1 = rol(g ^ rol(P[7], 20), 12)
    Y12 = (Y8 - c1) & M
    d1 = (c1 - P[9]) & M
    Y0 = rol(Y12, 8) ^ d1
    a1 = (Y0 - g - P[13]) & M
    X12 = rol(d1, 16) ^ a1
    Dc1 = (0x44036000 - X12) & M
    Dd1 = (Dc1 - P[2]) & M
    X1 = rol(X12, 8) ^ Dd1
    Da1 = rol(Dd1, 16) ^ P[3]
    w10 = (Da1 - P[1] - P[4]) & M
    w2 = (a1 - P[7] - P[5]) & M
    Ka1 = (0x566d1711 + w2) & M
    w3 = (P[1] - Ka1 - P[0]) & M
    C1a1 = (X1 + P[8] + w3) & M
    C1d1 = rol(P[6], 16) ^ rol(C1a1, 16)
    C1c1 = (P[10] + C1d1) & M
    C1b1 = rol(P[8], 20) ^ rol(C1c1, 20)
    Y1 = (C1a1 + C1b1 + w10) & M
    Y13 = rol(C1d1, 24) ^ rol(Y1, 24)
    chk = (P[12] - C1c1 - Y13) & M
    if full:
        return dict(g=g, Y12=Y12, d1=d1, a1=a1, Dd1=Dd1, w10=w10, C1a1=C1a1, C1c1=C1c1, Y1=Y1, chk=chk)
    return chk

def ADDS(P):
    '''list of (name, [operand,...], const); operand = ([(word, rot), ...], xconst).  Order = a topological order.'''
    K5 = (1 + P[1] - P[0] - 0x566d1711 + P[7] + P[5] + P[8]) & M
    return [
        ('Y12',  [([('g', 0)], rol(P[11], 7)), ([('g', 12)], (~P[7]) & M)], 1),
        ('d1',   [([('g', 12)], P[7])], (-P[9]) & M),
        ('a1',   [([('Y12', 8), ('d1', 0)], 0), ([('g', 0)], M)], (1 - P[13]) & M),
        ('Dd1',  [([('d1', 16), ('a1', 0)], M)], (0x44036001 - P[2]) & M),
        ('w10',  [([('Dd1', 16)], P[3])], (-P[1] - P[4]) & M),
        ('C1a1', [([('d1', 24), ('a1', 8), ('Dd1', 0)], 0), ([('a1', 0)], M)], K5),
        ('C1c1', [([('C1a1', 16)], rol(P[6], 16))], P[10]),
        ('Y1',   [([('C1a1', 0)], 0), ([('C1c1', 20)], rol(P[8], 20)), ([('w10', 0)], 0)], 0),
        ('chk',  [([('C1c1', 0)], 0), ([('C1a1', 8), ('Y1', 24)], rol(P[6], 8))], (-P[12]) & M),
    ]

def eval_adds(P, g):
    v = {'g': g}
    for name, ops, c in ADDS(P):
        s = c
        for terms, xc in ops:
            x = xc
            for w, r in terms: x ^= rol(v[w], r)
            s += x
        v[name] = s & M
    return v

if __name__ == '__main__':
    import random
    rnd = random.Random(5)
    for _ in range(20000):
        P = [rnd.getrandbits(32) for _ in range(14)]; g = rnd.getrandbits(32)
        a = ref(P, g, True); b = eval_adds(P, g)
        a['chk'] = (-a['chk']) & M          # model's chk = C1c1 + Y13 - Y9 = -(solve.cu check); zero <=> zero
        assert all(a[k] == b[k] for k in a), (a, b)
    print('ADDS model == solve.cu transcription on 20000 random (P, g): OK')
