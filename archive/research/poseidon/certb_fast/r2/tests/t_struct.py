# full-size (d=195312) mulmod / compose / xp checks via roots: g = prod(x-a_i) * random, results checked at the roots a_i
import sys, random, time
sys.path.insert(0, 'tests')
from fh import *
d = 195312; rng = random.Random(77)
roots = [rng.randrange(P) for _ in range(8)]
lin = R([1])
for a in roots: lin = lin * R([(-a) % P, 1])
t = time.time(); g = lin * rand_poly(rng, d - 8); print('g built', g.degree(), time.time() - t, flush=True)
def stress(): return R([rng.randrange(P) if rng.random() < 0.5 else (1 << 254) - 1 for _ in range(d)])
a = R([rng.randrange(P) for _ in range(d)]); b = R([rng.randrange(P) for _ in range(d)])
f = stress(); h = R([rng.randrange(P) for _ in range(d)])
for nm, v in (('g', g), ('a', a), ('b', b), ('f', f), ('h', h)): write_poly('tests/data/s_%s.bin' % nm, coeffs(v))
o, e, rc = run_wsl(['mulmod', '--g', 'tests/data/s_g.bin', '--a', 'tests/data/s_a.bin', '--b', 'tests/data/s_b.bin', '--out', 'tests/data/s_mm.bin']); print(o, e, rc, flush=True)
mm = to_poly(read_poly('tests/data/s_mm.bin'))
print('mulmod at roots', all(int(mm(r_)) == int(a(r_)) * int(b(r_)) % P for r_ in roots))
o, e, rc = run_wsl(['compose', '--g', 'tests/data/s_g.bin', '--f', 'tests/data/s_f.bin', '--h', 'tests/data/s_h.bin', '--out', 'tests/data/s_comp.bin']); print(o, e, rc, flush=True)
cp = to_poly(read_poly('tests/data/s_comp.bin'))
print('compose f(h) at roots', all(int(cp(r_)) == int(f(int(h(r_)))) for r_ in roots))
o, e, rc = run_wsl(['xp', '--g', 'tests/data/s_g.bin', '--out', 'tests/data/s_xp.bin']); print(o, e, rc, flush=True)
xp = to_poly(read_poly('tests/data/s_xp.bin'))
print('x^p at roots', all(int(xp(r_)) == r_ for r_ in roots))
