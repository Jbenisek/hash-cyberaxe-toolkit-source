from common import *
import json, re, random
B = base()
def dt(**kw): return led(**kw)["score"] - B["score"]
res = {}
# ---- parse the 595-op straight-line code
lines = rho._SRC.split("\n")[1:-2]
ops = []
for ln in lines:
    ln = ln.strip(); name, expr = ln.split("=", 1)
    m = re.match(r"^(\w+)\s*(<<|>>|\+|&|\||\^)\s*(\w+)$", expr)
    a, op, b_ = m.groups(); ops.append((name, a, op, b_))
assert len(ops) == 595
isimm = lambda x: x.isdigit()
imm_ops = [o for o in ops if isimm(o[3]) or isimm(o[1])]
shift_ops = [o for o in ops if o[2] in ("<<", ">>")]
mask_imm = [o for o in imm_ops if o[2] == "&"]
other_imm = [o for o in imm_ops if o[2] in ("+", "^")]
dist256 = {o[3] for o in imm_ops if o[2] not in ("<<", ">>")}
res["imm"] = dict(ops=len(ops), ops_with_256bit_immediate=len(imm_ops) - len(shift_ops), shift_ops_with_count=len(shift_ops),
                  and_imm=len(mask_imm), add_xor_imm=len(other_imm), distinct_256bit_constants=len(dist256),
                  distinct_shift_counts=len({o[3] for o in shift_ops}))
n_use = res["imm"]["ops_with_256bit_immediate"]
res["imm"]["scenario_load_per_use_delta_score"] = dt(ph=595 + n_use)
res["imm"]["scenario_shift_counts_also_loaded_delta_score"] = dt(ph=595 + n_use + len(shift_ops))
ret = rho._SRC.strip().split("\n")[-1]
outs = set(re.findall(r"t\d+", ret))
assert len(outs) == 8

def live_peak(ops, outs):
    last = {}
    for k, (n, a, op, b_) in enumerate(ops):
        for x in (a, b_):
            if not isimm(x): last[x] = k
    for o in outs: last[o] = len(ops)
    live = {f"i{i}" for i in range(8, 16)}
    peak = len(live)
    for k, (n, a, op, b_) in enumerate(ops):
        live.add(n); peak = max(peak, len(live))
        for x in (a, b_):
            if not isimm(x) and last.get(x) == k: live.discard(x)
        if n not in last: live.discard(n)
    return peak
res["regs"] = dict(peak_live_emitted_order=live_peak(ops, outs))

def belady(ops, outs, R):
    uses = {}
    for k, (n, a, op, b_) in enumerate(ops):
        for x in (a, b_):
            if not isimm(x): uses.setdefault(x, []).append(k)
    BIG = 10**9
    def nextuse(v, k):
        for u in uses.get(v, []):
            if u >= k: return u
        return BIG - 1 if v in outs else BIG
    inreg = {f"i{i}" for i in range(8, 16)}; inmem = set(); stores = loads = 0
    for k, (n, a, op, b_) in enumerate(ops):
        need = [x for x in (a, b_) if not isimm(x)]
        for x in need:
            if x not in inreg:
                loads += 1
                while len(inreg) >= R:
                    v = max((y for y in inreg if y not in need), key=lambda y: nextuse(y, k))
                    inreg.discard(v)
                    if v not in inmem and nextuse(v, k) < BIG: stores += 1; inmem.add(v)
                inreg.add(x)
        for x in need:
            if nextuse(x, k + 1) >= BIG: inreg.discard(x)
        while len(inreg) >= R:
            v = max(inreg, key=lambda y: nextuse(y, k + 1))
            inreg.discard(v)
            if nextuse(v, k + 1) < BIG and v not in inmem: stores += 1; inmem.add(v)
        inreg.add(n)
    return stores, loads
sp = {}
for R in (12, 16, 20, 24, 28, 32, 40, 48, 64):
    s, l = belady(ops, outs, R); sp[R] = (s, l, dt(ph=595 + s + l))
