#!/usr/bin/env python3
"""f_D(0): leading coefficient (in W = tau^5) of the digest polynomial F on the line j = 0, by leading-term propagation (proof.md section 2.3).
Not shipped.  usage: python fd0.py R.   Check: R = 3, 4, 5 reproduce the constants of the executed entries."""

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

import sys
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/orchard/exec_r5tt'))
import poseidon_ref as ref
P, M = ref.P, [list(r) for r in ref.MDS]
def fd0(R):
    a, b = M[0][1], (-M[0][0]) % P
    d = [(M[i][0] * a + M[i][1] * b) % P for i in range(3)]
    v1 = [0, pow(d[1], 5, P), pow(d[2], 5, P)]
    lane = []
    for i in range(3):
        c = sum(M[i][j] * v1[j] for j in range(3)) % P
        lane.append((1, c))                       # state after round 1 = alpha + beta W: degree 1, leading coefficient beta_i
    kinds = ['full'] * 2 + ['partial'] * R + ['full'] * 4
    for k in kinds:
        out = [(5 * dg, pow(c, 5, P)) if (k == 'full' or i == 0) else (dg, c) for i, (dg, c) in enumerate(lane)]
        new = []
        for i in range(3):
            terms = [(out[j][0], M[i][j] * out[j][1] % P) for j in range(3)]
            dm = max(t[0] for t in terms)
            c = sum(t[1] for t in terms if t[0] == dm) % P
            new.append((dm, c))
        lane = new
    return lane[0]
if __name__ == '__main__':
    R = int(sys.argv[1]); dg, c = fd0(R)
    print('r=%d degree %d = 5^%d? %s' % (R, dg, 6 + R, dg == 5 ** (6 + R)), 'f_D(0) = 0x%064x' % c, 'nonzero' if c else 'ZERO')
