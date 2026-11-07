"""trail_toy.py: research only. Does a differential trail (characteristic) of the residual event R beat the exact
count in the counter arrangement, at toy word size W = 8 (rotations 4/3/2/1)?

Model (transcribed from counter/toy/ctr_toy.c cmd_mass, comp(), ctr_words()):
  E1 = G(v1, v6, v11, v12; m12, m5): c input pair (y11, y11b) differs, m5' = m5 + delta. Free words d1, b1, a2.
  E3 = G(v3, v4, v9, v14; m15=0, m8): a input pair e1 = y3 + Y4, e1b = y3b + Y4. Free words h1, Y9, E (= e1 + w8).
  R: E3 (dg2, de2, dh2) == E1 (da2, dc2, db2) and E3 df2 == ror(dg2, R3).
Counter arrangement: outer step fixes (P = Y12, K = Y1 + w12, J = w5) and (Y4, Y9, E); the inner word d1 runs over D
(heaviest-beta d1 set); h1 = pi(d1) with pi a per-step permutation (taken as random).
  E1 per inner trial: a1 = rol(d1,R1)^P, Y6 = a1 - K, c1 = y11 + d1, b1 = ror(Y6^c1, R2), a2 = a1 + b1 + J.
Constants y11, y11b, delta, y3, y3b are random per seed (the real toy pins are in toy.h, not read: brief).
Usage: python -B trail_toy.py SEED
"""
import sys, time
import numpy as np

W = 8; M = (1 << W) - 1; R1, R2, R3, R4 = 4, 3, 2, 1
U = np.uint32
NK = 1 << (3 * W)


def ror(x, r): return ((x >> r) | (x << (W - r))) & M
def rol(x, r): return ((x << r) | (x >> (W - r))) & M


def lg(x): return float(np.log2(x)) if x > 0 else float("-inf")


seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1
rng = np.random.default_rng(seed)
y11, y11b, delta, y3, y3b = (int(v) for v in rng.integers(0, 256, 5))
while y11b == y11: y11b = int(rng.integers(0, 256))
while y3b == y3: y3b = int(rng.integers(0, 256))
t0 = time.time()
out = []
def say(s):
    print(s, flush=True); out.append(s)

say(f"SEED {seed} W {W} y11 {y11:02x} y11b {y11b:02x} delta {delta:02x} y3 {y3:02x} y3b {y3b:02x}")

# ---------------- E1 table over (d1, b1, a2) ----------------
d = np.arange(256, dtype=U)
D1 = d[:, None, None]; B1 = d[None, :, None]; A2 = d[None, None, :]
c1 = (y11 + D1) & M; c1b = (y11b + D1) & M
Y6 = rol(B1, R2) ^ c1
b1b = ror(Y6 ^ c1b, R2)
a2b = (A2 - B1 + b1b + delta) & M
d2 = ror(D1 ^ A2, R3); c2 = (c1 + d2) & M; b2 = ror(B1 ^ c2, R4)
d2b = ror(D1 ^ a2b, R3); c2b = (c1b + d2b) & M; b2b = ror(b1b ^ c2b, R4)
assert np.all((d2 ^ d2b) == ror(A2 ^ a2b, R3))
key1 = (((A2 ^ a2b) << 16) | ((c2 ^ c2b) << 8) | (b2 ^ b2b)).astype(U)     # (d1, b1, a2)
beta_of = ror(((y11 + d) & M) ^ ((y11b + d) & M), R2)
del c1, c1b, Y6, b1b, a2b, d2, c2, b2, d2b, c2b, b2b

