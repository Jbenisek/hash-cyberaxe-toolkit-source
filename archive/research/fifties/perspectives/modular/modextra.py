"""Modular lens, part 3 (rand/ train-test split, ctx/ replication, uniform CONTROL). Output: modextra_out.txt.
 G. exact GF(2) affine rank of the low k bits (XOR view) vs the Z/2^k module (modular view): R, Rm, parts
 H. where the strongest modular character of Rm sits (word 3, chi(x) = exp(2 pi i x / 2^20)): the residue it
    concentrates on, and whether that residue is 0 (only mass at 0 helps a collision)
 I. sign vs carry: the E-part XOR key given its modular difference, H(K|M) and H(M|K); best conditional
    probability max_m P(K = d | M = m) against P(K = d) for the most likely XOR keys d (what a filter that pins
    the modular difference could buy on one word)
"""
import sys
sys.dont_write_bytecode = True
import os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
W = ("1", "3", "4", "6")
E1IDX = (0, 2, 3, 1); E3IDX = (2, 0, 1, 3)
rng = np.random.default_rng(0x4D4F44554C415203)


def load(name):
    dig = np.fromfile(os.path.join(DATA, name, "dig.u32"), dtype="<u4").reshape(-1, 8)
    eo = np.fromfile(os.path.join(DATA, name, "eout.u32"), dtype="<u4").reshape(-1, 16)
    d = {"R": dig[:, :4] ^ dig[:, 4:], "Rm": (dig[:, :4] - dig[:, 4:]).astype(np.uint32)}
    d["K1"] = np.stack([eo[:, i] ^ eo[:, 4 + i] for i in E1IDX], 1)
    d["K3"] = np.stack([eo[:, 8 + i] ^ eo[:, 12 + i] for i in E3IDX], 1)
    d["M1"] = np.stack([(eo[:, i] - eo[:, 4 + i]).astype(np.uint32) for i in E1IDX], 1)
    d["M3"] = np.stack([(eo[:, 8 + i] - eo[:, 12 + i]).astype(np.uint32) for i in E3IDX], 1)
    return d


X = load("rand"); Cx = load("ctx")
N = X["R"].shape[0]; H = N // 2
CT = rng.integers(0, 1 << 32, size=(N, 4), dtype=np.uint64).astype(np.uint32)


def sec(t):
    print("\n" + "=" * 100 + "\n" + t + "\n" + "=" * 100)


# ---------------------------------------------------------------------------------------------- G
sec("G. exact GF(2) affine rank of the low k bits of every word (4k-bit vectors; rows XOR row 0; up to 4096 rows)")


def gf2_rank(vecs):
    basis = {}
    for v in vecs:
        while v:
            hb = v.bit_length() - 1
            if hb in basis:
                v ^= basis[hb]
            else:
                basis[hb] = v
                break
    return len(basis)


def lowk_vectors(arr, k, rows=4096):
    m = (1 << k) - 1; out = []
    a = arr[:rows].astype(np.uint64)
    base = None
    for r in range(a.shape[0]):
        v = 0
        for i in range(a.shape[1]):
            v = (v << k) | (int(a[r, i]) & m)
        if base is None:
            base = v; continue
        out.append(v ^ base)
    return out


print("  full = 4k (or 8k for two-part rows). XOR-view rank only; the Z/2^k module of the modular view is in modfourier F.")
for k in (1, 2, 4, 8, 16, 24, 32):
    row = "  k=%2d:" % k
    for nm, arr in (("R", X["R"]), ("Rm", X["Rm"]), ("K1", X["K1"]), ("K3", X["K3"]), ("M1", X["M1"]), ("M3", X["M3"]),
                    ("K1|K3", np.concatenate([X["K1"], X["K3"]], 1)), ("ctrl", CT)):
        full = k * arr.shape[1]
        row += " %s %d/%d" % (nm, gf2_rank(lowk_vectors(arr, k)), full)
    print(row)

# ---------------------------------------------------------------------------------------------- H
sec("H. the strongest modular character of Rm and where its mass sits")
for i, k in ((2, 20), (0, 12), (3, 12), (1, 20), (1, 12)):
    for nm, S, sl in (("train", X, slice(0, H)), ("test", X, slice(H, N)), ("ctx", Cx, slice(None))):
        x = (S["Rm"][sl, i] & np.uint32((1 << k) - 1)).astype(np.float64)
        z = np.exp(2j * np.pi * x / 2 ** k).mean()
        r0 = (np.angle(z) / (2 * np.pi) * 2 ** k) % 2 ** k
        # signed distance of the residue from r0 and from 0, in units of 2^k
        dist0 = np.abs(((x + 2 ** (k - 1)) % 2 ** k) - 2 ** (k - 1)) / 2 ** k
        distr = np.abs(((x - r0 + 2 ** (k - 1)) % 2 ** k) - 2 ** (k - 1)) / 2 ** k
        print("  word %s mod 2^%d [%5s]: |E chi| %.4f  mass centre r0 = %8.0f (%.4f of 2^k)  P(within 1/16 of r0) %.4f  P(within 1/16 of 0) %.4f (uniform 0.125)" % (
            W[i], k, nm, abs(z), r0, r0 / 2 ** k, (distr < 1 / 16).mean(), (dist0 < 1 / 16).mean()))
