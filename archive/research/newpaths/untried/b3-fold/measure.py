"""Fold-level event vs 'both differences zero' on REAL pinned 55/63 pairs of 2-round BLAKE3.

For each residual digest word w in {1,3,4,6}: h_w = Z_w ^ Z_{w+8}, with
  w=1: Z1 = E1.a, Z9 = E3.c   w=3: Z3 = E3.a, Z11 = E1.c
  w=4: Z4 = E3.b, Z12 = E1.d  w=6: Z6 = E1.b, Z14 = E3.d
dp = dZ_w (XOR difference A vs B), dq = dZ_{w+8}.
  fold event   : dp == dq            (identical to dh_w == 0, the front line's success test)
  both-zero    : dp == 0 and dq == 0
On the low k bits for k in KS; cross-pair (independence) prediction from value histograms.
Usage: python -B measure.py LOG2N [seed]
"""
import json
import sys
import time
import numpy as np
import b3fold_gen as g

U = np.uint32
LOG2N = int(sys.argv[1]) if len(sys.argv) > 1 else 20
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 2026
B = min(1 << 20, 1 << LOG2N)
NB = (1 << LOG2N) // B
N = NB * B
KS = [4, 8, 12, 16, 20, 24, 32]
WORDS = [1, 3, 4, 6]
NAMES = {1: ("E1.a", "E3.c"), 3: ("E3.a", "E1.c"), 4: ("E3.b", "E1.d"), 6: ("E1.b", "E3.d")}
JK = [1, 2, 3, 4, 5, 6, 8]


def mask(k):
    return U(0xFFFFFFFF if k == 32 else (1 << k) - 1)


t0 = time.time()
cnt = {w: {k: dict(fold=0, both=0, zp=0, zq=0) for k in KS} for w in WORDS}
joint = {k: 0 for k in JK}
chk = dict(lemmaL_bad=0, pins_bad=0, c3_bad=0, half_bad=0, half_bothzero=0, ident_bad=0,
           e1_out_zero=0, e3_out_zero=0, resid_all_bothzero=0, resid_fold_full=0,
           e1_d_identity_bad=0, e3only_identity_bad=0, e1eta_identity_bad=0,
           parity_dB1_even=0, parity_db1_dD1_even=0)
alg = {"w4p": {k: 0 for k in KS}, "w6p": {k: 0 for k in KS}}
alg_vals = {"w4p": [], "w6p": []}
dps = {w: [] for w in WORDS}
dqs = {w: [] for w in WORDS}
C3A = (0x8127C181, 0x76F7AEFD, 0x7AF77F38, 0xBBFBDFFE)
C3B = (0x7EDF3E7E, 0x76F7AEFD, 0x850000C3, 0xBBFBDFFE)

