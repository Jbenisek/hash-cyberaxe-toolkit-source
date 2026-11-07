import sys, time
sys.path.insert(0, 'tests'); sys.path.insert(0, '.'); sys.path.insert(0, r'../../../3rd_openai_workspace/luna3')
from fh import *
import P3_20_midpoint_group as p
center = 16102098619512022721056163846197557588758949045546201477974792624946581626367
Fbin = r'../../../3rd_openai_workspace/luna3/P3_20_F_j0_coeffs.bin'
import shutil; shutil.copy(Fbin, 'tests/data/F_j0.bin')
o, e, rc = run_wsl(['center', 'tests/data/F_j0.bin', str(center), 'tests/data/gc.bin']); print(o, e, rc)
coeff, _ = p.load_coefficients(0)
shift = p.shift_context(coeff)
t = time.time(); H = p.H_at_center(center, shift); print('flint shift', time.time() - t)
got = read_poly('tests/data/gc.bin')
print('center match', got == coeffs(H), len(got))
import pickle
