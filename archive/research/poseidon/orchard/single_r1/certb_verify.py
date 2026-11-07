"""certb_verify.py: referee recomputation of the single-centre success-probability inputs (proof.md section 8.7). Needs no data file except the organizer's constants JSON.
usage:  python certb_verify.py ORCHARD_CONSTANTS.json C0 L [J [C0A]]   (J = line index, default 0; C0A = the CERT A critical point, checked if given)
needs:  python 3 and python-flint (tested with 0.9.0: fmpz_mod_poly with pow_mod, compose_mod, gcd, derivative, pow_trunc, inverse_series_trunc)
V1  build F_j (degree 5^7) by evaluation at the 2^17-th roots of unity and one inverse transform; check F(tau^5) against an independent reference hash (5 values of tau).
V7  for m = 5, 25, ..., 15625: H_m is forced by the top m coefficients of F (r-th root series, r = 5^7 / m); F mod H_m must be non-constant (no right factor of degree m).
V6  (if C0A is given; CERT A) F'(C0A) = 0, F''(C0A) != 0, g(C0A; S) has constant term 0 and gcd(g, g') = 1.
V2  g = H(C0; S) monic of degree d = 39062 from F and C0 by one Taylor shift.   V3  gcd(g, g') = 1.   V4  L is prime and d/2 < L <= d - 3.
V5  R_0 = x^p mod g, R_i = R_(i-1) o R_(i-1) mod g, Q = x^(p^L) mod g by the binary chain; g_L = gcd(g, Q - x), g_1 = gcd(g, R_0 - x);
    accept iff deg g_L - deg g_1 = L; then f = g_L / g_1 is irreducible of degree L and divides g (proof.md Lemma 8.7.1).
It prints SHA-256 of f, of g / f and of R_i mod f (32-byte little-endian coefficients, constant term first), to be compared with the values stated in proof.md."""
import sys, json, time, hashlib, random
import flint

P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
T0 = time.time()


def say(tag, msg):
    print('%-5s %8.1fs  %s' % (tag, time.time() - T0, msg), flush=True)


def is_prime(n):
    return n > 1 and all(n % q for q in range(2, int(n ** 0.5) + 1))


def sha(poly):
    n = poly.degree()
    return hashlib.sha256(b''.join(int(poly[i]).to_bytes(32, 'little') for i in range(n + 1))).hexdigest()


