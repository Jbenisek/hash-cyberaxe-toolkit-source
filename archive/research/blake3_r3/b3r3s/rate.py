import sys, hashlib, importlib.util
def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
new = load('pkg/blake3/experiments/rho.py', 'rho_new'); old = load('../candidate_blake3/experiments/rho.py', 'rho_old')
for nm, m in (('old', old), ('new', new)):
    p = m.plan(22); ok = 0; halts = 0; A = 1500
    for a in range(A):
        r = int.from_bytes(hashlib.shake_256(b"rate/%d" % a).digest(32), "little") & (p["N"] - 1)
        try:
            res, cnt = m.search(p, r)
            ok += res is not None
        except m.Halt:
            halts += 1
    print(nm, 'B', p['B'], 'success', ok / A, 'halts', halts)
