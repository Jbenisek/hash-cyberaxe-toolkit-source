# charrows.py R39JOINT_PY : the pair's constants and signed rows (char.txt format; leftmost = bit 31; u = M bit 1, M' bit 0)
import sys, importlib.util
sp = importlib.util.spec_from_file_location("j", sys.argv[1]); J = importlib.util.module_from_spec(sp); sp.loader.exec_module(J)
h = lambda v: ' '.join('%08x' % x for x in v)
def sg(x, y): return ''.join('-' if not ((x ^ y) >> b) & 1 else ('u' if (x >> b) & 1 else 'n') for b in range(31, -1, -1))
CA, CE, _ = J.traj(J.CV_PUB, J.M_PUB); BA, BE, _ = J.traj(J.CV_PUB, J.MP_PUB); WM, WP = J.expand(J.M_PUB), J.expand(J.MP_PUB)
print('CV', h(J.CV_PUB)); print('M ', h(J.M_PUB)); print('MP', h(J.MP_PUB))
print('Mdiff_words_8_12', h(J.MP_PUB[8:13])); print('ROWS:')
for r in range(39):
    a, e, w = sg(CA[r + 4], BA[r + 4]), sg(CE[r + 4], BE[r + 4]), sg(WM[r], WP[r])
    if (a + e + w).strip('-'): print('%3d A: %s E: %s W: %s' % (r, a, e, w))
print('G16 %08x W17 %08x' % (J.G16, J.W17PUB))
