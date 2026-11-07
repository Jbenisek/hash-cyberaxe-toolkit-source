import sys, random, time
sys.path.insert(0, 'tests'); from fh import *
rng = random.Random(5); d = 39062
g = to_poly(read_poly('tests/data/gc.bin'))
a = R([rng.randrange(P) for _ in range(d)]); b = R([rng.randrange(P) for _ in range(d)])
write_poly('tests/data/a_gc.bin', coeffs(a)); write_poly('tests/data/b_gc.bin', coeffs(b))
o, e, rc = run_wsl(['mulmod', '--g', 'tests/data/gc.bin', '--a', 'tests/data/a_gc.bin', '--b', 'tests/data/b_gc.bin', '--out', 'tests/data/mm_gc.bin'])
t = time.time(); exp = (a * b) % g; print('flint mulmod_s', time.time() - t)
print('full-size mulmod match', to_poly(read_poly('tests/data/mm_gc.bin')) == exp)