def ntt(a, w):
    n = len(a); j = 0
    for i in range(1, n):
        bit = n >> 1
        while j & bit: j ^= bit; bit >>= 1
        j ^= bit
        if i < j: a[i], a[j] = a[j], a[i]
    ln = 2
    while ln <= n:
        wl = pow(w, n // ln, P); half = ln // 2
        tw = [1] * half
        for k in range(1, half): tw[k] = tw[k - 1] * wl % P
        for s in range(0, n, ln):
            for k in range(half):
                u = a[s + k]; v = a[s + k + half] * tw[k] % P
                a[s + k] = (u + v) % P; a[s + k + half] = (u - v) % P
        ln <<= 1


def line_data(const, j):
    MDS = [[int(x, 16) % P for x in r] for r in const['mds']]; RC = [[int(x, 16) % P for x in r] for r in const['round_constants']]
    mv = lambda v: [sum(MDS[i][k] * v[k] for k in range(3)) % P for i in range(3)]
    K5 = pow((1 << 65) + RC[0][2], 5, P)
    plane = [(MDS[i][2] * K5 + RC[1][i]) % P for i in range(3)]          # x_k = M_k0 U + M_k1 V + plane_k
    i1, i2 = [t for t in range(3) if t != j]
    a_, b_, c_, d_ = MDS[i1][0], MDS[i1][1], MDS[i2][0], MDS[i2][1]
    det = pow((a_ * d_ - b_ * c_) % P, -1, P)
    u, v = ((-plane[i1]) * d_ - b_ * (-plane[i2])) * det % P, (a_ * (-plane[i2]) - (-plane[i1]) * c_) * det % P   # x_i1 = x_i2 = 0
    kappa = (MDS[j][0] * u + MDS[j][1] * v + plane[j]) % P
    dirn = [(MDS[t][0] * MDS[j][1] - MDS[t][1] * MDS[j][0]) % P for t in range(3)]   # x_t = dirn_t * tau
    assert dirn[j] == 0 and dirn[i1] and dirn[i2]
    s1 = mv([kappa ** 5 % P if t == j else dirn[t] * 0 for t in range(3)])
    s2 = mv([pow(dirn[t], 5, P) for t in range(3)])
    return MDS, RC, (u, v, dirn, j, K5), s1, s2


def tail(s1, s2, MDS, RC, w):
    st = [(s1[i] + s2[i] * w) % P for i in range(3)]                        # state after round 1 (before the round-2 constants)
    for idx in (2, 3, 4, 60, 61, 62, 63):
        z = [(st[i] + RC[idx][i]) % P for i in range(3)]
        y = [pow(x, 5, P) for x in z] if idx != 4 else [pow(z[0], 5, P), z[1], z[2]]
        st = [sum(MDS[i][k] * y[k] for k in range(3)) % P for i in range(3)]
    return st[0]


def ref_hash(MDS, RC, nk, rho):                                              # independent straight-line reference of the target: rounds 0-3, 4, 60-63
    st = [nk, rho, 1 << 65]
    for idx in (0, 1, 2, 3, 4, 60, 61, 62, 63):
        z = [(st[i] + RC[idx][i]) % P for i in range(3)]
        y = [pow(x, 5, P) for x in z] if idx != 4 else [pow(z[0], 5, P), z[1], z[2]]
        st = [sum(MDS[i][k] * y[k] for k in range(3)) % P for i in range(3)]
    return st[0]


def build_F(const, j, R):
    MDS, RC, (u, v, dirn, jj, K5), s1, s2 = line_data(const, j)
    n = 5 ** 7; N = 1 << 17
    z = 2
    while True:
        w = pow(z, (P - 1) // N, P)
        if pow(w, N // 2, P) != 1: break
        z += 1
    vals = []; x = 1
    for _ in range(N):
        vals.append(tail(s1, s2, MDS, RC, x)); x = x * w % P
    ntt(vals, pow(w, -1, P)); ninv = pow(N, -1, P)
    co = [c * ninv % P for c in vals]
    assert all(c == 0 for c in co[n + 1:]) and co[n] != 0
    F = R(co[:n + 1])
    e = pow(5, -1, P - 1); rnd = random.Random(1)
    for _ in range(5):                                                       # F(tau^5) = reference hash of the canonical input built from tau
        tau = rnd.randrange(P); U = (u + tau * MDS[j][1]) % P; V = (v - tau * MDS[j][0]) % P
        nk = (pow(U, e, P) - RC[0][0]) % P; rho = (pow(V, e, P) - RC[0][1]) % P
        assert ref_hash(MDS, RC, nk, rho) == int(F(pow(tau, 5, P))) % P, 'F does not match the reference hash'
    return F


def taylor_shift(F, c, R):
    n = F.degree(); fact = [1] * (n + 1)
    for k in range(1, n + 1): fact[k] = fact[k - 1] * k % P
    A = R([int(F[n - i]) * fact[n - i] % P for i in range(n + 1)])          # sum a_{n-i} (n-i)! x^i
    inv = pow(fact[n], -1, P); invf = [1] * (n + 1); invf[n] = inv
    for k in range(n, 0, -1): invf[k - 1] = invf[k] * k % P
    cp = 1; B = []
    for m in range(n + 1): B.append(cp * invf[m] % P); cp = cp * c % P       # c^m / m!
    C = A * R(B)
    return R([int(C[n - k]) * invf[k] % P for k in range(n + 1)])           # coefficients of F(x + c)


def g_of_centre(F, c0, R):
    n = F.degree(); b = taylor_shift(F, c0, R); an = pow(int(F[n]), -1, P)
    return R([int(b[2 * k + 1]) * an % P for k in range((n - 1) // 2 + 1)])  # monic: F(c+s) - F(c-s) = 2 a_n s g(s^2)


def witness(g, l, R, show=say):
    """accept iff the monic squarefree g has exactly one irreducible factor of prime degree l (d/2 < l <= d-3); returns (f, cofactor, R_list) or None"""
    d = g.degree(); X = R.gen()
    assert g.gcd(g.derivative()) == R(1); show('V3', 'gcd(g, g\') = 1: g is squarefree')
    assert is_prime(l) and 2 * l > d and l <= d - 3; show('V4', 'l = %d is prime in (d/2, d-3], d = %d' % (l, d))
    Rs = [X.pow_mod(int(R.modulus()), g)]; show('V5', 'R_0 = x^p mod g')
    m = l.bit_length()
    for i in range(1, m):
        Rs.append(Rs[-1].compose_mod(Rs[-1], g)); show('V5', 'R_%d = R_%d o R_%d mod g' % (i, i - 1, i - 1))
    Q = None
    for i in range(m):
        if (l >> i) & 1:
            Q = Rs[i] if Q is None else Rs[i].compose_mod(Q, g); show('V5', 'chain bit %d' % i)
    gl = g.gcd(Q - X); g1 = g.gcd(Rs[0] - X)
    show('V5', 'deg gcd(g, x^(p^l) - x) = %d, deg gcd(g, x^p - x) = %d' % (gl.degree(), g1.degree()))
    if gl.degree() - g1.degree() != l: return None
    f = gl // g1
    return f, g // f, [r % f for r in Rs]


def indecomposable_at(F, m, R):
    """F is not G(H) for any G over F_p with deg H = m (m | deg F, p > deg F): H is forced by the top m coefficients of F (monic, H(0) = 0, the r-th root series, r = deg F / m);
    returns (H, F mod H); F = G(H) iff F mod H is constant."""
    n = F.degree(); r = n // m; assert n % m == 0 and P > n
    X = R.gen(); an = pow(int(F[n]), -1, P)
    A = R([int(F[n - i]) * an % P for i in range(m)])                      # A(y) = (reversed F / a_n) mod y^m, y = 1/x
    B = R(1); N = 1; rinv = pow(r, -1, P)
    while N < m:
        N = min(2 * N, m)
        t = A.truncate(N).mul_low(B.pow_trunc(r, N).inverse_series_trunc(N), N) + (r - 1)   # B <- B ((r-1) + A / B^r) / r  (Newton step for B^r = A)
        B = B.mul_low(t, N).scalar_mul(rinv)
    b = [int(B[i]) if i <= B.degree() else 0 for i in range(m)]
    H = R([0] + [b[m - 1 - k] for k in range(m)] + [])                     # x^m + b_1 x^(m-1) + ... + b_(m-1) x   (coefficient of x^(m-i) is b_i, b_0 = 1)
    return H, F % H


def cert_a(F, c0a, R):
    g = g_of_centre(F, c0a, R); d1 = F.derivative(); d2 = d1.derivative()
    assert int(d1(c0a)) % P == 0 and int(d2(c0a)) % P != 0, "CERT A: F-prime(c0) = 0 and F-second(c0) != 0 fail"
    assert int(g[0]) == 0 and g.gcd(g.derivative()) == R(1), "CERT A: g(0) = 0 and gcd(g, g-prime) = 1 fail"
    return g


if __name__ == '__main__':
    const = json.load(open(sys.argv[1])); c0 = int(sys.argv[2]); l = int(sys.argv[3]); j = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    R = flint.fmpz_mod_poly_ctx(P)
    c0a = int(sys.argv[5]) if len(sys.argv) > 5 else None
    F = build_F(const, j, R)
    say('V1', 'F_%d built, degree %d, sha256(coefficients) = %s' % (j, F.degree(), sha(F)))
    for e in range(1, 7):                                                   # V7: no proper right factor of degree 5^e (e = 1..6); 5^7 has no other proper divisors
        H, rem = indecomposable_at(F, 5 ** e, R)
        assert rem.degree() >= 1, 'F is a composition with an inner polynomial of degree %d' % 5 ** e
        say('PASS', 'V7 inner degree m = %5d: F mod H_m has degree %d > 0, so F != G(H) for every G; sha256(H_m) = %s' % (5 ** e, rem.degree(), sha(H)))
    if c0a is not None: cert_a(F, c0a, R); say('PASS', 'CERT A at c0 = %d: F-prime(c0) = 0, F-second(c0) != 0, g(0) = 0, g squarefree' % c0a)
    g = g_of_centre(F, c0, R); assert g.degree() == (F.degree() - 1) // 2 and int(g[g.degree()]) == 1
    say('V2', 'g = H(c0, S) monic, degree %d, sha256 = %s' % (g.degree(), sha(g)))
    res = witness(g, l, R)
    if res is None: say('FAIL', 'no irreducible factor of degree %d' % l); sys.exit(1)
    f, cof, Rl = res
    say('PASS', 'f has degree %d and is irreducible; sha256(f) = %s' % (f.degree(), sha(f)))
    say('PASS', 'cofactor degree %d, sha256 = %s' % (cof.degree(), sha(cof)))
    for i, r in enumerate(Rl): say('PASS', 'sha256(R_%d mod f) = %s' % (i, sha(r)))
