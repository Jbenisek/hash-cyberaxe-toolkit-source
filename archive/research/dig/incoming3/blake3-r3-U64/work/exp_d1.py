import random, json
from eng import *
rng = random.Random(21)
M = 0xFFFFFFFF
def cancel(m, j, d, d2):
    a, b = IV[j], IV[j+4]
    a1 = (a + b + m[2*j]) & M
    a1p = a1 ^ d ^ d2
    e = (a1p - a1) & M
    m2 = list(m); m2[2*j] = (m[2*j] + e) & M; m2[2*j+1] = (m[2*j+1] - e) & M
    return m2
def run(structs, D_cols, label, N=1500):
    """structs: dict word -> (value_A, value_B) among 'ctr_lo','ctr_hi','blen','flags'; D_cols: columns whose differing state word is cancelled."""
    res = {r: [] for r in (1, 2, 3)}
    for _ in range(N):
        m = [rng.getrandbits(32) for _ in range(16)]
        pa = dict(ctr_lo=0, ctr_hi=0, blen=64, flags=11); pb = dict(pa)
        for k, (va, vb) in structs.items(): pa[k] = va; pb[k] = vb
        mb = list(m)
        for j, k in enumerate(("ctr_lo", "ctr_hi", "blen", "flags")):
            if j in D_cols and pa[k] != pb[k]:
                mb = cancel(mb, j, pa[k], pb[k])
        for r in (1, 2, 3):
            da = compress(IV, m, pa["ctr_lo"] | (pa["ctr_hi"] << 32), pa["blen"], pa["flags"], r)[:8]
            db = compress(IV, mb, pb["ctr_lo"] | (pb["ctr_hi"] << 32), pb["blen"], pb["flags"], r)[:8]
            res[r].append(sum(1 for i in range(8) if da[i] == db[i]))
    out = {}
    for r in (1, 2, 3):
        vals = res[r]
        out["r%d_equal_words" % r] = dict(min=min(vals), max=max(vals), mean=sum(vals)/len(vals))
    ndiff = sum(1 for k in range(16) if mb[k] != m[k])
    out["message_words_differing"] = ndiff
    return label, out
R = {}
# d21: flags 11 vs 12 (delta 7)
R["d21_uncancelled"] = run(dict(flags=(11, 12)), set(), "flags 11 vs 12, identical message words")[1]
R["d21_cancel_col3"] = run(dict(flags=(11, 12)), {3}, "flags 11 vs 12, m6/m7 absorb")[1]
# d22: two structural differences (blen 55/63 and flags 11/12), cancelled in their calls
R["d22_len_only_cancel"] = run(dict(blen=(55, 63)), {2}, "blen 55 vs 63, m4/m5 absorb")[1]
R["d22_len_and_flags_cancel"] = run(dict(blen=(55, 63), flags=(11, 12)), {2, 3}, "blen+flags, m4..m7 absorb")[1]
R["d22_len_and_flags_nocancel"] = run(dict(blen=(55, 63), flags=(11, 12)), set(), "blen+flags no absorb")[1]
R["d22_len_cancel_flags_left"] = run(dict(blen=(55, 63), flags=(11, 12)), {2}, "blen absorbed, flags diff left")[1]
R["d22_flags_cancel_len_left"] = run(dict(blen=(55, 63), flags=(11, 12)), {3}, "flags absorbed, blen diff left")[1]
R["d22_ctr_lo_hi_cancel"] = run(dict(ctr_lo=(0, 1), ctr_hi=(0, 1)), {0, 1}, "counter lo+hi absorbed (not legal for a root block)")[1]
R["d22_all_four_cancel"] = run(dict(ctr_lo=(0, 1), ctr_hi=(0, 1), blen=(55, 63), flags=(11, 12)), {0, 1, 2, 3}, "all four absorbed (not legal)")[1]
# in-call absorption with ZERO message difference: G is a bijection in the state, so impossible; test the inverse on random states
def G(a, b, c, d, x, y):
    a = (a + b + x) & M; d = ror(d ^ a, 16); c = (c + d) & M; b = ror(b ^ c, 12)
    a = (a + b + y) & M; d = ror(d ^ a, 8); c = (c + d) & M; b = ror(b ^ c, 7); return a, b, c, d
def Ginv(a, b, c, d, x, y):
    b = ror(b, 25) ^ c; c = (c - d) & M; d = ror(d, 24) ^ a; a = (a - b - y) & M
    b = ror(b, 20) ^ c; c = (c - d) & M; d = ror(d, 16) ^ a; a = (a - b - x) & M; return a, b, c, d
okinv = all(Ginv(*G(*(s := [rng.getrandbits(32) for _ in range(6)])[:4], s[4], s[5]), s[4], s[5]) == tuple(s[:4]) for _ in range(200000))
R["G_inverse_roundtrip_200000"] = okinv
# same message, state words differ in d only: outputs differ always (bijection) - direct sample
neq = 0
for _ in range(300000):
    s = [rng.getrandbits(32) for _ in range(6)]; dd = rng.getrandbits(32) or 1
    o1 = G(s[0], s[1], s[2], s[3], s[4], s[5]); o2 = G(s[0], s[1], s[2], s[3] ^ dd, s[4], s[5])
    neq += (o1 != o2)
R["same_message_d_diff_outputs_equal_count_of_300000"] = 300000 - neq
json.dump(R, open("exp_d1_out.json", "w"), indent=1); print(json.dumps(R, indent=1))