# ---------------- E3 per member ----------------
H = d[:, None, None]; Q9 = d[None, :, None]; EE = d[None, None, :]
def e3(Y4):
    e1 = (y3 + Y4) & M; e1b = (y3b + Y4) & M; dY3 = (e1b - e1) & M
    Y14 = rol(H, R1) ^ e1; h1b = ror(Y14 ^ e1b, R1)
    g1 = (Q9 + H) & M; g1b = (Q9 + h1b) & M
    f1 = ror(Y4 ^ g1, R2); f1b = ror(Y4 ^ g1b, R2)
    e2 = (EE + f1) & M; e2b = (EE + dY3 + f1b) & M
    h2 = ror(H ^ e2, R3); g2 = (g1 + h2) & M; f2 = ror(f1 ^ g2, R4)
    h2b = ror(h1b ^ e2b, R3); g2b = (g1b + h2b) & M; f2b = ror(f1b ^ g2b, R4)
    dC = g2 ^ g2b
    valid = (f2 ^ f2b) == ror(dC, R3)
    k3 = ((dC << 16) | ((e2 ^ e2b) << 8) | (h2 ^ h2b)).astype(U)
    return k3, valid                                                          # axes (h1, Y9, E)

cls_of = np.array([((y3 + Y) & M) ^ ((y3b + Y) & M) for Y in range(256)])
vals, cnts = np.unique(cls_of, return_counts=True)
order = np.argsort(-cnts, kind="stable")
cands = [int(vals[i]) for i in order if cnts[i] >= 4][:8]

best = None; npos = 0
for cv in cands:
    if npos >= 2: break
    mem = [Y for Y in range(256) if cls_of[Y] == cv]
    mass = np.zeros((len(mem), 256), dtype=np.float64); N3s = np.zeros(NK, dtype=np.int64)
    for i, Y in enumerate(mem):
        k3, v = e3(Y)
        N3 = np.bincount(k3[v], minlength=NK)
        N3s += N3
        mass[i] = N3[key1].sum(axis=(1, 2))
    n = len(mem)
    bm = {}
    for x in range(256): bm.setdefault(int(beta_of[x]), []).append(x)
    heavy = max(bm, key=lambda b: (mass[:, bm[b]].sum(), -len(bm[b])))
    D = bm[heavy]
    rate_all = mass.sum() / (n * 2.0 ** 48); rate_D = mass[:, D].sum() / (n * len(D) * 2.0 ** 40)
    say(f"CLASS e1^e1b {cv:02x} eta {ror(cv, R1):02x} n {n} rate/trial filed 2^{lg(rate_all):.2f} ctrH(beta {heavy:02x}, |D| {len(D)}) 2^{lg(rate_D):.2f}")
    npos += rate_D > 0
    if best is None or rate_D > best[0]: best = (rate_D, cv, mem, mass, N3s, D, heavy)
rate_D, cv, mem, mass, N3s, D, heavy = best
if rate_D == 0:
    say("NO class with R mass > 0 for these constants"); open(f"trail_seed{seed}.txt", "w").write("\n".join(out) + "\n"); sys.exit(0)
n = len(mem); nD = len(D)
say(f"CHOSEN class {cv:02x} n {n} beta* {heavy:02x} D {[hex(x) for x in D]}  ({time.time()-t0:.0f}s)")

# ---------------- characteristics (beta*, tau, eps) ----------------
P1D = np.bincount(key1[D].ravel(), minlength=NK) / (nD * 65536.0)            # Pr[E1 out = o | d1 in D]
Q3 = N3s / (n * float(NK))                                                     # Pr[E3 out = o], member uniform
contrib = P1D * Q3
rate0 = contrib.sum()
say(f"BASE rate0 (ctrH exact) 2^{lg(rate0):.3f} (check 2^{lg(rate_D):.3f}); E1 outputs reachable {np.count_nonzero(P1D)}, matched {np.count_nonzero(contrib)}")
top = np.argsort(-contrib)[:5]
for j, o in enumerate(top):
    o = int(o)
    say(f"CHAR{j} tau {o>>16:02x} eps {(o>>8)&M:02x} db2 {o&M:02x}: p(E1|D) 2^{lg(P1D[o]):.2f} p(E3) 2^{lg(Q3[o]):.2f} "
        f"own p/trial 2^{lg(contrib[o]):.2f} = {contrib[o]/rate0:.3f} of rate0")
