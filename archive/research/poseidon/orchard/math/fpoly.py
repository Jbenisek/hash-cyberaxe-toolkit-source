import time
from flint import fmpz_mod_poly_ctx, fmpz_mod_ctx
from attack import *
R = fmpz_mod_poly_ctx(p)
ZC = fmpz_mod_ctx(p)
X = R([0, 1])

def build_F(L, r):
    """F(W) as an fmpz_mod_poly, W = X"""
    s = [R([L.v0[k], L.v1[k]]) for k in range(3)]
    def mdsp(s):
        return [sum((s[j] * MDS[i][j] for j in range(3)), R([0])) for i in range(3)]
    s = mdsp(s)
    for k in [2, 3] + list(range(4, 4 + r)) + [60, 61, 62, 63]:
        s = [s[i] + RC[k][i] for i in range(3)]
        full = k < 4 or k >= 60
        s = [(s[i] ** 5) if (full or i == 0) else s[i] for i in range(3)]
        s = mdsp(s)
    return s[0]

if __name__ == '__main__':
    import sys
    j = int(sys.argv[1]); r = int(sys.argv[2])
    L = Line(j)
    t = time.time(); F = build_F(L, r); print('build', time.time() - t, 'deg', F.degree())
    for _ in range(3):
        x = random.randrange(p)
        assert int(F(x)) == L.F(x, r)
    c = random.randrange(p)
    t = time.time(); Fc = F.compose(R([c, 1])); print('shift', time.time() - t)
    co = Fc.coeffs()
    gcoef = [co[k] for k in range(1, len(co), 2)]
    g = R(gcoef)
    print('deg g', g.degree())
    t = time.time(); Xp = R([0, 1]).pow_mod((p - 1) // 2, g); print('powmod', time.time() - t)
    t = time.time(); d1 = g.gcd(Xp - 1).degree(); d2 = g.gcd(Xp + 1).degree(); print('gcd', time.time() - t, d1, d2)
