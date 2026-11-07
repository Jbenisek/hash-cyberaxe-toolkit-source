"""Compare low-bit residues of K3's dS3 values with the K2-solvable set -S2 (looking for a congruence that
separates them).  Reads k3sol_f1.txt (dS3 of verified K3 solutions) and s2_iv.bin (dw4 records)."""
import os
import struct
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ds3 = set()
with open(os.path.join(HERE, "k3sol_f1.txt")) as f:
    for line in f:
        for tok in line.split():
            if tok.startswith("dS3="):
                ds3.add(int(tok[4:], 16))
s2 = []
with open(os.path.join(HERE, "s2_iv.bin"), "rb") as f:
    data = f.read()
for i in range(0, len(data), 12):
    dx, cnt, x = struct.unpack("<3I", data[i:i + 12])
    s2.append(dx)
targets = set(((-d) & 0xFFFFFFFF) for d in s2)
print("K3 distinct dS3:", len(ds3), " |S2|:", len(s2), " |-S2|:", len(targets))
for k in range(1, 13):
    m = (1 << k) - 1
    a = Counter(v & m for v in ds3)
    b = Counter(v & m for v in targets)
    common = set(a) & set(b)
    frac_k3 = sum(a[r] for r in common) / len(ds3)
    frac_s2 = sum(b[r] for r in common) / len(targets)
    print("mod 2^%-2d  K3 residues used %5d  -S2 residues used %5d  shared %5d  K3 mass on shared %.4f  -S2 mass on shared %.4f"
          % (k, len(a), len(b), len(common), frac_k3, frac_s2))
# ctz distributions
def ctz(v):
    return (v & -v).bit_length() - 1 if v else 32
print("ctz(dS3) for K3:", sorted(Counter(ctz(v) for v in ds3).items()))
print("ctz(t) for t in -S2:", sorted(Counter(ctz(v) for v in targets).items()))
