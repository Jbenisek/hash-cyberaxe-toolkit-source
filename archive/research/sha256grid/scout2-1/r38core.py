# r38core.py - reduced SHA-256 and the 38-step characteristic of ePrint 2026/1120 (Li, Zhang, Li, Liu, Qian, Zhu,
# "Pushing Collision Attacks on SHA-2 to 39 Steps", CC BY), Tables 3-5, copied verbatim from the transcription in
# research/tools/build_pkg/scratch/pkgR38a/base/experiments/vt38.py (lines 10-107).  Scout2-1 research copy.
M = 0xffffffff
K = [0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,
     0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,
     0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,
     0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb]
R = 38
def ror(x, n): return ((x >> n) | (x << (32 - n))) & M
def S0(x): return ror(x, 2) ^ ror(x, 13) ^ ror(x, 22)
def S1(x): return ror(x, 6) ^ ror(x, 11) ^ ror(x, 25)
def s0(x): return ror(x, 7) ^ ror(x, 18) ^ (x >> 3)
def s1(x): return ror(x, 17) ^ ror(x, 19) ^ (x >> 10)
def CH(x, y, z): return (x & y) ^ (~x & z & M)
def MAJ(x, y, z): return (x & y) ^ (x & z) ^ (y & z)

def trace(cv, w16):
    A = {-1: cv[0], -2: cv[1], -3: cv[2], -4: cv[3]}; E = {-1: cv[4], -2: cv[5], -3: cv[6], -4: cv[7]}
    W = list(w16)
    for i in range(16, R): W.append((s1(W[i-2]) + W[i-7] + s0(W[i-15]) + W[i-16]) & M)
    for i in range(R):
        E[i] = (A[i-4] + E[i-4] + S1(E[i-1]) + CH(E[i-1], E[i-2], E[i-3]) + K[i] + W[i]) & M
        A[i] = (E[i] - A[i-4] + S0(A[i-1]) + MAJ(A[i-1], A[i-2], A[i-3])) & M
    return A, E, W

CHAR = dict(
 A={7:'=nu=============================',8:'=========n=====n====n======u====',11:'====================u=======un==',
    12:'=u===n====n======u===nu=======n=',13:'==n============n================',14:'====u=========nn========u==u====',
    15:'======n=u=======n===============',17:'==u============================='},
 E={5:'+++=============================',6:'+++=1====0==+1=====0+===1==1====',7:'uuu=0+1=11=0+00====1+===0==00=01',
    8:'100=u+010n=1nu01=01nu=00n11u1=01',9:'11000u1=n11u0000101101110=01u0uu',10:'==1010=01u00001u=010u=101==10111',
    11:'1=n000=0111100101unn00011+111u10',12:'01nuuu=110n111nu000100100+010u1n',13:'00110101110=000u00111nuu+nnnu1n1',
    14:'=010n0===00===1n=11+0100+1110001',15:'=1==1=1==0=1==11===+u011n1011=1=',16:'=u==10===n===+u1===n0=u=1==+====',
    17:'=0=====+00===+0=+==01=0=0==+====',18:'=0=====+01===n1=+==1==1===0u====',19:'==11===nn====1==n===010===11==0=',
    20:'==1====00====1==0==========1====',21:'==u====10=======1===10==========',22:'==0=============================',
    23:'==1============================='},
 W={7:'==n=============================',8:'=====u===u==========n===========',9:'==u=============================',
    10:'=====n=u=======n===n==n=n=n=u=u=',11:'============u======u=u==========',15:'=====u===n==========n===========',
    16:'==u=============================',23:'=====1=uu=====1=u=1=============',25:'==n============================='})