chi = int(top[0])

# ---------------- E3 side per outer config (Y4, Y9, E) ----------------
rate3 = np.zeros((n, 65536)); F3c = np.zeros((n, 65536)); S3n = np.zeros((n, 65536)); hitS3 = np.zeros((n, 65536))
P1all = np.bincount(key1.ravel(), minlength=NK) / float(NK)                     # Pr[E1 out = o], d1 uniform
for i, Y in enumerate(mem):
    k3, v = e3(Y)
    rate3[i] = np.where(v, P1D[k3], 0.0).mean(axis=0).ravel()
    F3c[i] = (v & (k3 == chi)).mean(axis=0).ravel()
    good = v & (P1all[k3] > 0)                       # S3: h1 whose E3 output some E1 output (any d1) can match
    S3n[i] = good.sum(axis=0).ravel()
    hitS3[i] = np.where(good, P1all[k3], 0.0).sum(axis=0).ravel()
r3 = rate3.ravel(); f3c = F3c.ravel()
# E3-first enumeration: per outer step solve the E3 conditions for h1 (toy: brute force; 32-bit: bitwise DP), map each
# solution back to d1 through the inverse of the per-step permutation, run E1 once. Versus the D-loop (|D| trials).
ps = S3n > 0; hitD = nD * rate3
say(f"E3FIRST rate per uniform trial 2^{lg((P1all*Q3).sum()):.2f} (filed rate); steps with S3 nonempty 2^{lg(ps.mean()):.2f}, "
    f"mean |S3| there {S3n[ps].mean():.2f} (max {int(S3n.max())}) vs |D| {nD}")
say(f"E3FIRST hits per step: E3-first {hitS3.sum()/hitS3.size:.3e}  D-loop {hitD.sum()/hitD.size:.3e}  ratio 2^{lg(hitS3.sum()/hitD.sum()):.2f} "
    f"(formula 2^W*rate_all/(|D|*rate_D) = 2^{lg(256*(P1all*Q3).sum()/(nD*rate0)):.2f}); E1 runs per hit: E3-first "
    f"2^{lg(S3n.sum()/hitS3.sum()):.2f}  D-loop all steps 2^{lg(nD*S3n.size/hitD.sum()):.2f}  D-loop on rate3>0 steps 2^{lg(nD*np.count_nonzero(rate3)/hitD.sum()):.2f}")
assert abs(r3.mean() - rate0) <= 1e-9 * rate0 + 1e-300

def curve(x, qs):
    s = np.sort(x)[::-1]; m = x.mean(); res = []
    for q in qs:
        k = max(1, int(round(q * len(s)))); res.append(s[:k].mean() / m)
    return res

qnec = np.count_nonzero(r3) / len(r3)
qs3 = [qnec * 2.0 ** -j for j in range(0, 9, 2)]
g3 = curve(r3, qs3)
say(f"E3SIDE necessary filter (rate3>0): pass 2^{lg(qnec):.2f}, gain 2^{lg(1/qnec):.2f}; max rate3/rate0 2^{lg(r3.max()/rate0):.2f}")
say("E3SIDE top-q gain over rate0: " + "  ".join(f"q 2^{lg(q):.1f}: 2^{lg(g):.2f}" for q, g in zip(qs3, g3)))
say(f"E3SIDE chi: share of configs with F3(chi)>0 2^{lg(np.count_nonzero(f3c)/len(f3c)):.2f}, mean F3 2^{lg(f3c.mean()):.2f}, "
    f"max 2^{lg(f3c.max()):.2f}, mean|>0 2^{lg(f3c[f3c>0].mean()):.2f}")

