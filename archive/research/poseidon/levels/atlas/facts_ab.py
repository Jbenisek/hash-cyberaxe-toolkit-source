"""Round 0 is a reparametrisation: (nk,rho) -> (A,B) = ((nk+c00)^5, (rho+c01)^5) is a bijection of Fp^2.
Check (1) the hash equals H(A,B) = rounds 1.. applied to M*(A,B,K); (2) exact monomial counts of the lane polynomials in (A,B)
for rounds 1..3 (full triangle?); (3) total degree in (A,B) per round."""

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

import sys, time, random
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/orchard/impl'))
import poseidon_ref as R
P, RC, MDS, CAP = R.P, R.RC, R.MDS, R.CAPACITY
M = [list(r) for r in MDS]
random.seed(5)
D5 = pow(5, -1, P-1)
K = pow((CAP + RC[0][2]) % P, 5, P)
def H(A, B, r):
    s = [sum(M[i][j]*[A, B, K][j] for j in range(3)) % P for i in range(3)]
    for idx in list(range(1, 4)) + list(range(4, 4+r)) + list(range(60, 64)):
        full = idx < 4 or idx >= 60
        s = [(s[i]+RC[idx][i]) % P for i in range(3)]
        for i in (range(3) if full else range(1)): s[i] = pow(s[i], 5, P)
        s = [sum(M[i][j]*s[j] for j in range(3)) % P for i in range(3)]
    return s[0]
for r in (1, 2):
    ok = True
    for _ in range(20):
        nk, rho = random.randrange(P), random.randrange(P)
        A = pow((nk+RC[0][0]) % P, 5, P); B = pow((rho+RC[0][1]) % P, 5, P)
        ok &= H(A, B, r) == R.hash_reduced(nk, rho, r)
        # inverse direction: any (A,B) is hit by exactly one (nk,rho)
        nk2 = (pow(A, D5, P) - RC[0][0]) % P; rho2 = (pow(B, D5, P) - RC[0][1]) % P
        ok &= (nk2, rho2) == (nk, rho)
    log = print
    log('r=%d: hash_reduced(nk,rho) == H(A,B) with A=(nk+c00)^5, B=(rho+c01)^5 ; and fifth-root inversion returns (nk,rho): %s' % (r, ok))
# bivariate in (A,B)
def bmul(f, g):
    h = {}
    for (i1, j1), c1 in f.items():
        for (i2, j2), c2 in g.items():
            k = (i1+i2, j1+j2); h[k] = (h.get(k, 0)+c1*c2) % P
    return {k: c for k, c in h.items() if c}
def badd(f, g):
    h = dict(f)
    for k, c in g.items(): h[k] = (h.get(k, 0)+c) % P
    return {k: c for k, c in h.items() if c}
def bscal(f, s): return {k: c*s % P for k, c in f.items()}
def bpow5(f):
    f2 = bmul(f, f); f4 = bmul(f2, f2); return bmul(f4, f)
def bdeg(f): return max(i+j for i, j in f)
state = [badd(badd(bscal({(1, 0): 1}, M[i][0]), bscal({(0, 1): 1}, M[i][1])), {(0, 0): M[i][2]*K % P}) for i in range(3)]
print('after round 0 (in A,B): per-lane degree', [bdeg(s) for s in state], 'monomials', [len(s) for s in state], '(linear: M_i0 A + M_i1 B + M_i2 K)')
for idx in (1, 2, 3):
    t = time.time()
    state = [badd(s, {(0, 0): RC[idx][i]}) for i, s in enumerate(state)]
    state = [bpow5(s) for s in state]
    new = []
    for i in range(3):
        acc = {}
        for j in range(3): acc = badd(acc, bscal(state[j], M[i][j]))
        new.append(acc)
    state = new
    d = bdeg(state[0])
    print('round %d: degree in (A,B) = %d (=5^%d), monomials per lane %s, full triangle (d+1)(d+2)/2 = %d  (%.1fs)' % (idx, d, idx, [len(s) for s in state], (d+1)*(d+2)//2, time.time()-t))
print('conclusion: in (A,B) coordinates the lanes have total degree 5^k after round k (k>=1)  -> output degree 5^(8) for r=1, 5^(9) for r=2 (one level less than in (nk,rho))')
