"""check2-3: which W cells of rows 0..15 fail on the dumped successes (value part vs difference part), and what
vt38.CELL['W'] specifies for rows 0..15 (the success test of proof.md 6.2 checks W cells of rows 16..37 only)."""

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

import sys, importlib.util
sys.dont_write_bytecode = True
import numpy as np
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/sha256grid/check2-3'))
import indep_hits as H
vt = H.vt; U = np.uint32
pc = lambda x: bin(x).count('1')
print('vt38 W cells rows 0..15 (mask bits / diff):', [(i, pc(vt.CELL['W'][i][0]), hex(vt.CELL['W'][i][2])) for i in range(16)])
b = np.fromfile(_hca_public_path_text('__HCA_WORKSPACE__/research/sha256grid/scout2-3/g2_main.hits'), dtype='<u4')
n = b.size // 43; r = b.reshape(n, 43).astype(U)
with np.errstate(over='ignore'):
    Ax, Ex, Wx, _ = H.trace(r[:, 3:11], r[:, 11:27], 38); Ay, Ey, Wy, _ = H.trace(r[:, 3:11], r[:, 27:43], 38)
for i in range(16):
    m, v, d = (U(c) for c in vt.CELL['W'][i][:3])
    fv = int(((Wx[i] & m) != v).sum()); fd = int(((Wx[i] ^ Wy[i]) != d).sum())
    if fv or fd: print('row %d: value-part failures %d, difference-part failures %d (of %d)' % (i, fv, fd, n))
