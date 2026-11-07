'''Why does compress2 verification fail on planted roots?  Run the conditions of ev.verify one by one on
(a) a real point (ctr_outer, T1 = 0) and (b) a relation-propagated basis point with T1 = 0.'''

# Publication path adapter: resolve data paths from the extracted source tree.
def _hca_public_path_text(value):
    if "__HCA_WORKSPACE__/" not in value:
        return value
    import os as _hca_os
    from pathlib import Path as _hca_Path
    root = _hca_os.environ.get("HASHCYBERAXE_WORKSPACE")
    if root is None:
        here = _hca_Path(__file__).resolve().parent
        root = next((str(p) for p in (here, *here.parents) if (p / "research").is_dir()), None)
    if root is None:
        raise FileNotFoundError("Extract the research source tree, or set HASHCYBERAXE_WORKSPACE to its archive directory.")
    return value.replace("__HCA_WORKSPACE__/", str(_hca_Path(root).resolve()).replace("\\", "/") + "/")

import sys, random
sys.dont_write_bytecode = True
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/fifties/split_e3'))
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/fifties/cycle_solver/t1filter'))
import ev
from gen_batch import planted_point
hs = ev.hs; M = ev.M; ror = ev.ror
def conds(v, F, y14):
    c1 = ev.c1_from_y14(v, y14); r = hs.ctr_trial(v, c1)
    if r is None: return 'T0=0'
    a, b, t0, tv = r; t = t0 | (v['T1'] << 32)
    (wa, da, ya), (wb, db, yb) = hs.compress2(a[:hs.LEN_A], t, hs.CTR_FLAGS), hs.compress2(b[:hs.LEN_B], t, hs.CTR_FLAGS)
    e3a, e3b = (ya[3] + ya[4] + wa[15]) & M, (yb[3] + yb[4] + wb[15]) & M
    return {'Y4': ya[4] == F['Y4'], 'Y9': ya[9] == F['Y9'], 'w8': wa[8] == F['w8'], 'Y14': ya[14] == y14, 'tvY14': tv['Y14'] == y14,
            'digest0257': all(da[i] == db[i] for i in (0, 2, 5, 7)), 'pins': (ya[3], ya[11]) == (hs.Y3, hs.Y11),
            'class': e3a & hs.CLASS_MASK == hs.CLASS_VALUE, 'eta': ror(e3a ^ e3b, 16) == hs.ETA,
            'ab': ya[4] == yb[4] and ya[9] == yb[9] and ya[14] == yb[14] and wa[8] == wb[8]}
rnd = random.Random(3)
v1 = ev.real_point(rnd)
print('real point   :', conds(v1, {w: v1[w] for w in ('Y4', 'Y9', 'w8')}, ev.y14_of(v1)))
v0 = planted_point(rnd, 0)
print('relprop T1=0 :', conds(v0, {w: v0[w] for w in ('Y4', 'Y9', 'w8')}, ev.y14_of(v0)))
v2 = planted_point(rnd, 12345)
print('relprop T1!=0:', conds(v2, {w: v2[w] for w in ('Y4', 'Y9', 'w8')}, ev.y14_of(v2)))
from gen_batch import ORD
for t1 in (0, 12345):
    v = {w: rnd.getrandbits(32) for w in ev.rels.BASIS}; v['Y4'] = ev.real_point(rnd)['Y4']; v['T1'] = t1
    for i, w in ORD: v[w] = ev.solve1(ev.REL[i], w, v)
    print('relprop, real Y4, T1=%d:' % t1, conds(v, {w: v[w] for w in ('Y4', 'Y9', 'w8')}, ev.y14_of(v)))
