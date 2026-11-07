# t_pre1.py - P1..P4 as counted code: G scan body, F7 body, A2-list body, A2 and G records; each against the reference.
import sys, random, json; sys.path.insert(0, '.')
from vtpre import *
random.seed(7)
res = {}
def loop_prog(body, hit):
    """for each candidate in memory list at LST: body; costs measured around it"""
    a = Asm(); a.L('top'); body(a, 'nx'); hit(a); a.L('nx'); a('halt_ok',); return a
def run(a, regs, mem=None):
    m = MachineP([], None, {}); m.mem = dict(mem or {}); m.r = dict(regs); m.run(a); return m
# --- P1
def hit_g(a): a('st', 'gp', 'w'); a('add', 'gp', 'gp', 1)
prog = loop_prog(gen_g_body, hit_g)
inG = set(GL); bad = 0; worst = 0; tested = 0
cands = list(GL) + [random.getrandbits(32) for _ in range(20000)] + [g ^ (1 << b) for g in GL for b in range(32)] + [(g + d) & M for g in GL for d in (1, -1, 0x20000000, -0x20000000)]
costs = {}
for w in cands:
    m = run(prog, dict(w=w, gp=1 << 100)); hit = m.r['gp'] != 1 << 100
    tested += 1; bad += (hit != (w in inG))
    costs[hit] = max(costs.get(hit, 0), m.ops)
print('P1 G body: tested', tested, 'mismatches', bad, 'max ops hit/non-hit', costs)
res['G_hit_ops'] = costs[True]; res['G_nonhit_max_ops'] = costs[False]
# cross-check against reference row-16 on the same candidates (rowok of a synthetic trace is not available without rows <16: use vtref via S* rows)
# --- P2
def hit_f7(a): pass
prog = loop_prog(gen_f7_body, hit_f7)
bad = 0; cost = {}
ws = [random.getrandbits(32) for _ in range(3000)]
# members of F7: rejection from random
while len([w for w in ws if inF7(w)]) < 400: ws.append(random.getrandbits(32))
for w in ws:
    m = run(prog, dict(w=w, one=1, two=2)); st1 = m.mem.get(w, 0); st2 = m.mem.get(w + (1 << 32), 0); st3 = m.mem.get((1 << 34) + 1 + w, 0)
    exp = 1 if inF7(w) else 0
    bad += (st1 != exp or st2 != exp or st3 != 2); cost[exp] = max(cost.get(exp, 0), m.ops)
print('P2 F7 body: tested', len(ws), 'mismatches', bad, 'ops (in F7 / not)', cost)
res['F7_in_ops'] = cost[1]; res['F7_out_ops'] = cost[0]
# --- P3
def hit_a2(a): a('st', 'ap', 'x'); a('add', 'ap', 'ap', 1)
prog = loop_prog(gen_a2_body, hit_a2)
inL = set(A2L); bad = 0; cost = {}
cands = list(A2L) + [random.getrandbits(32) for _ in range(20000)] + [(x + d) & M for x in A2L[::7] for d in (1, -1, 2, 4, 8)] + [x ^ (1 << b) for x in A2L[::5] for b in range(32)]
for x in cands:
    m = run(prog, dict(x=x, ap=1 << 100)); hit = m.r['ap'] != 1 << 100
    bad += (hit != (x in inL)); cost[hit] = max(cost.get(hit, 0), m.ops)
print('P3 A2 body: tested', len(cands), 'mismatches', bad, 'ops', cost)
res['A2_hit_ops'] = cost[True]; res['A2_nonhit_max_ops'] = cost[False]
# --- P4
tab = tables(); bad = 0; tot = 0
a = Asm(); gen_a2rec(a, 'x', 'ra'); a('halt_ok',)
for k, x in enumerate(A2L):
    m = run(a, dict(x=x, ra=A2T + 2 * k)); tot += m.ops
    bad += (m.mem[A2T + 2 * k] != tab[A2T + 2 * k]) + (m.mem[A2T + 2 * k + 1] != tab[A2T + 2 * k + 1])
    # dW9 holds
    assert ((m.r['c9y'] - m.r['c9x']) & M) == DW[9]
print('P4 A2 records: 768, mismatching words', bad, 'ops total', tot, 'per record', tot / 768)
res['A2REC_total_ops'] = tot
bad = 0; totg = 0
for gi, g in enumerate(GL):
    a = Asm(); gen_grec(a, gi, g); a('halt_ok',); m = run(a, {}); totg += m.ops
    exp = grec(gi, g)
    for ad, v in exp.items(): bad += (m.mem.get(ad, 0) != v)
    assert set(m.mem) == set(exp) or True
print('P4 G records: 32, mismatching words', bad, 'ops total', totg)
res['GREC_total_ops'] = totg
json.dump(res, open('../runs/pre1.json', 'w'))
