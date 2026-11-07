
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

import sys, os, json, random
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/orchard/impl'))
import poseidon_ref as PR
P = PR.P; MDS = [list(r) for r in PR.MDS]; RC = PR.RC
def inv(a, p=P): return pow(a, -1, p)
def matmul(A, B, p=P):
    return [[sum(A[i][k]*B[k][j] for k in range(3)) % p for j in range(3)] for i in range(3)]
def matvec(A, v, p=P): return [sum(A[i][k]*v[k] for k in range(3)) % p for i in range(3)]
def det3(A, p=P):
    return (A[0][0]*(A[1][1]*A[2][2]-A[1][2]*A[2][1]) - A[0][1]*(A[1][0]*A[2][2]-A[1][2]*A[2][0]) + A[0][2]*(A[1][0]*A[2][1]-A[1][1]*A[2][0])) % p
def minors2(A, p=P):
    out = []
    for i in range(3):
        for j in range(3):
            r = [k for k in range(3) if k != i]; c = [k for k in range(3) if k != j]
            out.append((A[r[0]][c[0]]*A[r[1]][c[1]] - A[r[0]][c[1]]*A[r[1]][c[0]]) % p)
    return out
def matinv(A, p=P):
    d = inv(det3(A, p), p)
    cof = [[0]*3 for _ in range(3)]
    for i in range(3):
        for j in range(3):
            r = [k for k in range(3) if k != i]; c = [k for k in range(3) if k != j]
            m = (A[r[0]][c[0]]*A[r[1]][c[1]] - A[r[0]][c[1]]*A[r[1]][c[0]]) % p
            cof[i][j] = m if (i+j) % 2 == 0 else (-m) % p
    return [[cof[j][i]*d % p for j in range(3)] for i in range(3)]
def is_mds(A, p=P):
    return all(x % p for r in A for x in r) and all(minors2(A, p)) and det3(A, p) != 0
def legendre(a, p=P):
    a %= p
    if a == 0: return 0
    return 1 if pow(a, (p-1)//2, p) == 1 else -1
def charpoly(A, p=P):
    T = (A[0][0]+A[1][1]+A[2][2]) % p
    S = sum(minors2(A, p)[i] for i in (0, 4, 8)) % p
    return T, S, det3(A, p)
# F_{p^3} = F_p[x]/(x^3 - T x^2 + S x - D)
class F3:
    def __init__(self, T, S, D, p=P):
        self.T, self.S, self.D, self.p = T, S, D, p
    def mul(self, a, b):
        p = self.p
        c = [0]*5
        for i in range(3):
            for j in range(3):
                c[i+j] += a[i]*b[j]
        # x^3 = T x^2 - S x + D ; x^4 = T x^3 - S x^2 + D x
        T, S, D = self.T, self.S, self.D
        c3, c4 = c[3], c[4]
        # x^4 -> T x^3 - S x^2 + D x
        c3 += T*c4; c[2] += -S*c4; c[1] += D*c4
        c[2] += T*c3; c[1] += -S*c3; c[0] += D*c3
        return ((c[0]) % p, (c[1]) % p, (c[2]) % p)
    def add(self, a, b): return tuple((x+y) % self.p for x, y in zip(a, b))
    def sub(self, a, b): return tuple((x-y) % self.p for x, y in zip(a, b))
    def smul(self, s, a): return tuple(s*x % self.p for x in a)
    def one(self): return (1, 0, 0)
    def pw(self, a, e):
        r = self.one()
        if e < 0: a = self.inv(a); e = -e
        while e:
            if e & 1: r = self.mul(r, a)
            a = self.mul(a, a); e >>= 1
        return r
    def frob(self, a): return self.pw(a, self.p)
    def norm(self, a):
        f1 = self.frob(a); f2 = self.frob(f1)
        return self.mul(a, self.mul(f1, f2))[0]
    def trace(self, a):
        f1 = self.frob(a); f2 = self.frob(f1)
        return (a[0]+f1[0]+f2[0]) % self.p
    def inv(self, a):
        # a^(-1) = a^(p+p^2) / N(a)
        f1 = self.frob(a); f2 = self.frob(f1)
        n = self.mul(a, self.mul(f1, f2))[0]
        t = self.mul(f1, f2)
        return self.smul(pow(n, -1, self.p), t)
