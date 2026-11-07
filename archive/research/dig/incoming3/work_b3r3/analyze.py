"""Step analysis for blake3-r3 R1D1..R2C1 quarter-steps.  Own code (numpy tracer + filed tracer subclass)."""

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

import sys, json, math, random, importlib.util, struct
import numpy as np
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/blake3_r3/candidate_blake3/experiments'))
import rho
from rho import IV, PERM, GCALLS, M32
import b3steps

# ---- validation against the organizer reference (verifier/blake3.py), 7 rounds and 3 rounds
spec = importlib.util.spec_from_file_location("vb3", _hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/pareto_clone/verifier/blake3.py'))
vb3 = importlib.util.module_from_spec(spec); spec.loader.exec_module(vb3)
val = {}
val["empty_7r"] = vb3.blake3(b"", 7).hex()
val["empty_7r_ok"] = val["empty_7r"] == "af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262"
rng = random.Random(20261012)
okc = {7: 0, 3: 0, 2: 0, 1: 0}; N = 300
for _ in range(N):
    x = rng.getrandbits(256)
    msg = bytes(32) + x.to_bytes(32, "little")
    mw = [0]*8 + [(x >> (32*i)) & M32 for i in range(8)]
    for r in okc:
        d = rho.digest_words(mw, rounds=r)
        if b"".join(struct.pack("<I", w) for w in d) == vb3.blake3(msg, r): okc[r] += 1
val["rho_vs_verifier_matches_of_%d" % N] = okc
print(val)

# ---- numpy tracer with snapshots
def ror(v, r): return (v >> np.uint32(r)) | (v << np.uint32(32 - r))
def trace(X, skip=None, rounds=3):
    n = X.shape[0]
    v = np.zeros((n, 16), np.uint32)
    for i in range(8): v[:, i] = IV[i]
    for i in range(4): v[:, 8+i] = IV[i]
    v[:, 14] = 64; v[:, 15] = 11
    m = np.zeros((n, 16), np.uint32); m[:, 8:] = X
    snaps = {}
    for rd in range(rounds):
        for j, (a, b, c, d) in enumerate(GCALLS):
            nm = "R%d%s%d" % (rd+1, "C" if j < 4 else "D", j % 4)
            x, y = m[:, 2*j], m[:, 2*j+1]
            for q in range(1, 5):
                if (nm, q) == skip: continue          # step replaced by identity
                if q == 1: v[:, a] = v[:, a] + v[:, b] + x; v[:, d] = ror(v[:, d] ^ v[:, a], 16); out = (a, d)
                if q == 2: v[:, c] = v[:, c] + v[:, d]; v[:, b] = ror(v[:, b] ^ v[:, c], 12); out = (c, b)
                if q == 3: v[:, a] = v[:, a] + v[:, b] + y; v[:, d] = ror(v[:, d] ^ v[:, a], 8); out = (a, d)
                if q == 4: v[:, c] = v[:, c] + v[:, d]; v[:, b] = ror(v[:, b] ^ v[:, c], 7); out = (c, b)
                snaps[(nm, q)] = (v[:, out[0]].copy(), v[:, out[1]].copy())
        m = m[:, PERM]
    dig = v[:, :8] ^ v[:, 8:]
    return snaps, dig

def rand_X(n, seed):
    r = np.random.default_rng(seed)
    return r.integers(0, 2**32, size=(n, 8), dtype=np.uint32)

# numpy tracer vs filed scalar
Xv = rand_X(200, 1)
_, dg = trace(Xv)
okn = 0
for i in range(200):
    d = rho.digest_words([0]*8 + [int(w) for w in Xv[i]])
    okn += (d == [int(w) for w in dg[i]])
val["numpy_vs_scalar_ok_of_200"] = okn
print(val)

STEPS = [("R1D1",3),("R1D1",4)] + [("R1D2",q) for q in (1,2,3,4)] + [("R1D3",q) for q in (1,2,3,4)] + [("R2C0",q) for q in (1,2,3,4)] + [("R2C1",q) for q in (1,2,3,4)]

res = {"validation": val, "steps": {}}
base, info = b3steps.build()
alts = {}
for name, kw in (("asc", dict(order="asc")), ("desc", dict(order="desc")), ("lim33", dict(lim=1<<33)), ("lim34", dict(lim=1<<34)), ("lim35", dict(lim=1<<35))):
    t, _ = b3steps.build(**kw); alts[name] = t
# ceiling: skip cost of step
NS = 4096
Xs = rand_X(NS, 7)
snaps_base, dig_base = trace(Xs)
# sensitivity: flip each of 256 bits for 128 samples
NF = 128
Xf = rand_X(NF, 9)
sn0, _ = trace(Xf)
flips = {}
for bit in range(256):
    w, b = divmod(bit, 32)
    X1 = Xf.copy(); X1[:, w] ^= np.uint32(1 << b)
    sn1, _ = trace(X1)
    for key in [(s[0], s[1]) for s in STEPS]:
        a0, d0 = sn0[key]; a1, d1 = sn1[key]
        diff = (a0 ^ a1), (d0 ^ d1)
        flips.setdefault(key, []).append((int((diff[0] != 0).sum()), int((diff[1] != 0).sum()),
                                          float(np.mean([bin(int(z)).count("1") for z in diff[0]])),
                                          float(np.mean([bin(int(z)).count("1") for z in diff[1]]))))
NBIG = 1 << 21
Xb = rand_X(NBIG, 11)
snb, _ = trace(Xb)
for (nm, q) in STEPS:
    key = (nm, q)
    lab = "%s.q%d" % (nm, q)
    fl = flips[key]
    infl_bits = [i for i, f in enumerate(fl) if (f[0] + f[1]) > 0]
    words = sorted(set(i // 32 for i in infl_bits))
    a, d = snb[key]
    pair = a.astype(np.uint64) << np.uint64(32) | d.astype(np.uint64)
    distinct = int(np.unique(pair).size)
    # identity replacement: digest change fraction
    _, dig_skip = trace(Xs[:1024], skip=key)
    changed = int(np.any(dig_skip != dig_base[:1024], axis=1).sum())
    hd = float(np.mean([sum(bin(int(w)).count("1") for w in (dig_skip[i] ^ dig_base[i])) for i in range(1024)]))
    ops = base.ops and sum(base.step_by.get(key if key in base.step_by else (nm, "q%d" % q), {}).values())
    ops_by = base.step_by.get((nm, "q%d" % q), {})
    ops = sum(ops_by.values())
    masks = base.step_masks.get((nm, "q%d" % q), 0)
    sched = 599.0 + 3/16
    gain = -math.log2(1 - 0.9944 * ops / sched)
    alt_rec = {}
    for k, t in alts.items():
        alt_rec[k] = dict(total=t.ops, here=sum(t.step_by.get((nm, "q%d" % q), {}).values()), masks_here=t.step_masks.get((nm, "q%d" % q), 0))
    pre = info[(nm, "q%d" % q)]
    msg = info[(nm, "msg")]
    res["steps"][lab] = dict(ops=ops, ops_by=ops_by, masks=masks, gain_ceiling_bits=gain, pre=pre["pre"], post=pre["post"], msg=msg,
        infl_bits=len(infl_bits), infl_words=[8 + w for w in words] if False else words,
        mean_flip_out0=float(np.mean([f[2] for f in fl if f[0] + f[1] > 0])) if infl_bits else 0.0,
        mean_flip_out1=float(np.mean([f[3] for f in fl if f[0] + f[1] > 0])) if infl_bits else 0.0,
        p_change=float(np.mean([(f[0] + f[1]) / (2.0*NF) for f in fl if f[0] + f[1] > 0])) if infl_bits else 0.0,
        distinct=distinct, N=NBIG, expected_distinct_if_uniform64=NBIG - NBIG*NBIG/2**65,
        skip_changed_of_1024=changed, skip_mean_hd=hd, alts=alt_rec)
    print(lab, ops, ops_by, "infl bits", len(infl_bits), "words", words, "distinct", distinct, "skipchg", changed, flush=True)
res["alts_total"] = {k: t.ops for k, t in alts.items()}
res["base_total"] = base.ops
json.dump(res, open("analysis.json", "w"), indent=1, default=str)
