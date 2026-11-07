
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

import struct, json, random, math, sys
from eng import *
import rho
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/pareto_clone'))
from verifier.blake3 import blake3 as vb
def tl2(ops):
    old = rho.PH; rho.PH = ops; lg = rho.ledger(256); rho.PH = old; return math.log2(lg["total"] / 638)
rng = random.Random(5); out = []
for t, site in ((887398322, 100), (214938249, 12), (639130335, 14), (939343106, 100), (508565131, 13)):
    P = struct.pack("<16I", t & M32, t >> 32, *([0] * 14))
    h = compress(IV, words(P), 0, 64, CS, 3)[:8]
    cfg = Cfg(cv=h, flags=10)
    ops = trace(cfg)[0]
    ok_trace = check_trace(cfg)
    # end-to-end: message P || 0^32 || x, own circuit (traced source) vs verifier at 3 rounds
    ops_f, by, src, want, outs = trace(cfg, dce=False)
    ns = {}; exec(src, {}, ns)
    good = True
    for _ in range(30):
        xs = [rng.getrandbits(256) for _ in range(7)]
        args = [sum(((x >> (32 * i)) & M32) << (PITCH * l) for l, x in enumerate(xs)) for i in range(8)]
        res = ns["f"](*args)
        for l, x in enumerate(xs):
            msg = P + bytes(32) + x.to_bytes(32, "little")
            d = b"".join(struct.pack("<I", (res[i] >> (PITCH * l)) & M32) for i in range(8))
            if d != vb(msg, 3): good = False
    out.append(dict(t=t, site=site, ops=ops, ok_trace=ok_trace, end_to_end_vs_verifier_r3=good, tl2=tl2(ops), gain=tl2(595) - tl2(ops)))
print(json.dumps(out, indent=1)); json.dump(out, open("plever_out.json", "w"), indent=1)
