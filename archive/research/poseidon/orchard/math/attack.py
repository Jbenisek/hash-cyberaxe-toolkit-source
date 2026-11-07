from pos import *

def solve2(a, b, c, d, e, f):
    """solve a*U+b*V=e, c*U+d*V=f mod p"""
    det = (a * d - b * c) % p
    inv = pow(det, -1, p)
    return ((e * d - b * f) * inv) % p, ((a * f - e * c) * inv) % p

K = pow((CAP + RC[0][2]) % p, 5, p)

class Line:
    """line model for constant coordinate j of the round-1 S-box input"""
    def __init__(self, j):
        self.j = j
        I = [k for k in range(3) if k != j]
        self.I = I
        base = [(MDS[k][2] * K + RC[1][k]) % p for k in range(3)]   # x_k = M[k][0]U+M[k][1]V+base_k
        # point Q: x_i = 0 for i in I
        i1, i2 = I
        self.UQ, self.VQ = solve2(MDS[i1][0], MDS[i1][1], MDS[i2][0], MDS[i2][1], -base[i1] % p, -base[i2] % p)
        # direction (a,b) with d_j = 0
        self.a, self.b = MDS[j][1], (-MDS[j][0]) % p
        self.base = base
        self.d = [(MDS[k][0] * self.a + MDS[k][1] * self.b) % p for k in range(3)]
        self.xQ = [(MDS[k][0] * self.UQ + MDS[k][1] * self.VQ + base[k]) % p for k in range(3)]
        # S-box output affine: v0 + W*v1 , W = tau^5
        self.v0 = [pow(self.xQ[k], 5, p) if k == j else 0 for k in range(3)]
        self.v1 = [pow(self.d[k], 5, p) if k != j else 0 for k in range(3)]

    def UV(self, tau):
        return (self.UQ + tau * self.a) % p, (self.VQ + tau * self.b) % p

    def inputs(self, tau):
        """canonical (nk,rho) for line parameter tau (W = tau^5 bijective)"""
        U, V = self.UV(tau)
        nk = (pow(U, E5INV, p) - RC[0][0]) % p
        rho = (pow(V, E5INV, p) - RC[0][1]) % p
        return nk, rho

    def state_after_r1_sbox(self, W):
        return [(self.v0[k] + W * self.v1[k]) % p for k in range(3)]

    def F(self, W, r):
        s = mds(self.state_after_r1_sbox(W))
        for k in [2, 3] + list(range(4, 4 + r)) + [60, 61, 62, 63]:
            s = rnd(s, k, k < 4 or k >= 60)
        return s[0]
