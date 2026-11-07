# G02-U05 scan: memory objects CUBE (D[c] + sum spill), C7PL, CHUNK of pkgR37M3 (lowm.py copy).
# Convention: r37 ledger, 1 primitive per 256-bit op (rotation = 1).
import sys, json, math, random
sys.argv = ['x']
import lowm as L
from fractions import Fraction as Fr
base = L.ledger(show=False)
T0 = base['log2_T']
print('REPRO time_log2', base['time_log2'], 'log2_T', T0, 'vbar', base['vbar'], 'FIXED', L.FIXED)
tab, tot = L.memory_bytes()
print('REPRO bytes', tot, math.log2(tot))
out = {'base': dict(time_log2=base['time_log2'], log2_T=T0, bytes=tot, vbar=base['vbar'], vmax_fb=base['vmax_fb'], nfb=base['nfb'])}


def S_of(T, B):
    return T + max(0, math.log2(B) - 20)


def run(name, B, **patch):
    saved = {k: getattr(L, k) for k in patch}
    for k, v in patch.items():
        setattr(L, k, v)
    try:
        r = L.ledger(show=False)
    finally:
        for k, v in saved.items():
            setattr(L, k, v)
    d = r['log2_T'] - T0
    res = dict(time_log2=r['time_log2'], log2_T=r['log2_T'], dT_bits=d, vbar=r['vbar'], dvbar=r['vbar'] - base['vbar'],
               bytes=B, S=S_of(r['log2_T'], B), S_hold=S_of(T0, tot))
    out[name] = res
    print(name, json.dumps(res))
    return r


# CUBE part a: D[c] table (256 B). Recompute D[cu] = cu | S0(cu)<<32 per subtraction run:
# 3 rot + 2 xor + shift + or = 7, replacing address+load (2)
run('CUBE_D_recompute_rot1', tot - 256, RUN_CU=L.RUN_CU - 2 + 7)
run('CUBE_D_recompute_rot3', tot - 256, RUN_CU=L.RUN_CU - 2 + 13)


# CUBE part b: spill area (7168 B)
def det_A(n, k, Q0):   # no spill: redo sweep overhead + main W6 for each subtraction run
    nr = n >> k
    nb = (nr + 255) // 256
    nsw = (nb + 1) // 2
    part = 1 if nr % 256 else 0
    full = Q0 != 0
    t = L.cprep_ops() + L.CF_CLASS + nsw * L.SWEEP_OVH + nb * (L.sp_loads(k) + L.W6_OPS[(k, full)] + L.SCAN_FIX) + part
    if full:
        for cu in L.subsets(Q0):
            if cu:
                t += nsw * L.SWEEP_OVH + nb * (L.sp_loads(k) + L.W6_OPS[(k, True)] + L.RUN_CU + L.SUBF_OPS[(k, cu)] + L.SCAN_FIX) + part
    return t


def det_B(n, k, Q0):   # no spill: one-batch sweeps, sums stay in registers through the subtraction runs
    nr = n >> k
    nb = (nr + 255) // 256
    part = 1 if nr % 256 else 0
    full = Q0 != 0
    t = L.cprep_ops() + L.CF_CLASS + nb * L.SWEEP_OVH + nb * (L.sp_loads(k) + L.W6_OPS[(k, full)] + L.SCAN_FIX) + part
    if full:
        for cu in L.subsets(Q0):
            if cu:
                t += nb * (L.RUN_CU + L.SUBF_OPS[(k, cu)] + L.SCAN_FIX) + part
    return t


run('CUBE_spill_recompute_A', tot - 7168, class_det=det_A)
run('CUBE_spill_stream_B', tot - 7168, class_det=det_B)
run('CUBE_both_B_rot1', tot - 256 - 7168, class_det=det_B, RUN_CU=L.RUN_CU - 2 + 7)
run('CUBE_both_A_rot1', tot - 256 - 7168, class_det=det_A, RUN_CU=L.RUN_CU - 2 + 7)

# C7PL: plane transposition, verify on the real c7 values
env = L.Env()
c7s = [c['c7'] for c in env.cls] + [env.cls[0]['c7']] * (256 - L.NCLS)
M256 = (1 << 256) - 1


def rep(x):
    return sum(x << (32 * b) for b in range(8))


