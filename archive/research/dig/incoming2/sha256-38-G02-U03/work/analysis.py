import sys, pickle, os, math, json
sys.setrecursionlimit(20000)
W = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, W)
import a0l_var as A
from fractions import Fraction
pk = os.path.join(W, 'cal.pkl')
if os.path.exists(pk):
    cal = pickle.load(open(pk, 'rb'))
else:
    cal = A.calibrate(); pickle.dump(cal, open(pk, 'wb'))
C = 2728
def T_of(c):
    rows, info = A.ledger(cal=c, show=False)
    N = sum(int(v) for _, v in rows)
    return math.log2(N) - math.log2(C), info, N
def S_of(T, B): return T + max(0.0, math.log2(B) - 20)
T0, info0, N0 = T_of(cal)
parts, B0 = A.memory(cal)
print('REPRO T0 %.10f  bytes %d  log2 %.5f' % (T0, B0, math.log2(B0)))
S0 = S_of(T0, B0)
print('S0 %.6f  slack %d B' % (S0, 2**20 - B0))
GRPS = sorted(set(A.GRP))
progs = {g: A.program(g)[0] for g in GRPS}
for g in GRPS:
    ins = progs[g]; cnt = {}
    for i in ins: cnt[i[0]] = cnt.get(i[0], 0) + 1
    print('prog', g, len(ins), cnt)
used = {}; loads_per_prog = {}
for g in GRPS:
    lp = {}
    for i in progs[g]:
        if i[0] == 'ld': lp[i[2]] = lp.get(i[2], 0) + 1
    loads_per_prog[g] = lp
    for n in lp: used[n] = used.get(n, 0) + lp[n]
def jof(n): return int(''.join(ch for ch in n if ch.isdigit()))
def nm(n): return ''.join(ch for ch in n if not ch.isdigit())
names = [n + str(j) for n in ('HH', 'PP', 'QQ', 'EF', 'FF', 'K1', 'KP') for j in range(32)]
unused = [n for n in names if n not in used]
print('bcast planes loaded by some program:', len(used), 'of 224; unused', len(unused))
byname = {}
for n in names:
    byname.setdefault(nm(n), [0, 0])[0 if n in used else 1] += 1
print('per scalar (used, unused):', byname)
print('bcast loads per run, by prog:', {g: sum(v.values()) for g, v in loads_per_prog.items()})
def pl_cost(j): return 3 if j in (0, 31) else 4
def rc_cost(j): return 2 if j in (0, 31) else 3
res = {}
planes_U = sum(pl_cost(jof(n)) for n in used)
c = dict(cal); c['planes'] = planes_U
T, _, _ = T_of(c)
Bu = B0 - (224 - len(used)) * 32
res['BCAST_USEDONLY'] = dict(n_used=len(used), planes_ops=planes_U, T=T, dT=T - T0, bytes=Bu, S=S_of(T, Bu))
for tag, extra in (('R_LD', lambda j: rc_cost(j)), ('R_REG', lambda j: rc_cost(j) - 1)):
    newp = {}
    for g in GRPS:
        newp[g] = len(progs[g]) + sum(k * extra(jof(n)) for n, k in loads_per_prog[g].items())
    c = dict(cal); c['planes'] = 0; c['prog'] = dict(newp)
    T, _, _ = T_of(c)
    code_delta = sum(newp.values()) - sum(cal['prog'].values())
    Bn = B0 - 7168 + 32 * code_delta
    res['BCAST_' + tag] = dict(prog=newp, T=T, dT=T - T0, bytes=Bn, S=S_of(T, Bn), code_delta_instr=code_delta)
p7 = Fraction(287309824, 2**32)
runs = sum(p7 * 15 for h in A.GRP)
res['runs_per_FB'] = float(runs)