TWOBIT = [('A',14,15,0,'A',16,15),('A',14,23,0,'A',16,23),('A',14,25,0,'A',16,25),('A',15,4,0,'A',16,4),('A',15,7,0,'A',16,7),
    ('A',15,16,1,'A',16,16),('A',15,17,0,'A',16,17),('A',15,27,0,'A',16,27),('A',15,29,0,'A',16,29),('A',16,15,0,'A',17,15),
    ('A',16,23,0,'A',17,23),('A',16,25,0,'A',17,25),('A',17,9,0,'A',17,20),('A',17,6,0,'A',17,18),('A',17,8,0,'A',17,17),
    ('A',16,29,0,'A',18,29),('A',18,29,0,'A',19,29),('E',16,4,1,'E',16,23),('E',16,3,1,'E',16,8),('E',16,14,0,'E',16,28),
    ('E',16,4,0,'E',17,4),('E',16,18,0,'E',17,18),('E',18,0,1,'E',18,13),('E',17,15,0,'E',18,15),('E',17,24,0,'E',18,24),
    ('E',19,6,1,'E',19,19),('E',19,20,0,'E',19,2),('E',21,2,0,'E',21,16),('W',16,1,1,'W',16,12),('W',16,20,1,'W',16,27),
    ('W',16,8,0,'W',16,25),('W',16,14,0,'W',16,18),('W',16,4,1,'W',16,6),('W',16,22,1,'W',16,31),('W',23,0,1,'W',23,30),
    ('W',23,1,1,'W',23,31),('W',23,14,0,'W',23,21),('W',23,16,0,'W',23,25),('W',25,4,0,'W',25,6),('W',25,22,0,'W',25,31),
    ('W',25,20,0,'W',25,27)]
def _h(s): return [int(t, 16) for t in s.split()]
PCV = _h('cd278980 1b12a052 b87cc8a6 a9e059c5 c9c3db85 6ca4b5b5 63d13ac1 c0329f1e')
PMY = _h('48fc271b 9fca20cd cc89f96f fc40396f 8b328cb4 6b91ef78 97f9b767 e2450045 3b016f58 de9804cb 66a99ea5 0ce30b8d a28cd15a 77a1e994 d28e48a0 9b5f6dbb')
PMX = _h('48fc271b 9fca20cd cc89f96f fc40396f 8b328cb4 6b91ef78 97f9b767 c2450045 3f416758 fe9804cb 63a88c0f 0ceb1f8d a28cd15a 77a1e994 d28e48a0 9f1f65bb')

def cell(s):
    m = v = d = p = 0
    for c, y in enumerate(s):
        b = 31 - c
        if y in '01un': m |= 1 << b
        if y in '1u': v |= 1 << b
        if y in 'un': d |= 1 << b
        if y == '+': p |= 1 << b
    return m, v, d, p
CELL = {k: [cell(CHAR[k].get(i, '=' * 32)) for i in range(R)] for k in 'AEW'}
PLUS = [0] + [CELL['E'][i][3] & CELL['E'][i-1][3] for i in range(1, R)]
XROW = {}
for c in TWOBIT: XROW.setdefault(max(c[1], c[5]), []).append(c)

def rowok(tx, ty, i, wcell=True):
    (Ax, Ex, Wx), (Ay, Ey, Wy) = tx, ty
    for k, x, y in (('A', Ax[i], Ay[i]), ('E', Ex[i], Ey[i])) + ((('W', Wx[i], Wy[i]),) if wcell else ()):
        m, v, d, _ = CELL[k][i]
        if x & m != v or x ^ y != d: return False
    if (Ex[i] ^ Ex[i-1]) & PLUS[i]: return False
    V = {'A': Ax, 'E': Ex, 'W': Wx}
    for k1, i1, b1, ne, k2, i2, b2 in XROW.get(i, ()):
        if ((V[k1][i1] >> b1) ^ (V[k2][i2] >> b2)) & 1 != ne: return False
    return True

TX = trace(PCV, PMX); TY = trace(PCV, PMY)

# ---- dense-part functions (scout2-1) -------------------------------------------------------------------------
def Pf(A, E):  # E16 - K16 - W16 = A12 + E12 + S1(E15) + CH(E15, E14, E13)  (CV-free part of row 16)
    return (A[12] + E[12] + S1(E[15]) + CH(E[15], E[14], E[13])) & M
def Rf(A):     # A16 - E16 + A12 = S0(A15) + MAJ(A15, A14, A13)
    return (S0(A[15]) + MAJ(A[15], A[14], A[13])) & M
