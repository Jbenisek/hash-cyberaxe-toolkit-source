"""TEST A: low-weight collision characteristics (XOR-linear model with the output fold) by information-set
decoding (Lee-Brickell, p <= 2) on the code  dM -> addition-input differences  restricted to the kernel dout = 0.
Usage: python -B isd.py w setting objective iters seed
  setting   : equal | len   (len = block-length difference allowed in the low 7 bits of v14)
  objective : r1 (round-1 additions; round 0 left to message modification)
              E  (round-1 diagonal calls only; round 0 and round-1 columns assumed pinned/modified)
              all (every addition: plain probability, no message modification)
              gk (GKNWW14 convention: everything except round-0 additions that involve a message word)
Prints the best exact weights found and the breakdown of the best characteristic.
"""
import sys, time, json
import numpy as np
sys.dont_write_bytecode = True
from lin import Model, nullspace, rref, exact_weight


def build(w, setting):
    md = Model(w)
    A = md.out_matrix()
    if setting == "equal":
        lenrows = np.zeros((md.lw, md.nv), dtype=np.uint8)
        for j in range(md.lw):
            lenrows[j, 16 * w + j] = 1
        A = np.vstack([A, lenrows])
    K = nullspace(A)
    return md, K


SEL = {
    "r1": lambda a: a[0] == 1,
    "E": lambda a: a[0] == 1 and a[1][0] == "E",
    "all": lambda a: True,
    "gk": lambda a: not (a[0] == 0 and a[2] in ("x3", "y3")),
}


def breakdown(md, kvec, K, Fall, gall):
    """kvec: 0/1 combination of kernel rows -> full characteristic; per-category exact weights."""
    var = (kvec.astype(np.int64) @ K.astype(np.int64)) & 1
    img = ((Fall.astype(np.int64) @ var) & 1).astype(np.uint8)
    w = md.w
    cat = {}
    for ai, kind, sl in gall:
        r, name, kd, _ = md.adds[ai]
        wt = exact_weight(img, [(ai, kind, sl)], w)
        key = f"r{r}{name}"
        cat[key] = cat.get(key, 0) + wt
    msgw = [i for i in range(16) if var[i * w:(i + 1) * w].any()]
    dm = {i: int("".join(str(int(b)) for b in var[i * w:(i + 1) * w][::-1]), 2) for i in msgw}
    dl = int("".join(str(int(b)) for b in var[16 * w:16 * w + md.lw][::-1]), 2) if md.lw else 0
    r0 = sum(v for k, v in cat.items() if k.startswith("r0"))
    r1 = sum(v for k, v in cat.items() if k.startswith("r1"))
    rE = sum(v for k, v in cat.items() if k.startswith("r1E"))
    r0msg = 0
    for ai, kind, sl in gall:
        if md.adds[ai][0] == 0 and kind in ("x3", "y3"):
            r0msg += exact_weight(img, [(ai, kind, sl)], w)
    return {"dM": {str(k): hex(v) for k, v in dm.items()}, "dlen": dl, "W_all": r0 + r1, "W_r0": r0, "W_r1": r1,
            "W_E": rE, "W_gk": r0 + r1 - r0msg, "per_call": {k: v for k, v in sorted(cat.items()) if v}}


def run(w, setting, objective, iters, seed):
    t0 = time.time()
    md, K = build(w, setting)
    k = K.shape[0]
    F, groups = md.positions(SEL[objective])
    Fall, gall = md.positions(lambda a: True)
    Gc = ((K.astype(np.int64) @ F.T.astype(np.int64)) & 1).astype(np.uint8)
    N = Gc.shape[1]
    rng = np.random.default_rng(seed)
    best = None
    bestrec = None
    hist = []
    for it in range(iters):
        perm = rng.permutation(N)
        M = np.hstack([Gc[:, perm], np.eye(k, dtype=np.uint8)])   # track combination
        R, piv = rref(M)
        piv = [p for p in piv if p < N]
        R = R[: len(piv)]
        rows = R[:, :N]
        combs = R[:, N:]
        # candidates: single rows and pairs; proxy weight = Hamming weight of image
        packed = np.packbits(rows, axis=1)
        wt1 = np.bitwise_count(packed).sum(axis=1)
        cands = [(int(wt1[i]), (i,)) for i in range(len(rows))]
        x = packed[:, None, :] ^ packed[None, :, :]
        wt2 = np.bitwise_count(x).sum(axis=2)
        iu = np.triu_indices(len(rows), 1)
        w2 = wt2[iu]
        order = np.argsort(w2)[:40]
        for o in order:
            cands.append((int(w2[o]), (int(iu[0][o]), int(iu[1][o]))))
        cands.sort()
        for prox, idx in cands[:40]:
            img_perm = np.bitwise_xor.reduce(rows[list(idx)], axis=0)
            img = np.zeros(N, dtype=np.uint8)
            img[perm] = img_perm
            ex = exact_weight(img, groups, w)
            if best is None or ex < best:
                best = ex
                kv = np.bitwise_xor.reduce(combs[list(idx)], axis=0)
                bestrec = breakdown(md, kv, K, Fall, gall)
                bestrec["objective_weight"] = ex
                bestrec["iter"] = it
        hist.append(best)
    out = {"w": w, "setting": setting, "objective": objective, "iters": iters, "seed": seed, "dimK": k,
           "positions": N, "best": best, "best_char": bestrec, "secs": round(time.time() - t0, 1),
           "best_after_iter": {str(i): hist[i] for i in sorted(set([0, 9, 49, 99, 199, 499, 999, iters - 1])) if i < iters}}
    return out


if __name__ == "__main__":
    w, setting, objective, iters, seed = int(sys.argv[1]), sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
    res = run(w, setting, objective, iters, seed)
    print(json.dumps(res))
