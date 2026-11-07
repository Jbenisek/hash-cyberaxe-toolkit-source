"""fixcheck.py (newpaths/edge_root; research only): in the ROOT arrangement (outer six words, middle X2, member Y4),
do Y9, w8 and E = Y3 + Y4 + w8 (the inputs of the counter-path filter) stay fixed across the inner trials?
Uses halfsearch.py's own outer/middle/trial (read-only import).  usage: python -B fixcheck.py NOUT NMID NMEM SEED
"""

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
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/pkg10/pkg/blake3-r2/experiments'))
import halfsearch as H

NOUT, NMID, NMEM, seed = (int(a) for a in sys.argv[1:5])
rng = random.Random(seed)
M = H.MASK

def inputs(v, y4):
    words, t = H.trial(v, y4)
    c1 = H.g(t["X1"], t["X5"], v["X9"], v["X13"], words[3], words[10])  # as residual_word1
    y9, w8 = c1[2], words[8]
    return y9, w8, (H.Y3 + y4 + w8) & M

per_mid = {"Y9": [], "w8": [], "E": []}
per_out = {"Y9": [], "w8": [], "E": []}
for _ in range(NOUT):
    o = H.outer([rng.getrandbits(32) for _ in range(6)])
    ks = [rng.randrange(H.CLASS_SIZE) for _ in range(NMEM)]
    ys = [H.class_member(k) for k in ks]
    seen_out = {"Y9": set(), "w8": set(), "E": set()}
    for _ in range(NMID):
        v = H.middle(o, rng.getrandbits(32))
        rows = [inputs(v, y4) for y4 in ys]
        for i, name in enumerate(("Y9", "w8", "E")):
            vals = {r[i] for r in rows}
            per_mid[name].append(len(vals))
            seen_out[name] |= vals
    for name in seen_out:
        per_out[name].append(len(seen_out[name]))
print(f"class size 2^{len(H.CLASS_FREE)}; outer steps {NOUT}, middle steps per outer {NMID}, members per step {NMEM}")
for name in ("Y9", "w8", "E"):
    pm, po = per_mid[name], per_out[name]
    print(f"  {name}: distinct per middle step min {min(pm)} mean {sum(pm)/len(pm):.1f} of {NMEM}; "
          f"per outer step min {min(po)} mean {sum(po)/len(po):.1f} of {NMID*NMEM}")
# which word moves Y9 / w8: hold the member, vary X2 (same outer); hold X2, vary the member
o = H.outer([rng.getrandbits(32) for _ in range(6)])
y4 = H.class_member(rng.randrange(H.CLASS_SIZE))
a = {inputs(H.middle(o, rng.getrandbits(32)), y4)[:2] for _ in range(256)}
v = H.middle(o, rng.getrandbits(32))
b = {inputs(v, H.class_member(rng.randrange(H.CLASS_SIZE)))[:2] for _ in range(256)}
print(f"  member held, X2 varied (256): distinct (Y9,w8) {len(a)}; X2 held, member varied (256): distinct {len(b)}")