def schedule_remat(P, outs, maxslots, regs=A.REGS, cap=400000):
    nodes = P.nodes; N = len(nodes); END = N; NEVER = N + 1
    live = set(n for n, _ in outs); stack = list(live)
    while stack:
        n = stack.pop(); op, a, b, _n = nodes[n]
        if op != 'in':
            for x in (a, b):
                if x not in live: live.add(x); stack.append(x)
    uses = [[] for _ in range(N)]
    for i, (op, a, b, _n) in enumerate(nodes):
        if op == 'in' or i not in live: continue
        uses[a].append(i)
        if b != a: uses[b].append(i)
    for nid, _ in outs: uses[nid].append(END)
    ptr = [0] * N
    def nextuse(n, p):
        u = uses[n]
        while ptr[n] < len(u) and u[ptr[n]] <= p: ptr[n] += 1
        return u[ptr[n]] if ptr[n] < len(u) else NEVER
    reg_of = {}; val_in = {}; free = list(range(regs - 1, -1, -1)); instrs = []; inmem = {}; nslot = [0]; remat = [0]
    class Blow(Exception): pass
    def evict(p, pinned):
        best = None; bd = -1
        for r, n in val_in.items():
            if r in pinned: continue
            d = nextuse(n, p - 1)
            if d > bd: bd = d; best = r
        n = val_in[best]
        if bd != NEVER and nodes[n][0] != 'in' and n not in inmem and nslot[0] < maxslots:
            instrs.append(('st', nslot[0], best)); inmem[n] = nslot[0]; nslot[0] += 1
        del val_in[best]; del reg_of[n]; free.append(best)
    def getreg(p, pinned):
        if not free: evict(p, pinned)
        return free.pop()
    def need(n, p, pinned):
        if n in reg_of: return reg_of[n]
        if len(instrs) > cap: raise Blow()
        op, a, b, name = nodes[n]
        if op == 'in':
            r = getreg(p, pinned); instrs.append(('ldp' if name.startswith('P:') else 'ld', r, name))
        elif n in inmem:
            r = getreg(p, pinned); instrs.append(('lds', r, inmem[n]))
        else:
            remat[0] += 1
            pn = set(pinned)
            dropped = lambda x: x not in reg_of and nodes[x][0] != 'in' and x not in inmem
            first, second = (b, a) if (dropped(b) and not dropped(a)) else (a, b)
            r1 = need(first, p, pn); pn.add(r1); r2 = need(second, p, pn); pn.add(r2)
            ra, rb = (r2, r1) if first == b and first != a else (r1, r2)
            r = getreg(p, {x for x in pn if x in val_in}); instrs.append((op, r, ra, rb))
        reg_of[n] = r; val_in[r] = n; return r
    try:
        for i, (op, a, b, _n) in enumerate(nodes):
            if op == 'in' or i not in live: continue
            pinned = set()
            ra = need(a, i, pinned); pinned.add(ra)
            rb = need(b, i, pinned); pinned.add(rb)
            for n in (a, b):
                if n in reg_of and nextuse(n, i) == NEVER:
                    r = reg_of.pop(n); del val_in[r]; free.append(r)
            rd = getreg(i, {r for r in pinned if r in val_in})
            instrs.append((op, rd, ra, rb)); reg_of[i] = rd; val_in[rd] = i
        resr = []
        for (nid, neg) in outs:
            r = need(nid, END, set(resr))
            if neg: instrs.append(('not', r, r))
            resr.append(r)
    except (Blow, KeyError):
        return None, None, remat[0]
    return instrs, resr, remat[0]
def build(g):
    mask = A.CLASSES[A.GRP.index(g)][2]; sh, cb = A.shape_of(g)
    return A.build_e16(mask, cb, sh)
spill = {}
for k in (15, 14, 12, 8, 4, 2, 1, 0):
    newp = {}; ok = True; rm = {}
    for g in GRPS:
        P, okn = build(g)
        ins, r, nr = schedule_remat(P, [okn], k)
        rm[g] = nr
        if ins is None: ok = False; newp[g] = None; continue
        newp[g] = len(ins)
    if not ok:
        spill[k] = dict(blow=True, remat=rm); print('slots', k, 'BLOWUP >400000 instrs', rm); continue
    c = dict(cal); c['prog'] = dict(newp)
    T, _, _ = T_of(c)
    spill[k] = dict(prog=newp, remat=rm, T=T, dT=T - T0, code_delta=sum(newp.values()) - sum(cal['prog'].values()))
    print('slots', k, newp, 'remat', rm, 'dT %.6f' % (T - T0))
res['SPILL'] = spill
fbs = cal['fb_scalars']
K = len(A.CLASSES)
lanes_per_fb = float(sum(p7 * 3840 * Fraction(1, 2**12) for c_ in A.CLASSES))
res['lanes_per_FB'] = lanes_per_fb
pany = info0['pany']
dv_unc = -2 * float(K * p7) + float(1 - pany) * (fbs + cal['planes'])
c = dict(cal); c['dv'] = Fraction(dv_unc).limit_denominator(10**9); T, _, _ = T_of(c)
res['SCAL_HITLIST_UNCOND'] = dict(dv=dv_unc, T=T, dT=T - T0)
dv_sc = lanes_per_fb * fbs
c = dict(cal); c['dv'] = Fraction(dv_sc).limit_denominator(10**9); T, _, _ = T_of(c)
res['SCAL_RECOMP_PER_LANE'] = dict(dv=dv_sc, T=T, dT=T - T0, bytes=B0, fb_scalars_ops=fbs)
res['SCAL_HITLIST_FULL'] = dict(bytes=B0 + 832, S=S_of(T0, B0 + 832))
res['base'] = dict(T0=T0, B0=B0, S0=S0, vbar=float(info0['vbar']), N=N0, pany=float(pany), planes_ops=cal['planes'], fb_scalars=fbs)
json.dump(res, open(os.path.join(W, 'results.json'), 'w'), indent=1, default=str)
print(json.dumps(res, indent=1, default=str)[:7000])
