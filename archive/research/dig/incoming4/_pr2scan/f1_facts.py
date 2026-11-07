"""F1: facts for LINE / POLY / ROOT cells of poseidon-r2.  Own code; writes f1_facts.json."""
import json, math, random, time
from pos_scan_lib import *
import rcells as rc

F = {}
rng = random.Random(777)

# 1. skip table: degrees of the digest, exponent of 5, three levels of line freedom, r = 0,1,2
def generic_nkrho_deg(r):
    n0, r0, u, v = [rng.randrange(1, P) for _ in range(4)]
    lanes = [add(const(n0), scale(S(1, [mpz(1)], NEG), u)), add(const(r0), scale(S(1, [mpz(1)], NEG), v)), const(CAPACITY)]
    lanes = run_rounds(lanes, rounds_spec(r))
    y = lanes[0]
    return y.e, y.low <= y.e

def generic_uv_deg(r):
    a, b, U0, V0 = [rng.randrange(1, P) for _ in range(4)]
    sp = [d for d in rounds_spec(r) if d['idx'] >= 1]
    return rc.tau_run(sp, 0, (a, b, U0, V0))

tab = {}
for r in (0, 1, 2):
    e0, c0 = generic_nkrho_deg(r)
    e1, w1, c1 = generic_uv_deg(r)
    sp = specs_from_2(r)
    e2 = [W_deg(*lineaff_args, sp) for lineaff_args in [tuple(rc.lineaff(j)[:2]) for j in range(3)]]
    tab[r] = dict(generic_nk_rho_line=e0, generic_nk_rho_cert=c0, generic_UV_line_tau=e1, UV_Wform=w1, UV_cert=c1, W_line=[x[0] for x in e2],
                  power_of_5=[round(math.log(e0, 5), 6), round(math.log(e1, 5), 6), round(math.log(e2[0][0], 5), 6)])
F['skip_table'] = tab

# 2. round-2 free conditions
cond = {}
for j in range(3):
    alpha, beta, line = rc.lineaff(j)
    c2 = RC[2]
    cond[j] = dict(beta_zero_lanes=[i for i in range(3) if beta[i] == 0], alpha_plus_c2_zero_lanes=[i for i in range(3) if (alpha[i] + c2[i]) % P == 0])
F['round2_free_conditions'] = cond

# 3. random lines in (U,V): W-affine after R1?
cnt = 0; N = 24; degs = set()
sp1 = [d for d in rounds_spec(2) if d['idx'] >= 1]
for t in range(N):
    a, b, U0, V0 = [rng.randrange(1, P) for _ in range(4)]
    e, wf, cert = rc.tau_run(sp1, 0, (a, b, U0, V0))
    cnt += bool(wf); degs.add(e)
# direction through canonical Q but non-canonical slope
cnt2 = 0
for t in range(N):
    a0, b0, U0, V0, d = setup_line(0)
    a, b = rng.randrange(1, P), rng.randrange(1, P)
    e, wf, cert = rc.tau_run(sp1, 0, (a, b, U0, V0))
    cnt2 += bool(wf)
canon = []
for j in range(3):
    e, wf, cert = rc.tau_run(sp1, j)
    canon.append((e, bool(wf)))
F['random_lines'] = dict(n=N, wform_random_point_random_dir=cnt, wform_canonical_Q_random_dir=cnt2, tau_degrees_random=sorted(degs), canonical=canon)

# 4. interface lane degrees (W) per round for each j
iface = {}
sp0 = specs_from_2(2)
for j in range(3):
    row = {}
    for idx in (2, 3, 4, 5, 60, 61, 62):
        row[idx] = rc.lane_degs(sp0, j, idx)
    iface[j] = row
F['interface_lane_degrees'] = iface

# 5. leading coefficient: tracker vs NTT lead
leads = {}
for j in range(3):
    alpha, beta, line = rc.lineaff(j)
    lanes = run_rounds(W_start(alpha, beta), sp0)
    leads[j] = hex(int(lanes[0].c[0]))