for bi in range(NB):
    rng = np.random.default_rng([SEED, bi])
    F = rng.integers(0, 2**32, size=(9, B), dtype=U)
    WA, WB, tl = g.build_pairs_v(F)
    ZA, XA = g.compress2_v(WA, tl, g.LEN_A, keep_round0=True)
    ZB, XB = g.compress2_v(WB, tl, g.LEN_B, keep_round0=True)
    neq = np.zeros(B, dtype=bool)
    for i in range(16):
        neq |= XA[i] != XB[i]
    chk["lemmaL_bad"] += int(neq.sum())
    pin_bad = (XA[3] != g.X3P) | (XA[7] != g.X7P) | (XA[11] != g.X11P) | (XA[15] != g.X15P)
    chk["pins_bad"] += int(pin_bad.sum())
    ca = g.Gv(XA[3], XA[7], XA[11], XA[15], WA[4], WA[13])
    cb = g.Gv(XB[3], XB[7], XB[11], XB[15], WB[4], WB[13])
    c3bad = np.zeros(B, dtype=bool)
    for j in range(4):
        c3bad |= (ca[j] != C3A[j]) | (cb[j] != C3B[j])
    chk["c3_bad"] += int(c3bad.sum())
    hb = np.zeros(B, dtype=bool)
    hz = np.ones(B, dtype=bool)
    for w in (0, 2, 5, 7):
        hb |= (ZA[w] ^ ZA[w + 8]) != (ZB[w] ^ ZB[w + 8])
        hz &= (ZA[w] == ZB[w]) & (ZA[w + 8] == ZB[w + 8])
    chk["half_bad"] += int(hb.sum())
    chk["half_bothzero"] += int(hz.sum())
    d = {i: ZA[i] ^ ZB[i] for i in (1, 3, 4, 6, 9, 11, 12, 14)}
    chk["e1_out_zero"] += int(((d[1] | d[6] | d[11] | d[12]) == 0).sum())
    chk["e3_out_zero"] += int(((d[3] | d[4] | d[9] | d[14]) == 0).sum())
    allz = np.ones(B, dtype=bool)
    rfull = np.ones(B, dtype=bool)
    jm = {k: np.ones(B, dtype=bool) for k in JK}
    for w in WORDS:
        dp, dq = d[w], d[w + 8]
        dh = (ZA[w] ^ ZA[w + 8]) ^ (ZB[w] ^ ZB[w + 8])
        chk["ident_bad"] += int(((dh == 0) != (dp == dq)).sum())
        x = dp ^ dq
        allz &= (dp == 0) & (dq == 0)
        rfull &= x == 0
        for k in KS:
            m = mask(k)
            zp = (dp & m) == 0
            zq = (dq & m) == 0
            c = cnt[w][k]
            c["fold"] += int(((x & m) == 0).sum())
            c["both"] += int((zp & zq).sum())
            c["zp"] += int(zp.sum())
            c["zq"] += int(zq.sum())
        for k in JK:
            jm[k] &= (x & mask(k)) == 0
        dps[w].append(dp.copy())
        dqs[w].append(dq.copy())
    chk["resid_all_bothzero"] += int(allz.sum())
    chk["resid_fold_full"] += int(rfull.sum())
    for k in JK:
        joint[k] += int(jm[k].sum())
    # ---- fold algebra: exact identities (PROVED by hand; checked here) and the two derived words
    chk["e1_d_identity_bad"] += int((d[12] != g.rv(d[1], 8)).sum())          # dZ12 = ROR(dZ1, 8)
    r1, r3, r4, r6 = d[1] ^ d[9], d[3] ^ d[11], d[4] ^ d[12], d[6] ^ d[14]  # digest residual words
    w4p = r4 ^ g.rv(r1, 8)          # E3-only word
    w6p = r6 ^ g.rv(r3, 8)          # E1 + eta word
    dB1 = g.lv(d[4], 7) ^ d[9]      # E3 first-half b difference
    db1 = g.lv(d[6], 7) ^ d[11]     # E1 first-half b difference
    dD1 = g.lv(d[14], 8) ^ d[3]     # E3 first-half d difference (eta)
    Lz9 = d[9] ^ g.rv(d[9], 1)
    Lz11 = d[11] ^ g.rv(d[11], 1)
    chk["e3only_identity_bad"] += int((w4p != g.rv(dB1 ^ Lz9, 7)).sum())
    chk["e1eta_identity_bad"] += int((w6p != g.rv(db1 ^ g.rv(dD1, 1) ^ Lz11, 7)).sum())
    chk["parity_dB1_even"] += int(((np.bitwise_count(dB1) & 1) == 0).sum())
    chk["parity_db1_dD1_even"] += int(((np.bitwise_count(db1 ^ dD1) & 1) == 0).sum())
    for k in KS:
        m = mask(k)
        alg["w4p"][k] += int(((w4p & m) == 0).sum())
        alg["w6p"][k] += int(((w6p & m) == 0).sum())
    alg_vals["w4p"].append(w4p.copy())
    alg_vals["w6p"].append(w6p.copy())
t_gen = time.time() - t0

# cross-pair (independence) predictions from value histograms
cross = {w: {} for w in WORDS}
top = {}
for w in WORDS:
    dp = np.concatenate(dps[w]); dq = np.concatenate(dqs[w])
    for k in KS:
        same_f = cnt[w][k]["fold"]; same_b = cnt[w][k]["both"]
        if k <= 24:
            m = int(mask(k))
            hp = np.bincount((dp & U(m)).astype(np.int64), minlength=1 << k).astype(np.float64)
            hq = np.bincount((dq & U(m)).astype(np.int64), minlength=1 << k).astype(np.float64)
            sfold = float(np.dot(hp, hq)); sboth = hp[0] * hq[0]
        else:
            vp, np_ = np.unique(dp, return_counts=True)
            vq, nq_ = np.unique(dq, return_counts=True)
            common, ip, iq = np.intersect1d(vp, vq, assume_unique=True, return_indices=True)
            prod = np_[ip].astype(np.float64) * nq_[iq].astype(np.float64)
            sfold = float(prod.sum())
            hp0 = float(np_[vp == 0].sum()); hq0 = float(nq_[vq == 0].sum())
            sboth = hp0 * hq0
            order = np.argsort(-prod)[:6]
            top[w] = [(f"{int(common[o]):08x}", int(np_[ip[o]]), int(nq_[iq[o]]), float(prod[o] / max(sfold, 1)))
                      for o in order]
            cross[w]["distinct_dp"] = int(vp.size); cross[w]["distinct_dq"] = int(vq.size)
            cross[w]["max_count_dp"] = int(np_.max()); cross[w]["max_count_dq"] = int(nq_.max())
        pairs = float(N) * (N - 1)
        cross[w][k] = dict(fold=(sfold - same_f) / pairs, both=(sboth - same_b) / pairs)

