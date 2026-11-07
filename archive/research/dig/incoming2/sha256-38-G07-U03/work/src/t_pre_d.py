# t_pre_d.py - the changed preprocessing bodies of vtpre.py as counted code, against their definitions; writes
# runs/pre1.json and runs/pre2.json (the base values of P1..P4 with LIVE_ops and LIVE_g; every P5 and P6 value is the count of an
# executed body: P5 setup, body, append and loop, the P6 zero, count and fill iterations and their per-variant overheads, the prefix).
# usage: t_pre_d.py <dir of vt38.py> <runs dir>
import sys, os, json, random
sys.path.insert(0, sys.argv[1]); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.dont_write_bytecode = True
from vtpre import *
RUNS = sys.argv[2]; rr = random.Random(20261011)
class PM(Machine):
    """the counted machine with a plain memory for the preprocessing (reads what was stored, 0 elsewhere; records from tables())"""
    def load(s, addr):
        if addr in s.mem: return s.mem[addr]
        t = addr >> 150
        return s.tab[addr] if t in (3, 4) and addr in s.tab else 0
def execute(a, regs, mem=None, tab=None):
    a.L('END'); m = PM([], lambda *x: [], tab or {}); m.r.update(regs); m.mem.update(mem or {}); m.run(a); return m
# ---- P1': live words
cnt = []; L = live_list(cnt)
assert [g for _, g in L] == [g for g in GL if g not in (0x35f29010, 0x35f29011, 0x35f29410, 0x35f29414, 0x35f29415, 0x35fa9010, 0x35fa9011, 0x35fa9410, 0x35fa9414, 0x35fa9415)]
assert sum(cnt) == 1 << 20 and len(L) == 22
def pred(gi, e):
    r = grec(gi, GL[gi]); b = gaddr(gi); A = (e + r[b + 3]) & M
    return (e & r[b + 1]) == r[b + 2] and (A & r[b + 4]) == r[b + 5] and all(((A >> p) ^ (A >> q)) & 1 == (0 if w else 1) for p, q, w in a17int())
live_max = 0; bad = 0; npass = 0
for gi in range(32):
    a = Asm(); gen_live_body(a, gi, 'END'); r = grec(gi, GL[gi]); b = gaddr(gi)
    for k in range(3000):
        e = rr.getrandbits(32)
        if k % 2: e = (e & ~r[b + 1] & M) | r[b + 2]
        m = execute(a, dict(e=e, cnt=0)); ok = m.r['cnt'] == 1; bad += ok != pred(gi, e); npass += ok
        if ok: live_max = max(live_max, m.ops)
a = Asm(); gen_live_end(a, 0, 'END'); live_g = execute(a, dict(cnt=5, lv=1 << 160)).ops
print("P1' live words:", len(L), 'count', sum(cnt), '| body vs predicate on 96,000 E17:', bad, 'mismatches,', npass, 'passes | longest path', live_max, '| per g', live_g)
assert bad == 0 and npass > 0
# ---- P5: setup, body, append on real windows
tab = tables(); EV = entry_variants(); setup_ops = None; app = []; bodies = []; nvalid = 0; badw = 0
for j in rr.sample(range(256), 6):
    a0 = A0L[j]; a1e, a2ie = EV[j]
    for a2i in [a2ie] + rr.sample(range(768), 2):
        a = Asm(); gen_enum_setup(a, a0); s = execute(a, dict(ra=A2T + 2 * a2i), tab=tab); setup_ops = s.ops
        lo = s.r['lo']; base_r = (a1e - lo) & M if a2i == a2ie else rr.randrange(1 << 29)
        for r_ in [base_r] + [rr.randrange(1 << 29) for _ in range(300)]:
            a = Asm(); gen_enum_setup(a, a0); a.L('S'); gen_enum_body(a, a0, 'END'); a.L('B'); gen_enum_append(a, a0)
            m = execute(a, dict(ra=A2T + 2 * a2i, r=r_, lp=1 << 170), tab=tab)
            a1 = (lo + r_) & M; v = valid(variant(a0, a1, A2L[a2i]))
            if (1 << 170) in m.mem:
                assert v; nvalid += 1
                e = mkent(a0, a1, A2L[a2i], a2i, 0)
                badw += [m.mem[(1 << 170) + k] for k in range(3)] != [e[0], (e[1] - gw(0)) & WORD, c9x_of(A2L[a2i])]
                b2 = Asm(); gen_enum_setup(b2, a0); gen_enum_body(b2, a0, 'END'); body = execute(b2, dict(ra=A2T + 2 * a2i, r=r_), tab=tab).ops - setup_ops
                app.append(m.ops - setup_ops - body); bodies.append(body)
            else: assert not v