def md(x, y): return (x - y) & M   # member x minus member y
# CV-free reference differences of the published pair (x minus y)
REF = dict(
    s0W8=md(s0(TX[2][8]), s0(TY[2][8])), s0W9=md(s0(TX[2][9]), s0(TY[2][9])), s0W10=md(s0(TX[2][10]), s0(TY[2][10])),
    s0W11=md(s0(TX[2][11]), s0(TY[2][11])), s1W15=md(s1(TX[2][15]), s1(TY[2][15])), s0W15=md(s0(TX[2][15]), s0(TY[2][15])),
    P=md(Pf(TX[0], TX[1]), Pf(TY[0], TY[1])), R=md(Rf(TX[0]), Rf(TY[0])),
    dW16=md(TX[2][16], TY[2][16]), dW17=md(TX[2][17], TY[2][17]))

def dense_from_A(Ax):
    """Member x A0..A15 -> both members' (A, E4..E15, W8..W15) via the Table-3 XOR differences."""
    out = []
    for mem in (0, 1):
        A = {i: Ax[i] ^ (CELL['A'][i][2] if mem else 0) for i in range(16)}
        E = {}
        for i in range(4, 16): E[i] = (A[i] + A[i-4] - S0(A[i-1]) - MAJ(A[i-1], A[i-2], A[i-3])) & M
        W = {}
        for i in range(8, 16): W[i] = (E[i] - A[i-4] - E[i-4] - S1(E[i-1]) - CH(E[i-1], E[i-2], E[i-3]) - K[i]) & M
        out.append((A, E, W))
    return out

def dense_checks(X, Y):
    """Every CV-free Step-1 condition on a dense part (rows 4..15 cells, '+' pairs, W8..W15 cells, the s0/s1
    expansion differences and the row-16 modular differences).  Returns the list of failures (empty = valid)."""
    (Ax, Ex, Wx), (Ay, Ey, Wy) = X, Y
    bad = []
    for i in range(4, 16):
        for k, x, y in (('A', Ax[i], Ay[i]), ('E', Ex[i], Ey[i])) + ((('W', Wx[i], Wy[i]),) if i >= 8 else ()):
            m, v, d, _ = CELL[k][i]
            if x & m != v: bad.append('%s%d value' % (k, i))
            if x ^ y != d: bad.append('%s%d xor' % (k, i))
        if i >= 5 and (Ex[i] ^ Ex[i-1]) & PLUS[i]: bad.append('plus%d' % i)
    for i in (8, 9, 10, 11):
        if md(s0(Wx[i]), s0(Wy[i])) != REF['s0W%d' % i]: bad.append('s0W%d' % i)
    if md(s1(Wx[15]), s1(Wy[15])) != REF['s1W15']: bad.append('s1W15')
    if md(s0(Wx[15]), s0(Wy[15])) != REF['s0W15']: bad.append('s0W15')
    if md(Pf(Ax, Ex), Pf(Ay, Ey)) != REF['P']: bad.append('dE16')
    if md(Rf(Ax), Rf(Ay)) != REF['R']: bad.append('dA16')
    return bad

def step2_words(cv, A, E):
    A = dict(A); E = dict(E)
    for j in range(4): A[-1-j] = cv[j]; E[-1-j] = cv[4+j]
    for i in range(4): E[i] = (A[i] + A[i-4] - S0(A[i-1]) - MAJ(A[i-1], A[i-2], A[i-3])) & M
    return [(E[i] - A[i-4] - E[i-4] - S1(E[i-1]) - CH(E[i-1], E[i-2], E[i-3]) - K[i]) & M for i in range(8)]

def end_to_end(X, Y, cv):
    """Connect cv through Step-2 words, run both members 38 steps, return (rows 0..15 all hold with W cells from
    row 8, W0..W6 equal, dW16, dW17)."""
    wx = step2_words(cv, X[0], X[1]) + [X[2][i] for i in range(8, 16)]
    wy = step2_words(cv, Y[0], Y[1]) + [Y[2][i] for i in range(8, 16)]
    tx = trace(cv, wx); ty = trace(cv, wy)
    ok = all(rowok(tx, ty, i, wcell=(i >= 8)) for i in range(0, 16))
    same = all(wx[i] == wy[i] for i in range(7))
    return ok, same, md(tx[2][16], ty[2][16]), md(tx[2][17], ty[2][17]), (tx, ty, wx, wy)