res["regs"]["belady_by_R(stores,loads,delta_score)"] = sp
for R in range(8, 70):
    s, l = belady(ops, outs, R)
    if s == 0 and l == 0: res["regs"]["min_R_zero_spill_belady_emitted_order"] = R; break
res["regs"]["with_constants_in_regs_need"] = res["regs"]["min_R_zero_spill_belady_emitted_order"] + len(dist256)

def reschedule(ops, outs):
    defs = {n: (n, a, op, b_) for (n, a, op, b_) in ops}
    deps = {n: [x for x in (a, b_) if x in defs] for (n, a, op, b_) in ops}
    rem = {}
    for (n, a, op, b_) in ops:
        for x in (a, b_):
            if not isimm(x): rem[x] = rem.get(x, 0) + 1
    done = set(); live = {f"i{i}" for i in range(8, 16)}; peak = len(live)
    while len(done) < len(ops):
        best = None
        for n in defs:
            if n in done or not all(x in done for x in deps[n]): continue
            _, a, op, b_ = defs[n]
            freed = sum(1 for x in set([a, b_]) if not isimm(x) and rem[x] == [a, b_].count(x) and x not in outs)
            sc = (-freed, int(n[1:]))
            if best is None or sc < best[0]: best = (sc, n)
        n = best[1]; _, a, op, b_ = defs[n]
        live.add(n); peak = max(peak, len(live))
        for x in [a, b_]:
            if not isimm(x): rem[x] -= 1
        for x in set([a, b_]):
            if not isimm(x) and rem[x] == 0 and x not in outs: live.discard(x)
        if n not in rem and n not in outs: live.discard(n)
        done.add(n)
    return peak
res["regs"]["greedy_reschedule_peak_live"] = reschedule(ops, outs)

def trace_pitch(p):
    save = (rho.PITCH, rho.LIM, rho.REP)
    rho.PITCH, rho.LIM = p, 1 << p
    rho.REP = sum(1 << (p * i) for i in range(7))
    try:
        src, nops, by = rho.build_hash()
    finally:
        rho.PITCH, rho.LIM, rho.REP = save
    return nops, by
res["rot"] = {}
for p in (33, 34, 35, 36):
    try: res["rot"][f"pitch{p}_7lanes"] = trace_pitch(p)
    except Exception as e: res["rot"][f"pitch{p}_7lanes"] = "fail:" + repr(e)[:60]
by = rho.PH_BY
swar = 595 - by["add"] + 6 * by["add"]
res["rot"]["pitch32_8lanes_swar_add_bound"] = dict(ops=swar, per_instance=swar / 8, shipped_per_instance=595 / 7)
res["rot"]["rotations"] = dict(variable=80, ops_each=5, share_of_595=400 / 595, constant_rotations_folded=16)
res["rot"]["delta_score_per_op_saved_per_batch"] = dt(ph=594)
res["rot"]["if_rot_cost_4"] = dt(ph=595 - 80)
res["rot"]["if_rot_cost_3"] = dt(ph=595 - 160)

res["cmpbr"] = {}
res["cmpbr"]["U_sweep(score_delta, mem)"] = {U: (dt(U=U), led(U=U)["mem"]) for U in (1, 2, 4, 8, 16, 17, 18, 19, 20, 32, 64)}
res["cmpbr"]["stage1_ops_sweep"] = {s: dt(stage1=s) for s in (2, 3, 4, 5)}
res["cmpbr"]["s1_sweep"] = {s: dt(s1=s) for s in (16, 24, 28, 31, 32)}
res["cmpbr"]["loop_ops_sweep"] = {l: dt(loop=l) for l in (0, 1, 3, 6)}
res["cmpbr"]["group_filter_U16"] = dict(delta=dt(group=True), per_body=led(group=True)["per_body"], base_per_body=B["per_body"])
res["cmpbr"]["group_filter_U19"] = dict(delta=dt(group=True, U=19), mem=led(U=19)["mem"])
res["cmpbr"]["group_filter_U16_stage2_recompute_cost"] = dt(group=True, st2=300 + 16 * 595 + 100)
json.dump(res, open("a_machine.json", "w"), indent=1, default=str)
print(json.dumps(res, indent=1, default=str))
