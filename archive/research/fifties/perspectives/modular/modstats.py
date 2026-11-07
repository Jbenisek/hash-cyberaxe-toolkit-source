"""Modular lens on the front-line residual (perspectives/data). Read-only use of ../data.

For each residual word w in (1,3,4,6):
  R   = digA ^ digB            (XOR view, as stored in res.u32)
  Rm  = digA - digB mod 2^32   (modular view)
  M1  = E1A - E1B mod 2^32, M3 = E3A - E3B mod 2^32 (modular parts; XOR parts are K1, K3)
Every statistic is also computed on a CONTROL of uniform random u32 words of the same shape (fixed seed),
and every location picked on the TRAIN half (rand rows [0, 2^19)) is re-measured on the TEST half
(rand rows [2^19, 2^20)) and on ctx/ (a third set). Output: modstats_out.txt (stdout).
"""
import sys
sys.dont_write_bytecode = True
import os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
W = ("1", "3", "4", "6")
# digest word w = E1 word ^ E3 word; indices into E1 (a2 b2 c2 d2) and E3 (e2 f2 g2 h2)
E1IDX = (0, 2, 3, 1)   # word1 <- a2, word3 <- c2, word4 <- d2, word6 <- b2
E3IDX = (2, 0, 1, 3)   # word1 <- g2, word3 <- e2, word4 <- f2, word6 <- h2
M32 = np.uint64(0xFFFFFFFF)
rng = np.random.default_rng(0x4D4F44554C415201)


def load(name):
    d = {}
    for f, c in (("dig", 8), ("eout", 16), ("emid", 16), ("keys", 8), ("res", 4), ("inputs", 12)):
        d[f] = np.fromfile(os.path.join(DATA, name, f + ".u32"), dtype="<u4").reshape(-1, c)
    return d


def hw32(a):
    a = np.ascontiguousarray(a.astype(np.uint32))
    return np.unpackbits(a.view(np.uint8).reshape(-1, 4), axis=1).sum(1)


def naf_w(x):
    """minimal signed-digit (NAF) weight of x modulo 2^32: min over the representatives x and x - 2^32."""
    x = x.astype(np.uint64)
    def w(v):
        d = ((v ^ (np.uint64(3) * v)) >> np.uint64(1)) & M32
        return hw32(d.astype(np.uint32))
    return np.minimum(w(x), w((np.uint64(1 << 32) - x) & M32))


def h2_pairs(v):
    """collision entropy estimate from colliding pairs: H2 = log2(C(n,2)/pairs); pairs==0 -> lower bound."""
    _, c = np.unique(v, return_counts=True)
    n = len(v)
    pairs = float((c.astype(np.float64) * (c - 1) / 2).sum())
    tot = n * (n - 1) / 2
    return len(c), pairs, (np.log2(tot / pairs) if pairs > 0 else float("inf"))


def plugin_H(v, nbins):
    c = np.bincount(v, minlength=nbins).astype(np.float64)
    n = c.sum(); p = c[c > 0] / n
    H = -(p * np.log2(p)).sum()
    mm = (np.count_nonzero(c) - 1) / (2 * n * np.log(2))     # Miller-Madow correction
    return H + mm


def bit_probs(a):
    return ((a[:, None] >> np.arange(32, dtype=np.uint32)) & 1).mean(0)


def h_bin(p):
    p = np.clip(p, 1e-12, 1 - 1e-12)
    return -(p * np.log2(p) + (1 - p) * np.log2(1 - p))


def parts(d):
    digA, digB = d["dig"][:, :4], d["dig"][:, 4:]
    e = d["eout"]
    E1A, E1B, E3A, E3B = e[:, 0:4], e[:, 4:8], e[:, 8:12], e[:, 12:16]
    x = {}
    x["R"] = d["res"]
    x["Rm"] = (digA - digB).astype(np.uint32)
    x["K1"] = np.stack([E1A[:, i] ^ E1B[:, i] for i in E1IDX], 1)
    x["K3"] = np.stack([E3A[:, i] ^ E3B[:, i] for i in E3IDX], 1)
    x["M1"] = np.stack([(E1A[:, i] - E1B[:, i]).astype(np.uint32) for i in E1IDX], 1)
    x["M3"] = np.stack([(E3A[:, i] - E3B[:, i]).astype(np.uint32) for i in E3IDX], 1)
    x["a"] = np.stack([E1A[:, i] for i in E1IDX], 1); x["aB"] = np.stack([E1B[:, i] for i in E1IDX], 1)
    x["g"] = np.stack([E3A[:, i] for i in E3IDX], 1); x["gB"] = np.stack([E3B[:, i] for i in E3IDX], 1)
    x["digA"], x["digB"] = digA, digB
    return x