a = Asm(); a('add', 'r', 'r', 1); a('bne', 'r', 'r1', 'S'); a.L('S'); p5_loop = execute(a, dict(r=5, r1=9)).ops
print('P5: setup', setup_ops, '| valid candidates', nvalid, 'list words != (c7 + 2^32, mkent fields, c9x):', badw, '| append ops', sorted(set(app)), '| body ops (valid candidates)', sorted(set(bodies)), '| loop control', p5_loop)
assert badw == 0 and nvalid >= 6 and len(set(app)) == 1 and len(set(bodies)) == 1
# ---- P6 zero: 16 headers per iteration, memory zeroed, operations per iteration
a = Asm(); gen_zero16(a, 'hend'); zm = execute(a, dict(h=1 << 100, hend=(1 << 100) + 48, zero=0), mem={(1 << 100) + k: 7 for k in range(48)})
assert all(zm.mem[(1 << 100) + k] == 0 for k in range(48)) and zm.r['h'] == (1 << 100) + 48
zero16 = zm.ops // 3; assert zm.ops == 3 * zero16
print('P6 zero: 48 headers in 3 iterations, all zero, ops', zm.ops, '| per iteration (16 headers)', zero16)
# ---- P6 prefix: empty and nonempty header
a = Asm(); gen_prefix_body(a); pe = execute(a, dict(h=1 << 101, run=1 << 102), mem={1 << 101: 0}); assert pe.mem[1 << 101] == EMPTY
a = Asm(); gen_prefix_body(a); pn = execute(a, dict(h=1 << 101, run=1 << 102, zero=0), mem={1 << 101: 3})
assert pn.mem[1 << 101] == (1 << 102) + 6 and pn.mem[(1 << 102) + 6] == SENT and pn.r['run'] == (1 << 102) + 8
print('P6 prefix: empty header', pe.ops, 'ops, nonempty header', pn.ops, 'ops (loop control not included)')
# ---- P6 count and fill: whole variant pass on a toy.  Variants of one A0 block (real, from the enumeration) and synthetic ones (A1 = 2^32 - 3, 1, 0);
# each run covers Y in two segments with toy limits (registers E1, E2) or with the real limits (2^32, A1); headers and entries against the definition
j = 7; a0 = A0L[j]; HB = HDR | j << 64; LP = 1 << 200; vars_ = []
a1e, a2ie = EV[j]; vars_.append((a1e, a2ie))
while len(vars_) < 4:
    a2i = rr.randrange(768); lo_ = (lambda s: s.r['lo'])(execute((lambda a: (gen_enum_setup(a, a0), a)[1])(Asm()), dict(ra=A2T + 2 * a2i), tab=tab)); a1 = (lo_ + rr.randrange(1 << 29)) & M
    if valid(variant(a0, a1, A2L[a2i])): vars_.append((a1, a2i))
V = []                                       # (A1, c9x, c7, w1e): w1e = the packed fields without the G word (low 32 bits A1)
for (a1, a2i) in vars_:
    e = mkent(a0, a1, A2L[a2i], a2i, 0); V.append((a1, c9x_of(A2L[a2i]), e[0], (e[1] - gw(0)) & WORD))
for A1_ in (M - 2, 1, 0): V.append((A1_, rr.getrandbits(32), rr.getrandbits(64), (rr.getrandbits(160) << 32 | A1_) & ((1 << 224) - 1)))
def scen(A1_, kind):
    n1, n2 = min(4, (1 << 32) - A1_), min(3, A1_)
    if kind == 'mid': return 'E1', 'E2', dict(E1=A1_ + n1, E2=n2), list(range(n1)) + [(1 << 32) - A1_ + i for i in range(n2)]
    if kind == 'real1': return 1 << 32, 'E2', dict(E2=n2), list(range(M + 1 - A1_)) + [(1 << 32) - A1_ + i for i in range(n2)]
    return 'E1', 'A1', dict(E1=A1_ + n1), list(range(n1)) + [(1 << 32) - A1_ + i for i in range(A1_)]
def cases():
    for (A1_, c9x, c7, w1e) in V:
        for kind in ('mid', 'real1', 'real2'):
            if kind == 'real1' and M + 1 - A1_ > 8: continue          # the real upper limit 2^32 only where A1 is within 8 of it
            if kind == 'real2' and A1_ > 8: continue                  # the real second limit A1 only for small A1
            if A1_ == 0 and kind != 'mid': continue
            yield (A1_, c9x, c7, w1e) + scen(A1_, kind) + (kind,)
cops = {}; fops = {}; ncase = 0; mem_c = {}; expect = {}
for (A1_, c9x, c7, w1e, l1, l2, regs, Yl, kind) in cases():
    for Y in Yl:
        X = (s0((Y + A1_) & M) - A1_ + c9x) & M
        for gi, g in LIVE: k = HB + (Y << 32 | ((g - X) & M)); expect[k] = expect.get(k, 0) + 1
    a = Asm(); gen_variant_pass(a, HB, False, l1, l2)
    m = execute(a, dict(lp=LP, lpend=LP + 3, **regs), mem={**mem_c, LP: c7, LP + 1: w1e, LP + 2: c9x}); mem_c = {k: v for k, v in m.mem.items() if k < LP}
    cops[(kind, A1_ == 0, len(Yl))] = m.ops; ncase += 1