w4all = np.concatenate(alg_vals["w4p"]); w6all = np.concatenate(alg_vals["w6p"])
alg_joint = {k: int((((w4all & mask(k)) == 0) & ((w6all & mask(k)) == 0)).sum()) for k in KS}
alg_top = {}
for nm, arr in (("w4p", w4all), ("w6p", w6all)):
    v, c = np.unique(arr, return_counts=True)
    o = np.argsort(-c)[:5]
    alg_top[nm] = dict(distinct=int(v.size), top=[(f"{int(v[i]):08x}", int(c[i])) for i in o])
out = dict(N=N, log2N=LOG2N, seed=SEED, seconds=round(time.time() - t0, 1), gen_seconds=round(t_gen, 1),
           checks=chk, counts={str(w): {str(k): v for k, v in cnt[w].items()} for w in WORDS},
           cross={str(w): {str(k): v for k, v in cross[w].items()} for w in WORDS},
           joint_low_bits={str(k): joint[k] for k in JK}, top_full_width=top,
           fold_algebra=dict(w4p={str(k): v for k, v in alg["w4p"].items()},
                             w6p={str(k): v for k, v in alg["w6p"].items()},
                             w4p_and_w6p={str(k): v for k, v in alg_joint.items()}, top=alg_top))
import os
base = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"measure_out_n{LOG2N}_s{SEED}")
with open(base + ".json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, indent=1)


def lg(c, n):
    return f"{np.log2(c / n):7.2f}" if c > 0 else "   -inf"


lines = [f"N = 2^{LOG2N} = {N} real pinned pairs, seed {SEED}, {out['seconds']} s", f"checks: {chk}", ""]
lines.append("per word: log2 rates on the low k bits (same pair = real event; cross = independence prediction)")
lines.append(" w  pair          k   fold(same) fold(cross)  both0(same) both0(cross)  P(dp=0)  P(dq=0)   both0/fold")
for w in WORDS:
    for k in KS:
        c = cnt[w][k]; x = cross[w][k]
        share = c["both"] / c["fold"] if c["fold"] else float("nan")
        lines.append(f" {w}  {NAMES[w][0]}~{NAMES[w][1]}  {k:2d}  {lg(c['fold'], N)}   "
                     f"{np.log2(x['fold']) if x['fold'] > 0 else float('-inf'):7.2f}     {lg(c['both'], N)}     "
                     f"{np.log2(x['both']) if x['both'] > 0 else float('-inf'):7.2f}    {lg(c['zp'], N)}  {lg(c['zq'], N)}   {share:.4f}")
    lines.append("")
lines.append("joint fold event, all four words, low k bits each (4k bits in all): count, log2 rate, "
             "log2 product of per-word same-pair rates")
for k in JK:
    if k in KS:
        prod = sum(np.log2(cnt[w][k]["fold"] / N) for w in WORDS)
        ps = f"{prod:7.2f}"
    else:
        ps = "   n/a"
    lines.append(f"  k={k} ({4 * k:2d} bits): {joint[k]:9d}  {lg(joint[k], N)}  {ps}")
lines.append("")
lines.append("fold algebra: residual (r1, r3, r4, r6) -> (r1, r3, w4' = r4 ^ ROR(r1,8), w6' = r6 ^ ROR(r3,8)) "
             "is an invertible XOR-linear change of coordinates")
lines.append("  w4' depends on E3 only (dB1, dZ9); w6' on E1 (db1, dZ11) and E3's eta (dD1)")
lines.append("  k   log2 P(w4'=0)  log2 P(w6'=0)  log2 P(both)")
for k in KS:
    lines.append(f"  {k:2d}    {lg(alg['w4p'][k], N)}        {lg(alg['w6p'][k], N)}       {lg(alg_joint[k], N)}")
lines.append(f"  parity(dB1) even: {chk['parity_dB1_even'] / N:.6f}; parity(db1 ^ dD1) even: "
             f"{chk['parity_db1_dD1_even'] / N:.6f}")
lines.append(f"  most common values: {alg_top}")
lines.append("")
lines.append("top full-width common differences delta (dp = dq = delta) by cross-pair mass: delta, n_p, n_q, share")
for w in WORDS:
    lines.append(f"  w={w}: distinct dp {cross[w]['distinct_dp']}, dq {cross[w]['distinct_dq']}; "
                 f"max count dp {cross[w]['max_count_dp']}, dq {cross[w]['max_count_dq']}")
    for row in top[w]:
        lines.append(f"     {row}")
with open(base + ".txt", "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines) + "\n")
print("\n".join(lines))
