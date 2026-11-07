# t_pre_d.py - the changed preprocessing bodies of vtpre.py as counted code, against their definitions; writes
# runs/pre1.json and runs/pre2.json (the base values with LIVE_ops, LIVE_g, P5_SETUP, P5_APPEND, P6_COUNT, P6_FILL
# re-measured by executing the bodies).  usage: t_pre_d.py <dir of vt38.py> <runs dir>
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
tab = tables(); EV = entry_variants(); setup_ops = None; app = []; nvalid = 0; badw = 0
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
                badw += [m.mem[(1 << 170) + k] for k in range(3)] != [e[0], e[1], c9x_of(A2L[a2i])]
                b2 = Asm(); gen_enum_setup(b2, a0); gen_enum_body(b2, a0, 'END'); body = execute(b2, dict(ra=A2T + 2 * a2i, r=r_), tab=tab).ops - setup_ops
                app.append(m.ops - setup_ops - body)
            else: assert not v
print('P5: setup', setup_ops, '| valid candidates', nvalid, 'list words != (c7 + 2^32, mkent fields, c9x):', badw, '| append ops', sorted(set(app)))
assert badw == 0 and nvalid >= 6 and len(set(app)) == 1
# ---- P6 count and fill on a toy: variants of one A0 block, a few Y; headers and entries against the definition
j = 7; a0 = A0L[j]; HB = HDR | j << 64; vars_ = []
a1e, a2ie = EV[j]; vars_.append((a1e, a2ie))
while len(vars_) < 5:
    a2i = rr.randrange(768); lo_ = (lambda s: s.r['lo'])(execute((lambda a: (gen_enum_setup(a, a0), a)[1])(Asm()), dict(ra=A2T + 2 * a2i), tab=tab)); a1 = (lo_ + rr.randrange(1 << 29)) & M
    if valid(variant(a0, a1, A2L[a2i])): vars_.append((a1, a2i))
Ys = [rr.getrandbits(32) for _ in range(6)]; cops = []; fops = []; mem = {}
for (a1, a2i) in vars_:
    for Y in Ys:
        a = Asm(); gen_count_body(a, HB); m = execute(a, dict(Y=Y, A1=a1, c9x=c9x_of(A2L[a2i])), mem=mem); mem = m.mem; cops.append(m.ops)
expect = {}
for (a1, a2i) in vars_:
    for Y in Ys:
        X = (s0((Y + a1) & M) - a1 + c9x_of(A2L[a2i])) & M
        for gi, g in LIVE: k = HB + (Y << 32 | ((g - X) & M)); expect[k] = expect.get(k, 0) + 1
assert {k: v for k, v in mem.items()} == expect
# prefix by definition (end of each bucket), then the fill body; entries against mkent
run_ = 1 << 180; hdr = {}
for k in sorted(expect): run_ += 2 * expect[k]; hdr[k] = run_; run_ += 2
mem = dict(hdr)
for (a1, a2i) in vars_:
    e = mkent(a0, a1, A2L[a2i], a2i, 0)
    for Y in Ys:
        a = Asm(); gen_fill_body(a, HB); m = execute(a, dict(Y=Y, A1=a1, c9x=c9x_of(A2L[a2i]), c7=e[0], w1e=e[1]), mem=mem); mem = m.mem; fops.append(m.ops)
bad6 = 0
for k in expect:
    st = mem[k]; got = [tuple(mem[st + 2 * i + w] for w in range(2)) for i in range(expect[k])]
    for c7, fgw in got:
        gi = [g for g, _ in LIVE if gw(g) == (fgw >> 160)]; ok = len(gi) == 1
        if ok:
            f = fgw & ((1 << 160) - 1)
            (a1, a2i) = [(x, y) for (x, y) in vars_ if mkent(a0, x, A2L[y], y, 0)[1] == f][0]
            Y = [y for y in Ys if HB + (y << 32 | ((GL[gi[0]] - (s0((y + a1) & M) - a1 + c9x_of(A2L[a2i]))) & M)) == k]
            ok = len(Y) >= 1 and (c7, fgw) == mkent(a0, a1, A2L[a2i], a2i, gi[0])
        bad6 += not ok
print('P6 toy: %d variants x %d Y: %d headers, %d entries, count == definition, entries == mkent: %d mismatches | count ops %s fill ops %s'
      % (len(vars_), len(Ys), len(expect), sum(expect.values()), bad6, sorted(set(cops)), sorted(set(fops))))
assert bad6 == 0 and len(set(cops)) == 1 and len(set(fops)) == 1
p1 = {"G_hit_ops": 117, "G_nonhit_max_ops": 115, "F7_in_ops": 25, "F7_out_ops": 22, "A2_hit_ops": 41, "A2_nonhit_max_ops": 39, "A2REC_total_ops": 39168, "GREC_total_ops": 3072}
p2 = {"P5_SETUP": 35, "P5_BODY_MAX": 56, "P5_APPEND": 43, "P5_LOOP": 3, "P6_COUNT": 145, "P6_FILL": 189, "P6_PREFIX_EMPTY": 6, "P6_PREFIX_NONEMPTY": 11}
p1.update(LIVE_ops=live_max, LIVE_g=live_g); p2.update(P5_SETUP=setup_ops, P5_APPEND=app[0], P6_COUNT=cops[0], P6_FILL=fops[0])
json.dump(p1, open(os.path.join(RUNS, 'pre1.json'), 'w')); json.dump(p2, open(os.path.join(RUNS, 'pre2.json'), 'w'))
print('pre1.json', p1); print('pre2.json', p2)