bad6 = mem_c != expect
# prefix by definition (end of each bucket), then the fill pass on the same cases
run_ = 1 << 180; hdr = {}
for k in sorted(expect): run_ += 2 * expect[k]; hdr[k] = run_; run_ += 2
mem_f = dict(hdr)
for (A1_, c9x, c7, w1e, l1, l2, regs, Yl, kind) in cases():
    a = Asm(); gen_variant_pass(a, HB, True, l1, l2)
    m = execute(a, dict(lp=LP, lpend=LP + 3, **regs), mem={**mem_f, LP: c7, LP + 1: w1e, LP + 2: c9x}); mem_f = {k: v for k, v in m.mem.items() if k < LP}
    fops[(kind, A1_ == 0, len(Yl))] = m.ops
# every bucket against the definition: the multiset of (c7, w1e + gw(g)) of the (Y, variant, g) that hash to it; the real variants' entries equal mkent
want = {}
for (A1_, c9x, c7, w1e, l1, l2, regs, Yl, kind) in cases():
    for Y in Yl:
        X = (s0((Y + A1_) & M) - A1_ + c9x) & M
        for gi, g in LIVE: want.setdefault(HB + (Y << 32 | ((g - X) & M)), []).append((c7, (w1e + gw(gi)) & WORD))
for k in expect:
    st = mem_f[k]; got = sorted(tuple(mem_f[st + 2 * i + w] for w in range(2)) for i in range(expect[k]))
    bad6 += got != sorted(want[k]) or st != hdr[k] - 2 * expect[k]
for (a1, a2i), (A1_, c9x, c7, w1e) in zip(vars_, V):
    for gi, g in LIVE: bad6 += (c7, (w1e + gw(gi)) & WORD) != mkent(a0, a1, A2L[a2i], a2i, gi)
# operations per iteration: the two-segment path (A1 != 0) with two iteration counts; every run on that path is fixed + iterations x per-iteration
def per_iter(ops):
    two = {k: o for k, o in ops.items() if not k[1] and k[0] == 'mid'}; ks = sorted(two, key=lambda k: k[2]); k1, k2 = ks[0], ks[-1]
    it = (two[k2] - two[k1]) // (k2[2] - k1[2]); fixed = two[k1] - it * k1[2]
    assert all(o == fixed + it * k[2] for k, o in two.items())
    if not getattr(Machine, 'IMM', False):                       # (the limit of the toy runs is a register, the real limit 2^32 an instruction field: no difference in the count)
        assert all(o == fixed + it * k[2] for k, o in ops.items() if not k[1]) and all(o < fixed + it * k[2] for k, o in ops.items() if k[1])
    else: it += 1                                                # immediates charged: the branch back to seg1 compares with the constant 2^32
    return it, fixed
cit, cvar = per_iter(cops); fit, fvar = per_iter(fops)
print('P6 toy: %d variant runs (4 real variants, A1 = 2^32 - 3, 1 and 0; the real limits 2^32 and A1 as well as toy limits), %d headers, %d entries: count and fill == definition, %d mismatches'
      % (ncase, len(expect), sum(expect.values()), bad6))
print('P6 count: %d ops per iteration (incl. loop branch), %d per variant (loads, A1, both segment setups, guard, list-loop branch);' % (cit, cvar),
      'fill: %d ops per iteration, %d per variant' % (fit, fvar))
assert bad6 == 0
# P1..P4: the values printed by t_pre1.py (A.5), which executes those bodies on the shipped vt38.py
p1 = {"G_hit_ops": 117, "G_nonhit_max_ops": 115, "F7_in_ops": 25, "F7_out_ops": 22, "A2_hit_ops": 41, "A2_nonhit_max_ops": 39, "A2REC_total_ops": 39168, "GREC_total_ops": 3072}
p2 = dict(P5_SETUP=setup_ops, P5_BODY_MAX=bodies[0], P5_APPEND=app[0], P5_LOOP=p5_loop, P6_ZERO16=zero16, P6_COUNT_IT=cit, P6_COUNT_VAR=cvar, P6_FILL_IT=fit, P6_FILL_VAR=fvar,
          P6_PREFIX_EMPTY=pe.ops, P6_PREFIX_NONEMPTY=pn.ops)
p1.update(LIVE_ops=live_max, LIVE_g=live_g)
json.dump(p1, open(os.path.join(RUNS, 'pre1.json'), 'w')); json.dump(p2, open(os.path.join(RUNS, 'pre2.json'), 'w'))
print('pre1.json', p1); print('pre2.json', p2)
