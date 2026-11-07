"""Extra small MDS facts: are powers of M still MDS (all minors nonzero)? structure of N=1/M entries; Krylov data."""

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

import sys
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/orchard/impl'))
import poseidon_ref as R
P, M = R.P, [list(r) for r in R.MDS]
def mm(A, B): return [[sum(A[i][k]*B[k][j] for k in range(3)) % P for j in range(3)] for i in range(3)]
def d2(a, b, c, d): return (a*d-b*c) % P
def det3(m): return (m[0][0]*d2(m[1][1], m[1][2], m[2][1], m[2][2]) - m[0][1]*d2(m[1][0], m[1][2], m[2][0], m[2][2]) + m[0][2]*d2(m[1][0], m[1][1], m[2][0], m[2][1])) % P
def is_mds(A):
    return all(x for r in A for x in r) and all(d2(A[a][c], A[a][d], A[b][c], A[b][d]) for a in range(3) for b in range(a+1, 3) for c in range(3) for d in range(c+1, 3)) and det3(A) != 0
Mk = M
for k in range(1, 9):
    print('M^%d is MDS (all 1x1,2x2,3x3 minors nonzero): %s' % (k, is_mds(Mk))); Mk = mm(Mk, M)
# inverse powers
def inv3(m):
    di = pow(det3(m), -1, P)
    cof = [[((-1)**(i+j)*d2(*[m[a][b] for a in range(3) if a != i for b in range(3) if b != j])) % P for j in range(3)] for i in range(3)]
    return [[cof[j][i]*di % P for j in range(3)] for i in range(3)]
Mi = inv3(M)
print('M^-1 is MDS:', is_mds(Mi))
# Krylov of e0 under M^T (rows): e0, e0 M, e0 M^2 -- independent => lane 0 observable through 3 rounds
r0 = [1, 0, 0]; r1 = M[0]; r2 = mm(M, M)[0]
print('det of [e0; e0 M; e0 M^2] (partial-round observability, nonzero => no invariant subspace trail of dim>0 for r>=3):', hex(det3([r0, r1, r2])))
# column Krylov: M e0 etc (first column), controllability from lane 0 S-box
c0 = [M[i][0] for i in range(3)]; c1 = [sum(M[i][j]*c0[j] for j in range(3)) % P for i in range(3)]; c2 = [sum(M[i][j]*c1[j] for j in range(3)) % P for i in range(3)]
print('det of [M e0, M^2 e0, M^3 e0] (does the S-box of lane 0 reach all directions in 3 rounds?):', hex(det3([[c0[i], c1[i], c2[i]] for i in range(3)])))
# structure of 1/M entries: N_ij = x_i + y_j
N = [[pow(M[i][j], -1, P) for j in range(3)] for i in range(3)]
print('1/M_ij bit lengths:', [[n.bit_length() for n in r] for r in N])
print('signed small? min(|N|,p-|N|) bit lengths:', [[min(n, P-n).bit_length() for n in r] for r in N])
print('differences N_i1-N_i0 are the same for all i (Cauchy y-differences):', len({(N[i][1]-N[i][0]) % P for i in range(3)}) == 1, len({(N[i][2]-N[i][0]) % P for i in range(3)}) == 1)
print('det(M) quadratic residue?', pow(det3(M), (P-1)//2, P) == 1)
# ---- relation of the round-0 plane P0 to the partial-round difference spaces
print('\n--- plane P0 (state after round 0) versus partial-round difference spaces ---')
n2 = Mi[2]   # normal of P0: direction space of P0 = {d : n2 . d = 0}
# difference space of P0 intersect {d0 = 0}: d=(0,d1,d2), n2[1] d1 + n2[2] d2 = 0
dd = [0, n2[2], (-n2[1]) % P]
print('P0-direction vectors with d0=0 (the S-box of R4 sees no difference): span of', [hex(x) for x in dd], ' (1-dim: the plane meets {d0=0} in a line)')
# is the r=2 trail vector (d0=0, (Md)_0=0) in P0's direction space?
d2v = [0, M[0][2], (-M[0][1]) % P]
print('r=2 trail vector d2v . n2 =', hex(sum(n2[j]*d2v[j] for j in range(3)) % P), '(nonzero => d2v is not a difference between two round-0 outputs)')
# the same quantities for round-1 input: states entering round 1 are on P0 (+c1 shift irrelevant for differences)
# Differences between two states of P0 that arrive at lane0-equal after R? only meaningful later.
# tracker: where do trail vectors go in M-coordinates
Md = [sum(M[i][j]*d2v[j] for j in range(3)) % P for i in range(3)]
print('M d2v has lane 0 = 0:', Md[0] == 0, '; lane 1,2 =', hex(Md[1])[:12], hex(Md[2])[:12])
