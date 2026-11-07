import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import poseidon_ref as ref
ok = bad = 0; ms = {}
for line in open(sys.argv[1]):
    f = line.split()
    if f[0] == 'M': ms[int(f[1])] = int(f[2]); continue
    if f[0] != 'T': continue
    j, k, r = int(f[1]), int(f[2]), int(f[3]); tau, nk, rho, F = (int(x, 16) for x in f[4:8])
    good = 0 <= nk < ref.P and 0 <= rho < ref.P and ref.hash_reduced(nk, rho, r) == F
    ok += good; bad += (not good)
    if not good: print('MISMATCH', j, k, r)
print('poly_degree_m', ms, 'r3 expected 976562:', ms.get(3) == 976562)
by_r = {}
for line in open(sys.argv[1]):
    f = line.split()
    if f[0] == 'T': by_r[int(f[3])] = by_r.get(int(f[3]), 0) + 1
print('checked per r', by_r, 'ok', ok, 'mismatches', bad)
sys.exit(0 if bad == 0 and ms.get(3) == 976562 else 1)