ops = 0
W = [sum(c7s[32 * b + k] << (32 * b) for b in range(8)) for k in range(32)]
for s, m in ((16, 0x0000ffff), (8, 0x00ff00ff), (4, 0x0f0f0f0f), (2, 0x33333333), (1, 0x55555555)):
    mm = rep(m)
    for k in range(32):
        if k & s:
            continue
        a, b = W[k], W[k + s]
        t = ((a >> s) ^ b) & mm
        b ^= t
        a ^= (t << s) & M256
        W[k], W[k + s] = a, b
        ops += 6
tgt = L.planes_from_values(c7s)
# output word j lane b is a 32-bit field; find the (word, bit-order) correspondence to plane j
def rev32(x):
    return int('{:032b}'.format(x), 2) if False else int('{:032b}'.format(x)[::-1], 2)
def revw(w):
    return sum(rev32((w >> (32 * b)) & 0xffffffff) << (32 * b) for b in range(8))
direct = sum(1 for j in range(32) if W[j] == tgt[j])
rev = sum(1 for j in range(32) if revw(W[j]) == tgt[j])
revword = sum(1 for j in range(32) if W[31 - j] == tgt[j])
revboth = sum(1 for j in range(32) if revw(W[31 - j]) == tgt[j])
print('transposition ops', ops, 'planes matching: direct', direct, 'bitrev', rev, 'wordrev', revword, 'both', revboth)
TRANSP = ops
c7_extra = 222 * 3 + TRANSP - 63
print('C7 recompute extra ops/FB', c7_extra)
run('C7PL_recompute', tot - 1024, FIXED=L.FIXED + c7_extra)


# CHUNK: direct exact test of all 32 l (replaces probe + survivors)
def expected_direct():
    ct_var = L.CLS_LANE * L.NCLS * L.P7
    perclass = pairs = Fr(0)
    for (n, k, cnt) in L.CLASS_TYPES:
        perclass += cnt * L.P7 * L.class_expected(n, k)
        pairs += cnt * L.P7 * L.P6 * n
    groups = (pairs + 3) / 4
    lanes = 4 * groups
    grp = groups * L.GROUP_BODY + L.PAD_OPS
    surv = lanes * L.NSURV * (L.EX_OPS + 1)
    c3b_row = L.ROWCOMP + L.ROWCHECK + 1
    c3b_pair = 201 + L.RECOMP + 1 + L.RARE_LOOKUP
    c3b_l = 2 + 6 + 2 * c3b_row
    rare = lanes * L.R16F * (c3b_pair + c3b_l + 19 * Fr(1, 512) * c3b_row)
    return dict(ct_var=ct_var, perclass=perclass, grp=grp, surv=surv, rare=rare, g=pairs, vbar=ct_var + perclass + grp + surv + rare)


run('CHUNK_direct_exact32', tot - 262144, expected=expected_direct)

# CHUNK: SIMD prefilter across l (4 words x 8 lanes of 32 bit), verify against env.filt
MP = sum(1 << b for b in (7, 9, 11, 12, 17, 18, 22))


def simd_filt(u):
    m = 0
    for l in L.FEASIBLE_L:
        c = env.LC[l]
        e = (u + c['C']) & L.M32
        if (e & MP) == (L.E16V & MP) and not ((e ^ c['Ex15']) & 0x10):
            m |= 1 << l
    return m


bad = 0
rr = random.Random(7)
hit = 0
for _ in range(60000):
    u = rr.getrandbits(32)
    a = env.filt(u)
    b = simd_filt(u)
    bad += a != b
    hit += a != 0
print('simd prefilter vs table filt mismatches', bad, 'of 60000; filt!=0', hit, 'expect ~', 60000 * 1521152 / 2 ** 24)
PREF = 1 + 4 * 9 + 3 + 1
p_word = 1 - (1 - 2 ** -8) ** 8
HITCOST = 4 * p_word * (8 * (L.EX_OPS + 1) + 2)
per_lane = PREF + HITCOST


def expected_simd():
    ex = expected_direct()
    lanes = 4 * ((ex['g'] + 3) / 4)
    ex['surv'] = lanes * Fr(per_lane).limit_denominator(10 ** 6)
    ex['vbar'] = ex['ct_var'] + ex['perclass'] + ex['grp'] + ex['surv'] + ex['rare']
    return ex


print('simd per-lane price', per_lane, 'vs table', sum(L.PROBE) / 4 + float(L.PNZ * L.SURV_FIX + L.MU * (L.SURV_LANE + L.EX_OPS)))
run('CHUNK_simd_prefilter_ESTIMATE', tot - 262144, expected=expected_simd)
json.dump(out, open('m_scan_out.json', 'w'), indent=1)
