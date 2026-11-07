"""U3 Q5/Q8: sparse equivalent partial rounds (real field). Single process."""

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

import sys, random
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/orchard/impl'))
from poseidon_ref import *
random.seed(77)
M = MDS
def rnd(): return random.randrange(P)
def inv(a): return pow(a, P-2, P)
def mv(A, v): return [sum(A[i][j]*v[j] for j in range(len(v))) % P for i in range(len(A))]
def mm(A, B): return [[sum(A[i][k]*B[k][j] for k in range(len(B))) % P for j in range(len(B[0]))] for i in range(len(A))]
def inv2(A):
    d = (A[0][0]*A[1][1]-A[0][1]*A[1][0]) % P; di = inv(d)
    return [[A[1][1]*di % P, (-A[0][1])*di % P],[(-A[1][0])*di % P, A[0][0]*di % P]]
def out(*a): print(*a); sys.stdout.flush()
def upto_R3(nk, rho):
    s = [nk, rho, CAPACITY]
    for i in range(4): s = round_full(s, i)
    return s
Mh = [[M[1][1], M[1][2]],[M[2][1], M[2][2]]]
dh = (Mh[0][0]*Mh[1][1]-Mh[0][1]*Mh[1][0]) % P
out("Mhat = lower-right 2x2 block of M; det =", hex(dh), "nonzero:", dh != 0, "(this is an MDS 2x2 minor)")
Mhi = inv2(Mh)
w = [M[1][0], M[2][0]]; v = [M[0][1], M[0][2]]; m00 = M[0][0]
def pw(A, k):
    R = [[1,0],[0,1]]
    for _ in range(k): R = mm(R, A)
    return R
def sparse_block(r):
    """A_k = Mhat^-(r-k+1), k=1..r; M_k = [[m00, v^T A_k],[A_{k+1}^-1 w, I]] ; A_{r+1}=I; hat c_k = (c_k0, A_k^-1 c_k12)."""
    A = {k: pw(Mhi, r-k+1) for k in range(1, r+1)}
    A[r+1] = [[1,0],[0,1]]
    Ainv = {k: inv2(A[k]) if k <= r else [[1,0],[0,1]] for k in A}
    mats = {}
    for k in range(1, r+1):
        row = [sum(v[i]*A[k][i][j] for i in range(2)) % P for j in range(2)]
        col = [sum(Ainv[k+1][i][j]*w[j] for j in range(2)) % P for i in range(2)]
        mats[k] = (m00, row, col)
    return A, Ainv, mats
def run_sparse(r, s, with_pushed_consts=False):
    A, Ainv, mats = sparse_block(r)
    # front: hat y0 = Q1^-1 y0 = (y0_0, A1^-1 y0_12)
    y = [s[0]] + mv(Ainv[1], s[1:])
    for k in range(1, r+1):
        idx = 3 + k
        c = RC[idx]; c12 = mv(Ainv[k], c[1:])
        t = [(y[0]+c[0]) % P, (y[1]+c12[0]) % P, (y[2]+c12[1]) % P]
        t[0] = pow(t[0], 5, P)
        m, row, col = mats[k]
        n0 = (m*t[0] + row[0]*t[1] + row[1]*t[2]) % P
        n1 = (t[1] + col[0]*t[0]) % P
        n2 = (t[2] + col[1]*t[0]) % P
        y = [n0, n1, n2]
    return y   # Q_{r+1}=I
for r in (1, 2, 3, 4):
    bad = 0
    for _ in range(300):
        nk, rho = rnd(), rnd()
        s = upto_R3(nk, rho)
        ref = list(s)
        for idx in range(4, 4+r): ref = round_partial(ref, idx)
        if run_sparse(r, s) != ref: bad += 1
    out("sparse equivalent partial block r=%d: mismatches %d/300 (random states after R3)" % (r, bad))
    # hash check
    bad = 0
    for _ in range(100):
        nk, rho = rnd(), rnd()
        s = run_sparse(r, upto_R3(nk, rho))
        for idx in range(60, 64): s = round_full(s, idx)
        if s[0] != hash_reduced(nk, rho, r): bad += 1
    out("  full hash through sparse block r=%d: mismatches %d/100" % (r, bad))
A, Ainv, mats = sparse_block(2)
for rr in (1, 2):
    A, Ainv, mats = sparse_block(rr)
    for k, (m, row, col) in mats.items():
        out("r=%d sparse matrix of partial round %d: m=%s row=(%s, %s) col=(%s, %s)" % (rr, k, hex(m), hex(row[0]), hex(row[1]), hex(col[0]), hex(col[1])))
        out("   special? any entry in {0,1,-1}: %s ; col0==col1: %s ; row0==row1: %s" % (any(x in (0,1,P-1) for x in (m,)+tuple(row)+tuple(col)), col[0]==col[1], row[0]==row[1]))
        out("   col ratio col1/col0 = %s" % hex(col[1]*inv(col[0]) % P))
# uniqueness freedom: Mhat^j w ratio and eigen-collinearity
out("w = M[1:,0] =", hex(w[0]), hex(w[1]))
mw = [sum(Mh[i][j]*w[j] for j in range(2)) % P for i in range(2)]
out("collinear(w, Mhat w) (w would be an eigenvector of Mhat):", (w[0]*mw[1]-w[1]*mw[0]) % P == 0)
# Mhat char poly discriminant -> eigenvalues in Fp?
tr = (Mh[0][0]+Mh[1][1]) % P; disc = (tr*tr-4*dh) % P
out("Mhat trace^2-4det is a square in Fp (eigenvalues of Mhat in Fp):", pow(disc, (P-1)//2, P) == 1)
# alternative M = M' M'' with M'=diag(1,Mhat), M''=[[m00,v],[Mhat^-1 w, I]]
Mp = [[1,0,0],[0,Mh[0][0],Mh[0][1]],[0,Mh[1][0],Mh[1][1]]]
mw2 = [sum(Mhi[i][j]*w[j] for j in range(2)) % P for i in range(2)]
Mpp = [[m00, v[0], v[1]],[mw2[0],1,0],[mw2[1],0,1]]
out("M == diag(1,Mhat) * [[m00,v],[Mhat^-1 w, I]] :", mm(Mp, Mpp) == [list(r) for r in M])
# multiplication counts
out("mult count per partial round (excluding constants additions): S-box 3 + dense M 9 = 12 ; sparse M: row0 3 + lanes1,2 2 = 5 -> 3+5 = 8 ; saved 4 per partial round")
out("r=1: dense 12 -> 8 (save 4) ; r=2: 24 -> 16 (save 8); front matrix Q1^-1*M(R3) stays dense 9 (no extra cost)")
