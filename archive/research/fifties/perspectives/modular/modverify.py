"""Check on EVERY rand and ctx row the exact modular-linear relations that modfourier F found on <= 4096 rows,
and identify the one-bit M3 relation. Output: modverify_out.txt."""
import sys
sys.dont_write_bytecode = True
import os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
E1IDX = (0, 2, 3, 1); E3IDX = (2, 0, 1, 3)
for name in ("rand", "ctx"):
    eo = np.fromfile(os.path.join(DATA, name, "eout.u32"), dtype="<u4").reshape(-1, 16)
    dig = np.fromfile(os.path.join(DATA, name, "dig.u32"), dtype="<u4").reshape(-1, 8)
    M1 = np.stack([(eo[:, i] - eo[:, 4 + i]).astype(np.uint32) for i in E1IDX], 1)
    M3 = np.stack([(eo[:, 8 + i] - eo[:, 12 + i]).astype(np.uint32) for i in E3IDX], 1)
    Rm = (dig[:, :4] - dig[:, 4:]).astype(np.uint32)
    n = len(M1)
    d34 = np.unique((M1[:, 1] - M1[:, 2]).astype(np.uint32))
    print("[%s] rows %d" % (name, n))
    print("  M1.w1 == 0 mod 16 on all rows: %s ; M1.w1 mod 32 values: %s" % (bool((M1[:, 0] % 16 == 0).all()), np.unique(M1[:, 0] % 32).tolist()))
    print("  M1.w3 - M1.w4 values: %s (one constant = dc1 = E1.c1 A-B)" % [hex(v) for v in d34])
    # one-bit relation among M3 parities (and with M1 parities)
    par = np.stack([M1[:, i] & 1 for i in range(4)] + [M3[:, i] & 1 for i in range(4)], 1)
    print("  parity columns (M1 w1,w3,w4,w6 | M3 w1,w3,w4,w6): constant columns %s, P(=1) %s" % (
        [i for i in range(8) if len(np.unique(par[:, i])) == 1], np.round(par.mean(0), 4).tolist()))
    for a in range(8):
        for b in range(a + 1, 8):
            v = np.unique(par[:, a] ^ par[:, b])
            if len(v) == 1:
                print("  exact parity relation: col %d ^ col %d = %d on all rows" % (a, b, v[0]))
    print("  Rm == M1 + M3 mod 2 on all rows: %s" % bool((((Rm - M1 - M3) & 1) == 0).all()))