F['tracker_leads'] = leads
F['ntt_leads'] = {j: json.loads([l for l in open('r2_j%d_c0.json.txt' % j) if l.startswith('{')][0])['lead'] for j in range(3)}
F['lead_match'] = all(int(F['tracker_leads'][j], 16) == int(F['ntt_leads'][j], 16) for j in range(3))

# 6. reference collisions at r = 2 (lean_r2/data/collisions_r2.json): verify with poseidon_ref and the W-line map
cols = json.load(open(os.path.join(IMPL, '..', 'lean_r2', 'data', 'collisions_r2.json')))
ver = []
for c in cols:
    ok_hash = hash_reduced(c['nk1'], c['rho1'], 2) == c['digest'] == hash_reduced(c['nk2'], c['rho2'], 2)
    distinct = (c['nk1'], c['rho1']) != (c['nk2'], c['rho2'])
    j = c['j']
    a, b, U0, V0, d = setup_line(j)
    Ws = []
    okline = True
    for nk, rho in ((c['nk1'], c['rho1']), (c['nk2'], c['rho2'])):
        U = pow((nk + RC[0][0]) % P, 5, P); V = pow((rho + RC[0][1]) % P, 5, P)
        t1 = (U - U0) * inv(a) % P; t2 = (V - V0) * inv(b) % P
        okline &= (t1 == t2)
        Ws.append(pow(t1, 5, P))
    centre_ok = ((Ws[0] + Ws[1]) * inv(2) - c['centre']) % P == 0
    ver.append(dict(ok_hash=ok_hash, distinct=distinct, on_line=okline, centre=centre_ok, j=j))
F['r2_collisions_file'] = dict(n=len(cols), verified=ver)

# 7. exponent / window counts
def sliding_window_cost(e, w):
    bits = bin(e)[2:]
    n = len(bits)
    i = 0
    sq = n - 1
    mults = 0
    pre = (1 if w > 1 else 0) + ((1 << (w - 1)) - 1 if w > 1 else 0)   # x^2 and odd powers up to 2^w - 1
    first = True
    while i < n:
        if bits[i] == '0':
            i += 1
            continue
        j = min(n, i + w)
        while bits[j - 1] == '0':
            j -= 1
        if not first:
            mults += 1
        first = False
        i = j
    return dict(w=w, squarings=sq + (1 if w > 1 else 0), mults=mults + max(0, pre - 1 if w > 1 else 0), total=sq + mults + pre)
F['e5_bits'] = INV5.bit_length(); F['e5_pop'] = bin(INV5).count('1')
F['e5_windows'] = [sliding_window_cost(INV5, w) for w in range(1, 7)]
h = (P - 1) // 2
F['half_bits'] = h.bit_length(); F['half_pop'] = bin(h).count('1')
F['p_mod_5'] = P % 5

# 8. allowed transform sizes (p-1 = 2^32 * 3 * 463 * ...)
assert (P - 1) % (2 ** 32 * 3 * 463) == 0
sizes = sorted(set(2 ** a * 3 ** b * 463 ** c for a in range(0, 33) for b in (0, 1) for c in (0, 1)))
def smallest(x): return next(s for s in sizes if s >= x)
n_ = 195312
F['sizes'] = dict(N_for_g=smallest(n_ + 1), N_for_product=smallest(2 * n_ - 1), N_for_qg=smallest(n_ + 1),
                  pow2_for_g=1 << (n_ + 1 - 1).bit_length(), pow2_for_product=1 << (2 * n_ - 2).bit_length())
F['sizes_r1'] = dict(N_for_g=smallest(39063), N_for_product=smallest(2 * 39062 - 1))
json.dump(F, open('f1_facts.json', 'w'), indent=1, default=str)
print(json.dumps(F, indent=1, default=str)[:6000])
