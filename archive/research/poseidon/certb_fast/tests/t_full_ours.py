import sys, random
sys.path.insert(0, 'tests'); from fh import *
rng = random.Random(77)
d = 39062
o, e, rc = run_wsl(['xp', '--g', 'tests/data/gc.bin', '--out', 'tests/data/xp_gc.bin']); print(o, e, rc)
f = [rng.randrange(P) for _ in range(d)]
write_poly('tests/data/f_gc.bin', f)
o, e, rc = run_wsl(['compose', '--g', 'tests/data/gc.bin', '--f', 'tests/data/f_gc.bin', '--h', 'tests/data/xp_gc.bin', '--out', 'tests/data/comp_gc.bin']); print(o, e, rc)
