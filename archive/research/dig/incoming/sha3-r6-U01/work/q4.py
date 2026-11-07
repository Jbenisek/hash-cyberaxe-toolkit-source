"""Q4: do non-identity chi1 transitions (and theta2 kernel membership of the chi1 output difference) give another route?
Per-direction exhaustive scan: for every CP-kernel pair message direction (the leader's 32 z-directions are members), enumerate every value of
the chi1 rows it touches, classify the chi1 output difference D: identity (D = input diff), theta2-kernel (all column parities zero), footprint |theta(D)|.
Feasibility of a row assignment is checked with the affine forms of the message (F135 format)."""
import json, random, itertools, time
from sha3lab import *

F = Forms('F135')
t0 = time.time()
def chi5(r):  # r: 5-bit int, bit x
    o = 0
    for x in range(5):
        a = (r >> x) & 1; b = (r >> ((x + 1) % 5)) & 1; c = (r >> ((x + 2) % 5)) & 1
        o |= (a ^ ((1 - b) & c)) << x
    return o
CHI5 = [chi5(r) for r in range(32)]

pool = []
for x in range(5):
    ys = [y for y in range(5) if x + 5 * y < 17]
    for z in range(64):
        for i in range(len(ys)):
            for j in range(i + 1, len(ys)):
                s1 = 64 * (x + 5 * ys[i]) + z; s2 = 64 * (x + 5 * ys[j]) + z
                if s1 < 1080 and s2 < 1080: pool.append((s1, s2))
print('pool', len(pool))
leader = set((j, 320 + j) for j in range(32))

def posrow(p):
    lane, z = divmod(p, 64); return lane // 5, z, lane % 5
def theta_fp(bits):  # bits: set of (x,y,z) -> theta image weight
    A = [0] * 25
    for (x, y, z) in bits: A[x + 5 * y] |= 1 << z
    return bin(to_int(theta(A))).count('1')

res = []
for (s1, s2) in pool:
    d = (1 << s1) | (1 << s2)
    T = lin_image('F135', d)
    pos = [p for p in range(1600) if (T >> p) & 1]
    if len(pos) != 2: continue
    rows = {}
    for p in pos:
        y, z, x = posrow(p); rows.setdefault((y, z), 0); rows[(y, z)] |= 1 << x
    keys = list(rows)
    best = None; n_kernel = 0; n_nonid_kernel = 0; n_feas = 0; n_nonid_feas = 0; minfp_nonid = None
    for vals in itertools.product(range(32), repeat=len(keys)):
        Dbits = set()
        for (y, z), a in zip(keys, vals):
            dr = CHI5[a ^ rows[(y, z)]] ^ CHI5[a]
            for x in range(5):
                if (dr >> x) & 1: Dbits.add((x, y, z))
        if not Dbits: continue
        ident = (Dbits == set((posrow(p)[2], posrow(p)[0], posrow(p)[1]) for p in pos))
        col = {}
        for (x, y, z) in Dbits: col[(x, z)] = col.get((x, z), 0) ^ 1
        kern = not any(col.values())
        fp = len(Dbits) if kern else theta_fp(Dbits)
        # feasibility: the touched rows must take these values
        S = Sys(); ok = True
        for (y, z), a in zip(keys, vals):
            for x in range(5):
                p = 64 * (x + 5 * y) + z
                if S.add(F.rows[p], ((a >> x) & 1) ^ ((F.const >> p) & 1)) == 'incons': ok = False
        if not ok: continue
        n_feas += 1
        if not ident:
            n_nonid_feas += 1
            if minfp_nonid is None or fp < minfp_nonid[0]: minfp_nonid = (fp, len(Dbits), kern)
        if kern:
            n_kernel += 1
            if not ident: n_nonid_kernel += 1
        if best is None or fp < best[0]: best = (fp, len(Dbits), kern, ident)
    res.append(dict(dir=(s1, s2), leader=(s1, s2) in leader, nrows=len(keys), n_feasible=n_feas, n_nonid_feasible=n_nonid_feas, n_kernel=n_kernel,
                    n_nonid_kernel=n_nonid_kernel, best=best, minfp_nonid=minfp_nonid))
tot = len(res)
summ = dict(directions=tot, pool=len(pool), leader_dirs=sum(r['leader'] for r in res),
            dirs_with_kernel_D=sum(1 for r in res if r['n_kernel'] > 0), dirs_with_nonid_kernel_D=sum(1 for r in res if r['n_nonid_kernel'] > 0),
            dirs_one_row=sum(1 for r in res if r['nrows'] == 1), dirs_two_rows=sum(1 for r in res if r['nrows'] == 2))
fpv = [r['minfp_nonid'][0] for r in res if r['minfp_nonid']]
summ['min_footprint_nonidentity_any_dir'] = min(fpv) if fpv else None
bid = [r['best'][0] for r in res if r['best']]
summ['min_footprint_any_transition_any_dir'] = min(bid)
summ['leader_dirs_best'] = sorted(set(str(r['best']) for r in res if r['leader']))
summ['leader_dirs_n_kernel'] = sum(r['n_kernel'] for r in res if r['leader'])
summ['nonid_kernel_examples'] = [dict(dir=r['dir'], best=r['best'], n=r['n_nonid_kernel'], nrows=r['nrows']) for r in res if r['n_nonid_kernel']][:12]
summ['kernel_example_footprints'] = sorted(set(r['best'][0] for r in res if r['n_kernel']))
summ['secs'] = round(time.time() - t0, 1)
json.dump(dict(summary=summ, rows=res), open('q4_out.json', 'w'), default=str)
print(json.dumps(summ, default=str, indent=1))