x = (CT[:, 2] & np.uint32((1 << 20) - 1)).astype(np.float64)
print("  CONTROL mod 2^20: |E chi| %.4f" % abs(np.exp(2j * np.pi * x / 2 ** 20).mean()))
# explanation check: the word-3 residue in terms of the E-part modular differences
for i in range(4):
    s = (X["Rm"][:, i] - X["M1"][:, i] - X["M3"][:, i]).astype(np.uint32)
    z = abs(np.exp(2j * np.pi * (s & 0xFFFFF).astype(np.float64) / 2 ** 20).mean())
    z1 = abs(np.exp(2j * np.pi * (X["M1"][:, i] & 0xFFFFF).astype(np.float64) / 2 ** 20).mean())
    z3 = abs(np.exp(2j * np.pi * (X["M3"][:, i] & 0xFFFFF).astype(np.float64) / 2 ** 20).mean())
    zr = abs(np.exp(2j * np.pi * (X["Rm"][:, i] & 0xFFFFF).astype(np.float64) / 2 ** 20).mean())
    print("  word %s: |E chi_(2^-20)| of Rm %.4f, M1 %.4f, M3 %.4f, carry term Rm-M1-M3 %.4f" % (W[i], zr, z1, z3, z))

# ---------------------------------------------------------------------------------------------- I
sec("I. sign vs carry on the E parts: H(K|M), H(M|K) (plug-in, test half), and what pinning M buys")


def ent(keys):
    _, c = np.unique(keys, return_counts=True)
    p = c / c.sum()
    return -(p * np.log2(p)).sum()


def cond(a, b):  # H(a|b) = H(a,b) - H(b), plug-in
    ab = (a.astype(np.uint64) << np.uint64(32)) | b.astype(np.uint64)
    return ent(ab) - ent(b)


print("  plug-in entropies are biased low when the distinct count nears the row count; read them as lower bounds.")
for part, K, M in (("E1", "K1", "M1"), ("E3", "K3", "M3")):
    for i in range(4):
        k_te, m_te = X[K][H:, i], X[M][H:, i]
        hk, hm = ent(k_te), ent(m_te)
        print("  %s word %s: H(K) %.2f  H(M) %.2f  H(K|M) %.2f  H(M|K) %.2f  [distinct K %d, M %d of %d]" % (
            part, W[i], hk, hm, cond(k_te, m_te), cond(m_te, k_te), len(np.unique(k_te)), len(np.unique(m_te)), len(k_te)))

print("\n  E1 word 1 (a2): top XOR keys d on TRAIN, P(K=d) and max over m of P(K=d | M=m) on TRAIN, then the same m on TEST")
k_tr, m_tr, k_te, m_te = X["K1"][:H, 0], X["M1"][:H, 0], X["K1"][H:, 0], X["M1"][H:, 0]
vals, cnt = np.unique(k_tr, return_counts=True)
for d in vals[np.argsort(cnt)[::-1][:5]]:
    sel = k_tr == d
    ms, mc = np.unique(m_tr[sel], return_counts=True)
    mt, mtc = np.unique(m_tr, return_counts=True)
    tot = dict(zip(mt.tolist(), mtc.tolist()))
    best = max(ms.tolist(), key=lambda m: dict(zip(ms.tolist(), mc.tolist()))[m] / tot[m])
    p_tr = sel.mean(); pc_tr = (k_tr[m_tr == best] == d).mean()
    p_te = (k_te == d).mean(); pc_te = (k_te[m_te == best] == d).mean(); pm_te = (m_te == best).mean()
    print("    d=%08x  #m giving d: %4d  P(K=d) tr %.2e te %.2e | best m=%08x: P(K=d|m) tr %.2e te %.2e (gain %.2f bits)  P(m) te %.2e" % (
        d, len(ms), p_tr, p_te, best, pc_tr, pc_te, np.log2(pc_te / p_te) if pc_te > 0 else float("nan"), pm_te))

print("\n  E1 word 3 (c2) and E3 word 3 (e2): the same, top 3 XOR keys")
for nmK, nmM, i in (("K1", "M1", 1), ("K3", "M3", 1)):
    k_tr, m_tr, k_te, m_te = X[nmK][:H, i], X[nmM][:H, i], X[nmK][H:, i], X[nmM][H:, i]
    vals, cnt = np.unique(k_tr, return_counts=True)
    mt, mtc = np.unique(m_tr, return_counts=True); tot = dict(zip(mt.tolist(), mtc.tolist()))
    for d in vals[np.argsort(cnt)[::-1][:3]]:
        sel = k_tr == d
        ms, mc = np.unique(m_tr[sel], return_counts=True); dm = dict(zip(ms.tolist(), mc.tolist()))
        # require at least 8 train rows of m so the conditional estimate is not a 1/1 artefact
        cand = [m for m in ms.tolist() if tot[m] >= 8]
        if not cand:
            print("    %s d=%08x: no m with >= 8 rows" % (nmK, d)); continue
        best = max(cand, key=lambda m: dm[m] / tot[m])
        p_te = (k_te == d).mean(); sel_te = m_te == best
        pc_te = (k_te[sel_te] == d).mean() if sel_te.any() else float("nan")
        print("    %s d=%08x  #m giving d: %5d  P(K=d) tr %.2e te %.2e | best m=%08x (train rows %d): P(K=d|m) tr %.2e te %.2e (test rows %d)" % (
            nmK, d, len(ms), sel.mean(), p_te, best, tot[best], dm[best] / tot[best], pc_te, int(sel_te.sum())))
