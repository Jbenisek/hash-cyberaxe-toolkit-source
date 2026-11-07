import sys, time
sys.path.insert(0, 'tests'); sys.path.insert(0, r'../../../../3rd_openai_workspace/luna3')
from fh import *
import P3_21_midpoint_group as p
center = int(open('centres_r2.txt').readline())
o, e, rc = run_wsl(['center', 'data/F_r2_j0.bin', str(center), 'tests/data/gc_r2.bin']); print(o, e, rc)
coeff, _ = p.load_coefficients(0)
shift = p.shift_context(coeff)
t = time.time(); H = p.H_at_center(center, shift); print('flint shift', time.time() - t)
got = read_poly('tests/data/gc_r2.bin')
print('center r2 match', got == coeffs(H), len(got))