def sec(t):
    print("\n" + "=" * 100 + "\n" + t + "\n" + "=" * 100)


rand, ctx = load("rand"), load("ctx")
N = rand["res"].shape[0]; H = N // 2
X = parts(rand); C = parts(ctx)
TR = {k: v[:H] for k, v in X.items()}; TE = {k: v[H:] for k, v in X.items()}
CTRL = rng.integers(0, 1 << 32, size=(N, 4), dtype=np.uint64).astype(np.uint32)
CTRL2 = rng.integers(0, 1 << 32, size=(N, 4), dtype=np.uint64).astype(np.uint32)
print("rows rand %d (train %d / test %d), ctx %d; control = uniform u32, same shape, seed 0x4D4F44554C415201" % (
    N, H, N - H, C["R"].shape[0]))

# ---------------------------------------------------------------------------------------------- 0. identities
sec("0. identities (COMPUTED on every row of rand and ctx)")
for nm, S in (("rand", X), ("ctx", C)):
    z_x = np.all((S["R"] == 0) == (S["Rm"] == 0))
    lowk = all(np.array_equal((S["R"] & np.uint32((1 << k) - 1)) == 0, (S["Rm"] & np.uint32((1 << k) - 1)) == 0)
               for k in range(1, 32))
    lsb = np.array_equal(S["R"] & 1, S["Rm"] & 1)
    xr = np.array_equal(S["R"], S["K1"] ^ S["K3"])
    m_lsb = np.array_equal(S["Rm"] & 1, (S["M1"] + S["M3"]) & 1)
    m1w1 = np.all(S["M1"][:, 0] % 16 == 0)
    print("  [%s] R==0 <=> Rm==0 per word: %s | low-k zero sets equal for all k<32: %s | lsb(R)==lsb(Rm): %s" % (
        nm, z_x, lowk, lsb))
    print("  [%s] R == K1^K3 exactly: %s | Rm == M1+M3 mod 2: %s | M1 word1 == 0 mod 16: %s" % (nm, xr, m_lsb, m1w1))

# ---------------------------------------------------------------------------------------------- 1. per-word
sec("1. per word: distinct, collision entropy H2 (all 2^20 rand rows), bit bias, independent-bit entropy deficit")
print("  H2 from colliding pairs; uniform 32-bit expects ~128 pairs -> H2 ~ 32.0. bias = |P(bit=1)-1/2|.")
print("  deficit = sum_b (1 - h(p_b)) bits (independent-bit model). max bias: location chosen on TRAIN, value on TEST.")
print("  %-6s %-4s %9s %9s %7s | %-22s %-8s | %8s %8s" % ("view", "word", "distinct", "pairs", "H2", "maxbias train(bit)", "test", "deficit", "ctx_def"))
for view in ("R", "Rm", "K1", "K3", "M1", "M3", "CTRL"):
    for i in range(4):
        full = CTRL[:, i] if view == "CTRL" else X[view][:, i]
        tr, te = full[:H], full[H:]
        cx = CTRL2[:H, i] if view == "CTRL" else C[view][:, i]
        dist, pairs, h2 = h2_pairs(full)
        ptr, pte = bit_probs(tr), bit_probs(te)
        b = int(np.abs(ptr - .5).argmax())
        dfull = (1 - h_bin(bit_probs(full))).sum(); dctx = (1 - h_bin(bit_probs(cx))).sum()
        print("  %-6s %-4s %9d %9.0f %7.2f | %.4f (b%2d)          %.4f   | %8.3f %8.3f" % (
            view, W[i], dist, pairs, h2, abs(ptr[b] - .5), b, abs(pte[b] - .5), dfull, dctx))

# ---------------------------------------------------------------------------------------------- 2. NAF / HW
sec("2. signed-digit weight: XOR Hamming weight of R vs NAF weight of Rm (and of the signed value), vs control")
print("  NAF weight is min over the representatives x, x-2^32. control: uniform u32 (NAF of uniform; HW of uniform).")
nafc = np.stack([naf_w(CTRL[:, i]) for i in range(4)], 1)
hwc = np.stack([hw32(CTRL[:, i]) for i in range(4)], 1)
for i in range(4):
    hR = hw32(X["R"][:, i]); nR = naf_w(X["Rm"][:, i])
    # NAF weight can never exceed the XOR weight (the signed XOR difference is a signed-digit form of Rm)
    gap = hR.astype(int) - nR.astype(int)
    print("  word %s: mean HW(R) %.3f (ctrl %.3f) | mean NAF(Rm) %.3f (ctrl %.3f) | min NAF %d | NAF<=HW all rows: %s | mean HW-NAF %.3f" % (
        W[i], hR.mean(), hwc[:, i].mean(), nR.mean(), nafc[:, i].mean(), nR.min(), bool((gap >= 0).all()), gap.mean()))
