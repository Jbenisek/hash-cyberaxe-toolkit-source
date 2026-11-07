import sys, time
sys.path.insert(0, 'tests'); from fh import *
g = to_poly(read_poly('tests/data/gc.bin'))
t = time.time(); xp = X.pow_mod(P, g); t1 = time.time() - t
ours = to_poly(read_poly('tests/data/xp_gc.bin'))
print('xp flint_s', t1, 'match', xp == ours, flush=True)
f = to_poly(read_poly('tests/data/f_gc.bin'))
t = time.time(); c = f.compose_mod(xp, g); t2 = time.time() - t
oc = to_poly(read_poly('tests/data/comp_gc.bin'))
print('compose flint_s', t2, 'match', c == oc, flush=True)