# toy analogue of the existing outer filter (STACK conditions (1) and (2), separate existence, same tau)
eta = ror(cv, R1); dY3 = (y3b - y3) & M
def Gt(t): return rol(t ^ ror(t, 1), R2)
mk = np.nonzero(contrib)[0]
pass12 = np.zeros(65536, dtype=bool)
hh = d[:, None]; yy = d[None, :]
for o in mk:
    tau, eps = int(o) >> 16, (int(o) >> 8) & M
    g = Gt(tau); df1 = ror(g, R2)
    ok1 = ((((yy + hh) & M) ^ ((yy + (hh ^ eta)) & M)) == g).any(axis=0)                 # over Y9
    ok2 = ((((yy + hh) & M) ^ ((yy + dY3 + (hh ^ df1)) & M)) == eps).any(axis=0)          # over E (hh = f1)
    pass12 |= (ok1[:, None] & ok2[None, :]).ravel()
q12 = pass12.mean(); kept = rate3[:, pass12].sum() / rate3.sum()
say(f"E3SIDE existing-style filter (1)&(2): pass 2^{lg(q12):.2f} keeps {kept:.4f} of mass, gain 2^{lg(kept/q12):.2f}; "
    f"exact joint filter (rate3>0) pass 2^{lg(qnec):.2f}: extra 2^{lg(q12/qnec):.2f}")

# ---------------- E1 side per outer config (P, K, J), d1 in D ----------------
NC = 1 << 21
P = rng.integers(0, 256, NC).astype(U); K = rng.integers(0, 256, NC).astype(U); J = rng.integers(0, 256, NC).astype(U)
keys = np.empty((nD, NC), dtype=U)
for t, x in enumerate(D):
    a1 = rol(U(x), R1) ^ P; Y6c = (a1 - K) & M; c1x = (y11 + x) & M
    b1 = ror(Y6c ^ c1x, R2); a2 = (a1 + b1 + J) & M
    keys[t] = key1[x, b1, a2]
q3v = Q3[keys]                                                                 # (nD, NC)
r1 = q3v.mean(axis=0)
perm = np.stack([rng.permutation(q3v[t]) for t in range(nD)]); r1s = perm.mean(axis=0)
qs1 = [2.0 ** -j for j in (1, 2, 4, 6, 8, 10)]
say(f"E1SIDE mean rate1/rate0 {r1.mean()/rate0:.4f}; share rate1>0 real 2^{lg(np.count_nonzero(r1)/NC):.2f} shuffled 2^{lg(np.count_nonzero(r1s)/NC):.2f}")
say("E1SIDE top-q gain real/shuffled: " + "  ".join(f"q 2^{lg(q):.0f}: 2^{lg(a):.2f}/2^{lg(b):.2f}" for q, a, b in zip(qs1, curve(r1, qs1), curve(r1s, qs1))))
cnt = (keys == chi).sum(axis=0)
pc = P1D[chi]
h = np.bincount(cnt, minlength=nD + 1) / NC
from math import comb
binom = [comb(nD, k) * pc ** k * (1 - pc) ** (nD - k) for k in range(nD + 1)]
say("E1SIDE chi count per step (real vs binomial): " + "  ".join(f"{k}: {h[k]:.3g}/{binom[k]:.3g}" for k in range(min(nD, 6) + 1)))

# which outer bits carry the E1 structure: rate1 variance explained by J alone, by (P,K) low/high nibbles
def explained(x, lab, nlab):
    s = np.bincount(lab, weights=x, minlength=nlab); c = np.bincount(lab, minlength=nlab)
    mu = np.where(c > 0, s / np.maximum(c, 1), 0)
    return float(((mu[lab] - x.mean()) ** 2).mean() / x.var())
say(f"E1SIDE variance share: J {explained(r1, J.astype(np.int64), 256):.3f}  P {explained(r1, P.astype(np.int64), 256):.3f}  "
    f"K {explained(r1, K.astype(np.int64), 256):.3f}  (K,J low nibbles) {explained(r1, ((K & 15) * 16 + (J & 15)).astype(np.int64), 256):.3f}"
    f"  [shuffled J {explained(r1s, J.astype(np.int64), 256):.3f}]")

