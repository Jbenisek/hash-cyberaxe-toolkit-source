import sys, random, time
sys.path.insert(0, 'tests'); sys.path.insert(0, '.')
from fh import *
d = int(sys.argv[1]) if len(sys.argv) > 1 else 200
rng = random.Random(1234 + d)
g = rand_poly(rng, d)
os.makedirs('tests/data', exist_ok=True)
write_poly('tests/data/g%d.bin' % d, coeffs(g))
a = R([rng.randrange(P) for _ in range(d)]); b = R([rng.randrange(P) for _ in range(d)])
write_poly('tests/data/a%d.bin' % d, coeffs(a)); write_poly('tests/data/b%d.bin' % d, coeffs(b))
o, e, rc = run_wsl(['mulmod', '--g', 'tests/data/g%d.bin' % d, '--a', 'tests/data/a%d.bin' % d, '--b', 'tests/data/b%d.bin' % d, '--out', 'tests/data/mm%d.bin' % d])
print(o, e, rc)
got = to_poly(read_poly('tests/data/mm%d.bin' % d)); exp = (a * b) % g
print('mulmod', got == exp)
o, e, rc = run_wsl(['xp', '--g', 'tests/data/g%d.bin' % d, '--out', 'tests/data/xp%d.bin' % d])
print(o, e, rc)
got = to_poly(read_poly('tests/data/xp%d.bin' % d)); exp = X.pow_mod(P, g)
print('xp', got == exp)
f = R([rng.randrange(P) for _ in range(d)]); 
write_poly('tests/data/f%d.bin' % d, coeffs(f))
write_poly('tests/data/h%d.bin' % d, coeffs(exp))
o, e, rc = run_wsl(['compose', '--g', 'tests/data/g%d.bin' % d, '--f', 'tests/data/f%d.bin' % d, '--h', 'tests/data/h%d.bin' % d, '--out', 'tests/data/comp%d.bin' % d])
print(o, e, rc)
got = to_poly(read_poly('tests/data/comp%d.bin' % d)); exp2 = f.compose_mod(exp, g)
print('compose', got == exp2)
