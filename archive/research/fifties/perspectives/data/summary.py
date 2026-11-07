"""Sanity summary of rand/ and ctx/ (no analysis claims): per word of R, K1, K3 - distinct values, mean Hamming
weight, largest single-bit bias |P(bit=1) - 1/2| and the bit where it occurs, constant bits."""
import sys
sys.dont_write_bytecode = True
import os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
NAMES = ("1", "3", "4", "6")


def hw(a):
    a = a.astype(np.uint32)
    return np.unpackbits(a.view(np.uint8).reshape(-1, 4), axis=1).sum(1)


for name in ("rand", "ctx"):
    keys = np.fromfile(os.path.join(HERE, name, "keys.u32"), dtype="<u4").reshape(-1, 8)
    res = np.fromfile(os.path.join(HERE, name, "res.u32"), dtype="<u4").reshape(-1, 4)
    n = res.shape[0]
    print("[%s] rows %d" % (name, n))
    for label, arr in (("R", res), ("K1", keys[:, :4]), ("K3", keys[:, 4:])):
        for i in range(4):
            col = arr[:, i]
            bits = ((col[:, None] >> np.arange(32, dtype=np.uint32)) & 1).mean(0)
            bias = np.abs(bits - 0.5)
            const = [b for b in range(32) if bits[b] in (0.0, 1.0)]
            print("  %-2s word %s: distinct %8d  mean HW %6.3f  max bit bias %.4f at bit %2d  constant bits %s" % (
                label, NAMES[i], len(np.unique(col)), hw(col).mean(), bias.max(), int(bias.argmax()), const or "-"))
    rows = np.ascontiguousarray(res).view(np.dtype((np.void, 16))).ravel()
    print("  distinct 128-bit residuals: %d of %d" % (len(np.unique(rows)), n))
