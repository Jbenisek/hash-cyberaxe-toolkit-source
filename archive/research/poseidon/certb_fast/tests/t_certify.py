import sys, random, json
sys.path.insert(0, 'tests'); from fh import *
rng = random.Random(31)
def irr(e):
    while True:
        f = R([rng.randrange(P) for _ in range(e)] + [1])
        if f.is_irreducible(): return f
def sqfree_coprime(deg, other):
    while True:
        v = rand_poly(rng, deg)
        if v.is_squarefree() and v.gcd(other).degree() == 0: return v
def case(name, f, v):
    g = f * v
    d = 'tests/data/cert_' + name; os.makedirs(d, exist_ok=True)
    write_poly(d + '/g.bin', coeffs(g)); write_poly(d + '/f.bin', coeffs(f)); write_poly(d + '/co.bin', coeffs(v))
    o, e, rc = run_wsl(['certify', '--f', d + '/f.bin', '--cofactor', d + '/co.bin', '--g', d + '/g.bin', '--center', '12345', '--outdir', d])
    res = json.loads(o.strip().splitlines()[-1])
    print(name, 'deg', f.degree(), 'flint is_irreducible:', f.is_irreducible(), '| engine:', res['result'], 'rc', rc,
          '| x^(p^l)==x', res['x_p_l_equals_x'], 'gcd deg', res['gcd_R0_minus_x_degree'], 'prod ok', res['f_times_cofactor_equals_g'], 'sqfree', res['squarefree'], e[-200:])
    return d, res
d, res = case('pos101', irr(101), None) if False else (None, None)
f = irr(101); v = sqfree_coprime(60, f)
d, res = case('pos101', f, v)
# check R_j files vs flint
def read_txt(path):
    L = open(path).read().split('coefficients:\n')[1].split()
    return R([int(x) for x in L])
x0 = X.pow_mod(P, f); Rj = [x0]
for j in range(1, 16): Rj.append(Rj[-1].compose_mod(Rj[-1], f))
print('R_j files match flint:', all(read_txt('%s/certB_witness_R_%d.txt' % (d, j)) == Rj[j] for j in range(16)))
print(open(d + '/certB_witness_composition.json').read()[:0])
# negative 1: irreducible(100) * linear -> degree 101 reducible
a = irr(100); lin = R([rng.randrange(P), 1]); f2 = a * lin
case('neg_deg100_times_linear', f2, sqfree_coprime(60, f2))
# negative 2: product of 53 distinct linear factors (x^p = x, gcd check must fail)
f3 = R([1])
for i in range(53): f3 = f3 * R([P - (1000 + i), 1])
case('neg_all_linear53', f3, sqfree_coprime(40, f3))
# negative 3: product of two irreducibles degree 50 and 51 (prime 101)
f4 = irr(50) * irr(51)
case('neg_50x51', f4, sqfree_coprime(40, f4))
# negative 4: f * cofactor != g (wrong cofactor)
f5 = irr(97); v5 = sqfree_coprime(50, f5); g5 = f5 * v5
d5 = 'tests/data/cert_wrongco'; os.makedirs(d5, exist_ok=True)
write_poly(d5 + '/g.bin', coeffs(g5)); write_poly(d5 + '/f.bin', coeffs(f5)); write_poly(d5 + '/co.bin', coeffs(v5 + 1))
o, e, rc = run_wsl(['certify', '--f', d5 + '/f.bin', '--cofactor', d5 + '/co.bin', '--g', d5 + '/g.bin', '--center', '1', '--outdir', d5])
print('wrongco', json.loads(o.strip().splitlines()[-1])['result'], rc)
# negative 5: non-squarefree g
f6 = irr(89); v6 = sqfree_coprime(30, f6); v6 = v6 * v6; g6 = f6 * v6
d6 = 'tests/data/cert_nsq'; os.makedirs(d6, exist_ok=True)
write_poly(d6 + '/g.bin', coeffs(g6)); write_poly(d6 + '/f.bin', coeffs(f6)); write_poly(d6 + '/co.bin', coeffs(v6))
o, e, rc = run_wsl(['certify', '--f', d6 + '/f.bin', '--cofactor', d6 + '/co.bin', '--g', d6 + '/g.bin', '--center', '1', '--outdir', d6])
print('nonsquarefree', json.loads(o.strip().splitlines()[-1])['result'], rc)
