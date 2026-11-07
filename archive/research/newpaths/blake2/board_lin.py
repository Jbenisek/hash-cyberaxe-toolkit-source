"""Is the board's structure visible to the XOR-linear model?  (COMPUTED)
Board path: dv14 (length) absorbed in K2 by m4, m5; digest half A (out0,2,5,7) equal for free once C3 is pinned.
Here: kernel dimension of half A (and of 'E0,E2 inputs unchanged') with differences only in m4, m5 and the low 7
bits of v14, at w = 8, 12, 16, 32.  A zero dimension means no XOR-linear characteristic has the board's free half:
the free half exists only through value-dependent (pinned) transitions in C3."""
import sys
import numpy as np
sys.dont_write_bytecode = True
from lin import Model, nullspace

lines = []
for w in (8, 12, 16, 32):
    md = Model(w)
    cols = [i * w + j for i in (4, 5) for j in range(w)] + [16 * w + j for j in range(md.lw)]
    A = md.out_matrix((0, 2, 5, 7))[:, cols]
    dA = nullspace(A).shape[0]
    # E0, E2 state inputs after round-1 columns: Y0, Y5, Y10, Y15, Y2, Y7, Y8, Y13
    forms = [md.Y[i][b] for i in (0, 5, 10, 15, 2, 7, 8, 13) for b in range(w)]
    B = md.forms_to_mat(forms)[:, cols]
    dB = nullspace(B).shape[0]
    # K2 local collision alone (round-0 state after round 0 equal)
    forms0 = [md.X[i][b] for i in range(16) for b in range(w)]
    C = md.forms_to_mat(forms0)[:, cols]
    K0 = nullspace(C)
    dC = K0.shape[0]
    lines.append(f"w={w:2d}: vars {len(cols)}; dim(half A collides) = {dA}; dim(E0,E2 state inputs unchanged) = {dB}; "
                 f"dim(round-0 output unchanged) = {dC}")
    if dC:
        v = K0[0]
        dm4 = int("".join(str(int(b)) for b in v[:w][::-1]), 2)
        dm5 = int("".join(str(int(b)) for b in v[w:2 * w][::-1]), 2)
        dl = int("".join(str(int(b)) for b in v[2 * w:][::-1]), 2)
        lines.append(f"      example round-0 local collision: dm4={dm4:#x} dm5={dm5:#x} dv14={dl:#x}")
print("\n".join(lines))
with open("board_lin.txt", "w") as fh:
    fh.write(__doc__ + "\n" + "\n".join(lines) + "\n")