# J chosen per (P, K) (only possible if w5 is enumerated after P, K are known)
NPK = 4096
Pp = rng.integers(0, 256, NPK).astype(U)[:, None]; Kp = rng.integers(0, 256, NPK).astype(U)[:, None]; Jp = d[None, :]
acc = np.zeros((NPK, 256))
for x in D:
    a1 = rol(U(x), R1) ^ Pp; Y6c = (a1 - Kp) & M; b1 = ror(Y6c ^ ((y11 + x) & M), R2); a2 = (a1 + b1 + Jp) & M
    acc += Q3[key1[x, np.broadcast_to(b1, a2.shape), a2]]
acc /= nD
accs = np.zeros((NPK, 256))                                                    # control: (b1, a1+b1) random per d
for x in D:
    b1 = rng.integers(0, 256, (NPK, 1)).astype(U); s = rng.integers(0, 256, (NPK, 1)).astype(U)
    accs += Q3[key1[x, np.broadcast_to(b1, (NPK, 256)), (s + Jp) & M]]
accs /= nD
srs = np.sort(accs, axis=1)[:, ::-1]
say("JCHOICE control (no structure): " + "  ".join(f"top {k}/256: 2^{lg(srs[:, :k].mean()/accs.mean()):.2f}" for k in (1, 16, 64)))
srt = np.sort(acc, axis=1)[:, ::-1]
say("JCHOICE gain if J picked per (P,K): " + "  ".join(f"top {k}/256 of J: 2^{lg(srt[:, :k].mean()/acc.mean()):.2f}" for k in (1, 16, 64)))

# ---------------- joint selection: rate = sum_o P1sel(o) * F3sel(o) ----------------
sup = np.nonzero(P1D)[0]
def p1sel(mask):
    k = keys[:, mask].ravel(); return np.bincount(np.searchsorted(sup, k), minlength=len(sup)) / k.size
th3 = {"all": -1.0, "nec": 0.0}
s3 = np.sort(r3)[::-1]
for j in (2, 4, 6):
    kk = max(1, int(round(qnec * 2.0 ** -j * len(s3)))); th3[f"nec/2^{j}"] = s3[kk - 1]
th3["chi>0"] = None
th3["exist12"] = "x"
F3sel = {kname: np.zeros(len(sup)) for kname in th3}; n3sel = {kname: 0 for kname in th3}
for i, Y in enumerate(mem):
    k3, v = e3(Y)
    k3 = k3.reshape(256, 65536); v = v.reshape(256, 65536)
    for kname, t in th3.items():
        m = (F3c[i] > 0) if t is None else pass12 if t == "x" else (rate3[i] > 0) if t == 0.0 else (rate3[i] >= t)
        if not m.any(): continue
        kk = k3[:, m][v[:, m]]
        idx = np.searchsorted(sup, kk); ok = (idx < len(sup)) & (sup[np.minimum(idx, len(sup) - 1)] == kk)
        F3sel[kname] += np.bincount(idx[ok], minlength=len(sup)); n3sel[kname] += 256 * int(m.sum())
for kname in th3: F3sel[kname] /= max(n3sel[kname], 1)
s1 = np.sort(r1)[::-1]
sel1 = {"all": np.ones(NC, bool), "r1>0": r1 > 0, "chi>=1": cnt >= 1}
base_nec = None
for a, m1 in sel1.items():
    q1 = m1.mean(); P1s = p1sel(m1); row = []
    for b in th3:
        q3 = n3sel[b] / (256.0 * n * 65536)
        rt = float((P1s * F3sel[b]).sum())
        if a == "all" and b == "nec": base_nec = rt
        row.append(f"{b}: q3 2^{lg(q3):.1f} r/r0 2^{lg(rt/rate0):.2f}")
    say(f"JOINT sel1 {a} (q1 2^{lg(q1):.1f}) | " + " | ".join(row))
say(f"DONE {time.time()-t0:.0f}s")
open(sys.argv[2] if len(sys.argv) > 2 else f"trail_seed{seed}.txt", "w").write("\n".join(out) + "\n")
