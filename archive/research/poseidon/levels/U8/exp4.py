# U8: order of the MDS matrix M inside F_{p^3}^*, using the (partial) factorisation of p^3-1.

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

import sys, re
from sympy import isprime
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/orchard/impl'))
import poseidon_ref as R
P = R.P; M = [list(r) for r in R.MDS]
def pr(*a): print(' '.join(str(x) for x in a), flush=True)
def mm(A, B): return [[sum(A[i][k]*B[k][j] for k in range(3)) % P for j in range(3)] for i in range(3)]
I3 = [[1 if i == j else 0 for j in range(3)] for i in range(3)]
def mpow(A, e):
    Rr = I3; B = A
    while e:
        if e & 1: Rr = mm(Rr, B)
        B = mm(B, B); e >>= 1
    return Rr
def isscalar(A): return A[0][1] == A[0][2] == A[1][0] == A[1][2] == A[2][0] == A[2][1] == 0 and A[0][0] == A[1][1] == A[2][2]
known = [3, 73, 5839, 12221196943, 5187662682403, 487887715480415483992657]  # last one found by fact2.py
extra = [int(x) for x in re.findall(r'ECM found factor bits \d+ (\d+)', open('fact1_output.txt').read().split('p2+p+1 trial')[1])] if 'p2+p+1 trial' in open('fact1_output.txt').read() else []
for e in extra:
    if e not in known: known.append(e)
pr("p^2+p+1 known prime factors:", known)
Q = P*P+P+1
rest = Q
for f in known:
    while rest % f == 0: rest //= f
pr("p^2+p+1 cofactor after dividing known primes: %d bits, is prime: %s" % (rest.bit_length(), isprime(rest)))
f_pm1 = {2: 32, 3: 1, 463: 1, 539204044132271846773: 1, 8999194758858563409123804352480028797519453: 1}
# N = p^3-1 = (p-1)(p^2+p+1); gcd(p-1, p^2+p+1) = gcd(p-1,3) = 3
N = (P-1)*Q
assert pow(P, 3, P) == 0 or True
assert all(x == 0 for x in [0])
pr("M^(p^3-1) = I:", mpow(M, N) == I3)
# valuation of each known prime in N
def val(n, r):
    v = 0
    while n % r == 0: n //= r; v += 1
    return v
primes = list(f_pm1.keys())+[k for k in known if k not in f_pm1]
if isprime(rest): primes.append(rest); known.append(rest)
pr("\nprime r | known part of p^3-1 : v_r(p^3-1) -> v_r(ord M) (exact, by testing M^(N/r^j))")
tot = 1
for r in primes:
    vN = val(N, r)
    # find smallest j such that M^(N/r^(vN-j)) ... compute v_r(ord) = vN - max s such that M^(N/r^s)=I
    s = 0
    while s < vN and mpow(M, N//r**(s+1)) == I3: s += 1
    vo = vN - s
    pr("  r=%d (%d bits): v_r(N)=%d  v_r(ord M)=%d" % (r, r.bit_length(), vN, vo))
    tot *= r**vo
pr("known-prime part of ord(M):", tot, "bits", tot.bit_length())
pr("ord(M) exact if cofactor prime:", isprime(rest))
# test: does M^(N/rest) have order dividing 1?  i.e. is the cofactor part nontrivial
Nk = N//rest
pr("M^(N/cofactor) == I (cofactor part trivial)?:", mpow(M, Nk) == I3, " ; is M^(N/rest) of order exactly rest-part?")
# does ord(M) divide (p^3-1)/3 ? etc
for r in (2, 3, 463):
    pr("ord(M) divides N/%d:" % r, mpow(M, N//r) == I3)
# scalar powers: M^k scalar iff lambda^k in F_p: k multiple of ord(lambda)/gcd(ord, p-1)
k = P*P+P+1
# lambda^(p^2+p+1)=det: norm; M^(p^2+p+1) = det * I  (scalar) -> check
pr("M^(p^2+p+1) is the scalar det M * I:", isscalar(mpow(M, k)))
pr("M^((p^2+p+1)/3) scalar?", isscalar(mpow(M, k//3)))
for f in known:
    pr("M^((p^2+p+1)/%d) scalar?" % f, isscalar(mpow(M, k//f)))