tot_naf = sum(naf_w(X["Rm"][:, i]).astype(int) for i in range(4))
tot_hw = sum(hw32(X["R"][:, i]).astype(int) for i in range(4))
tot_nafc = nafc.astype(int).sum(1); tot_hwc = hwc.astype(int).sum(1)
print("  128-bit totals: mean HW(R) %.2f (ctrl %.2f), min %d (ctrl min %d) | mean NAF(Rm) %.2f (ctrl %.2f), min %d (ctrl min %d)" % (
    tot_hw.mean(), tot_hwc.mean(), tot_hw.min(), tot_hwc.min(), tot_naf.mean(), tot_nafc.mean(), tot_naf.min(), tot_nafc.min()))
for thr in (20, 24, 28):
    print("  P(total NAF <= %d): data %.3e  ctrl %.3e | P(total HW <= %d): data %.3e ctrl %.3e" % (
        thr, (tot_naf <= thr).mean(), (tot_nafc <= thr).mean(), thr + 16, (tot_hw <= thr + 16).mean(), (tot_hwc <= thr + 16).mean()))

# ---------------------------------------------------------------------------------------------- 3. magnitude
sec("3. signed magnitude of Rm: P(|Rm| < 2^m) per word vs uniform 2^(m-31) (is the modular residual small?)")
for i in range(4):
    s = X["Rm"][:, i].view(np.int32).astype(np.int64); a = np.abs(s)
    sc = CTRL[:, i].view(np.int32).astype(np.int64); ac = np.abs(sc)
    row = []
    for m in (20, 24, 26, 28, 30):
        row.append("m=%d %.2e/%.2e(c %.2e)" % (m, (a < (1 << m)).mean(), 2.0 ** (m - 31), (ac < (1 << m)).mean()))
    print("  word %s: " % W[i] + "  ".join(row) + "  | frac Rm>0 (signed) %.4f" % (s > 0).mean())

# ---------------------------------------------------------------------------------------------- 4. low/top k-bit entropy
sec("4. plug-in entropy (Miller-Madow) of the low k bits / top k bits, per word and jointly, TRAIN vs TEST vs CONTROL")
def lowk(a, k): return (a & np.uint32((1 << k) - 1)).astype(np.int64)
def topk(a, k): return (a >> np.uint32(32 - k)).astype(np.int64)
print("  per word, k bits (entropy deficit = k - H; control deficit shows estimator bias at this sample size):")
for k in (4, 8, 12, 16):
    for fn, nm in ((lowk, "low"), (topk, "top")):
        line = "  k=%2d %-3s" % (k, nm)
        for i in range(4):
            dR = k - plugin_H(fn(TE["R"][:, i], k), 1 << k)
            dM = k - plugin_H(fn(TE["Rm"][:, i], k), 1 << k)
            dC = k - plugin_H(fn(CTRL[H:, i], k), 1 << k)
            line += " | w%s R %.4f Rm %.4f ctrl %.4f" % (W[i], dR, dM, dC)
        print(line)
print("  jointly, low k bits of all four words (4k bits), deficit = 4k - H on TEST half; P(all 4k bits zero) on all rand:")
for k in (1, 2, 3, 4, 5):
    def joint(a, fn=lowk):
        v = np.zeros(a.shape[0], np.int64)
        for i in range(4):
            v = (v << k) | fn(a[:, i], k)
        return v
    hR = plugin_H(joint(TE["R"]), 1 << 4 * k); hM = plugin_H(joint(TE["Rm"]), 1 << 4 * k)
    hC = plugin_H(joint(CTRL[H:]), 1 << 4 * k)
    hT = plugin_H(joint(TE["Rm"], topk), 1 << 4 * k); hTC = plugin_H(joint(CTRL[H:], topk), 1 << 4 * k)
    z = (joint(X["R"]) == 0).mean()
    print("  k=%d (%2d bits): low R %.4f  low Rm %.4f  ctrl %.4f | top-k Rm %.4f ctrl %.4f | P(low zero) %.3e vs 2^-%d=%.3e" % (
        k, 4 * k, 4 * k - hR, 4 * k - hM, 4 * k - hC, 4 * k - hT, 4 * k - hTC, z, 4 * k, 2.0 ** (-4 * k)))

