import random, json
from eng import *
M = 0xFFFFFFFF
rng = random.Random(33)
def cancel(m, j, d, d2):
    a, b = IV[j], IV[j+4]
    a1 = (a + b + m[2*j]) & M
    e = ((a1 ^ d ^ d2) - a1) & M
    m2 = list(m); m2[2*j] = (m[2*j] + e) & M; m2[2*j+1] = (m[2*j+1] - e) & M
    return m2
def bias(structs, cols, N=6000):
    res = {}
    cnt = {r: [0]*256 for r in (1, 2, 3)}
    for _ in range(N):
        m = [rng.getrandbits(32) for _ in range(16)]
        pa = dict(ctr_lo=0, ctr_hi=0, blen=64, flags=11); pb = dict(pa)
        for k, (va, vb) in structs.items(): pa[k] = va; pb[k] = vb
        mb = list(m)
        for j, k in enumerate(("ctr_lo", "ctr_hi", "blen", "flags")):
            if j in cols and pa[k] != pb[k]: mb = cancel(mb, j, pa[k], pb[k])
        for r in (1, 2, 3):
            da = compress(IV, m, 0, pa["blen"], pa["flags"], r)[:8]; db = compress(IV, mb, 0, pb["blen"], pb["flags"], r)[:8]
            for i in range(8):
                x = da[i] ^ db[i]
                for b in range(32):
                    cnt[r][i*32+b] += (x >> b) & 1
    for r in (1, 2, 3):
        p = [c / N for c in cnt[r]]
        nb = sum(1 for q in p if abs(q - 0.5) > 0.05)
        words = sum(1 for i in range(8) if any(abs(p[i*32+b] - 0.5) > 0.05 for b in range(32)))
        res["r%d" % r] = dict(biased_bits=nb, words_with_biased_bit=words, max_dev=max(abs(q-0.5) for q in p))
    return res
R = {}
R["d21_flags_no_cancel"] = bias(dict(flags=(11, 12)), set())
R["d21_flags_cancel_m6m7"] = bias(dict(flags=(11, 12)), {3})
R["d22_len_cancel_m4m5"] = bias(dict(blen=(55, 63)), {2})
R["d22_len_flags_both_cancel"] = bias(dict(blen=(55, 63), flags=(11, 12)), {2, 3})
json.dump(R, open("exp_d1b_out.json", "w"), indent=1); print(json.dumps(R, indent=1))
