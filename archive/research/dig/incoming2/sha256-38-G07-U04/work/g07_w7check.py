
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

import sys, random, math
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/tools/build_pkg/scratch/pkgR38M3/pkg/sha256-r38/experiments'))
import a0lean38 as L
d = L.w7_distribution(); ex = sum(c * p for (c, ok), p in d.items()); pk = sum(p for (c, ok), p in d.items() if ok)
print('exact mean cost (20 bits)', float(ex), 'pass prob', float(pk), 'pass*2^32', float(pk) * 2**32)
rng = random.Random(7); n = 400000; s = 0; s2 = 0; ps = 0
for _ in range(n):
    m = L.Mach(); g = L.w7test(m, rng.getrandbits(32), 0); s += m.ops; s2 += m.ops ** 2; ps += g
mu = s / n; sd = math.sqrt((s2 / n - mu * mu) / n)
print('random 32-bit w: mean', mu, 'se', sd, 'z vs exact', (mu - float(ex)) / sd, 'pass freq', ps / n, 'exp', float(pk))
# chaining values: a = cv[0] of real compressions
m = L.Mach(lambda: rng.getrandbits(256)); s = 0; c7 = L.CLASSES[0][0]; k = 0; ss = 0
for _ in range(20000):
    r0 = m.rand(); r1 = m.rand(); M0 = L.unpack16(L.Mach(), r0, r1); cv = L.compress(L.IV, M0); a = cv[0]
    for c in L.CLASSES:
        mm = L.Mach(); L.w7test(mm, c[0], a); s += mm.ops + 4; k += 1
print('real cv, 90 classes: mean per fb w7 term', s / 20000)