# ---------------------------------------------------------------------------------------------- 5. zero curves
sec("5. coordinate-free anchor: -log2 P(low k bits of word w are zero) (same set in XOR and modular coordinates)")
print("  rand all rows; ctx in brackets. uniform = k. 'excess' = k - (-log2 P).")
for i in range(4):
    out = []
    for k in (4, 8, 12, 14, 16, 18):
        m = np.uint32((1 << k) - 1)
        p = ((X["R"][:, i] & m) == 0).mean(); pc = ((C["R"][:, i] & m) == 0).mean()
        out.append("k%d %.2f[%.2f]" % (k, -np.log2(p) if p > 0 else 99, -np.log2(pc) if pc > 0 else 99))
    print("  word %s: " % W[i] + "  ".join(out))

# ---------------------------------------------------------------------------------------------- 6. split combination
sec("6. do the modular parts combine simply? R = K1^K3 always; Rm vs M1 (+/-) M3")
print("  DERIVED: x^y = x + y - 2(x&y), so Rm - M1 - M3 = -2*((aA&gA) - (aB&gB)) mod 2^32; exact iff aA&gA == aB&gB.")
print("  v2 = 2-adic valuation of (Rm - M1 - M3): the modular split holds mod 2^v2. control: uniform aA,gA,aB,gB.")
cA, cG, cAB, cGB = (rng.integers(0, 1 << 32, size=N, dtype=np.uint64).astype(np.uint32) for _ in range(4))
def v2(x):
    x = x.astype(np.uint64); out = np.full(x.shape, 32)
    nz = x != 0
    low = x[nz] & (~x[nz] + np.uint64(1))
    out[nz] = np.log2(low.astype(np.float64)).astype(int)
    return out
for i in range(4):
    e = (X["Rm"][:, i] - X["M1"][:, i] - X["M3"][:, i]).astype(np.uint32)
    e2 = (X["Rm"][:, i] - X["M1"][:, i] + X["M3"][:, i]).astype(np.uint32)
    ec = (((cA ^ cG) - (cAB ^ cGB)) - (cA - cAB) - (cG - cGB)).astype(np.uint32)
    vv, vc = v2(e), v2(ec)
    print("  word %s: P(Rm==M1+M3) %.3e (ctrl %.3e)  P(Rm==M1-M3) %.3e | mean v2 %.2f (ctrl %.2f) | P(v2>=8) %.4f (ctrl %.4f)" % (
        W[i], (e == 0).mean(), (ec == 0).mean(), (e2 == 0).mean(), vv.mean(), vc.mean(), (vv >= 8).mean(), (vc >= 8).mean()))
# MITM consequence: is Rm a function of (M1, M3)? count rows with equal (M1,M3) on a word but different Rm
for i in range(4):
    key = (X["M1"][:, i].astype(np.uint64) << np.uint64(32)) | X["M3"][:, i].astype(np.uint64)
    o = np.argsort(key, kind="stable"); ks = key[o]; rs = X["Rm"][o, i]
    same = ks[1:] == ks[:-1]
    print("  word %s: rows sharing (M1,M3) with a neighbour: %d ; of those, Rm differs: %d | rows sharing (K1,K3): R differs never (identity)" % (
        W[i], int(same.sum()), int((same & (rs[1:] != rs[:-1])).sum())))

# ---------------------------------------------------------------------------------------------- 7. part entropies
sec("7. E-part differences in three coordinates: XOR (K), modular (M), signed-bit (BSD = XOR pattern + signs)")
print("  H2 from colliding pairs on all 2^20 rand rows (uniform 32-bit ~32, 64-bit key: no pairs expected).")
e = rand["eout"]; m = rand["emid"]
labs1 = ("a", "b", "c", "d"); labs3 = ("e", "f", "g", "h")
for half, arr in (("mid", m), ("out", e)):
    for side, lab, off in (("E1", labs1, 0), ("E3", labs3, 8)):
        for q in range(4):
            A_, B_ = arr[:, off + q], arr[:, off + 4 + q]
            xd = A_ ^ B_; md = (A_ - B_).astype(np.uint32)
            bsd = (xd.astype(np.uint64) << np.uint64(32)) | (A_ & xd).astype(np.uint64)
            dx, _, hx = h2_pairs(xd); dm, _, hm = h2_pairs(md); db, _, hb = h2_pairs(bsd)
            top_m = np.unique(md, return_counts=True); jm = top_m[1].argmax()
            top_x = np.unique(xd, return_counts=True); jx = top_x[1].argmax()
            print("  %s %s.%s%s: XOR distinct %7d H2 %6.2f top %08x p=%.4f | MOD distinct %7d H2 %6.2f top %08x p=%.4f | BSD distinct %7d H2 %6.2f" % (
                half, side, lab[q], "1" if half == "mid" else "2", dx, hx, top_x[0][jx], top_x[1][jx] / N,
                dm, hm, top_m[0][jm], top_m[1][jm] / N, db, hb))
