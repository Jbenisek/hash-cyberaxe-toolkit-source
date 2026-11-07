"""Q8: degree vs S-box count vs multiplications per evaluation (r=1, r=2). Executed-operation counts from a counting field class."""

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
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/orchard/impl'))
import poseidon_ref as pr
P = pr.P
class Counter:
    mul = 0; add = 0; sbox = 0
class F:
    __slots__ = ('v',)
    def __init__(self, v): self.v = v % P
    def __add__(self, o): Counter.add += 1; return F(self.v + (o.v if isinstance(o, F) else o))
    def __mul__(self, o): Counter.mul += 1; return F(self.v * (o.v if isinstance(o, F) else o))
    __rmul__ = __mul__
def sbox(x):
    Counter.sbox += 1
    x2 = x * x; x4 = x2 * x2; return x4 * x          # 3 multiplications
def run(r):
    rows = []
    s = [F(123456789), F(987654321), F(pr.CAPACITY)]
    for idx in pr.schedule(r):
        m0, a0_, s0 = Counter.mul, Counter.add, Counter.sbox
        s = [s[i] + pr.RC[idx][i] for i in range(3)]
        full = idx < 4 or idx >= 60
        for i in (range(3) if full else range(1)): s[i] = sbox(s[i])
        s = [s[0] * pr.MDS[i][0] + s[1] * pr.MDS[i][1] + s[2] * pr.MDS[i][2] for i in range(3)]
        rows.append((idx, full, Counter.sbox - s0, Counter.mul - m0, Counter.add - a0_))
    return rows
lines = []
for r in (1, 2):
    Counter.mul = Counter.add = Counter.sbox = 0
    rows = run(r)
    print(f"=== r={r}: executed operations of the plain algorithm (no shortcuts), then the same with folding of constants and dead lanes ===")
    print(" round | kind    | sboxes | mults | adds | cum sboxes | cum mults | layers (log5 of nk,rho-degree) | degree (nk,rho)")
    cs = cm = 0; layers = 0
    for (idx, full, sb, mu, ad) in rows:
        cs += sb; cm += mu; layers += 1
        print(f"  R{idx:<3d} | {'full' if full else 'partial':7s} | {sb:6d} | {mu:5d} | {ad:4d} | {cs:10d} | {cm:9d} | {layers:30d} | 5^{layers} = {5**layers}")
    # folded
    fold = 0; fs = 0
    for (idx, full, sb, mu, ad) in rows:
        m = mu; sbx = sb
        if idx == 0: m -= 3 + 3; sbx -= 1      # lane-2 S-box acts on a constant (3 mults) ; M column 2 multiplies constants (3 mults) -> precomputed
        if idx == 63: m -= 6                    # only row 0 of M is read
        fold += m; fs += sbx
    print(f"  total executed: sboxes {cs}, mults {cm}; with folding (R0 lane 2 constant, R63 rows 1,2 dead): sboxes {fs}, mults {fold}")
    print(f"  output degree in (nk,rho) 5^{len(rows)} = {5**len(rows)}; in (A,B) 5^{len(rows)-1} = {5**(len(rows)-1)}; mults per unit of log5-degree: {cm/len(rows):.1f} naive")
    print(f"  S-boxes per sequential layer: {cs/len(rows):.2f}; partial rounds add a layer of degree for 1 S-box (and 12 mults) instead of 3 (18)")
