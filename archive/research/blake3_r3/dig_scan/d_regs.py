from common import *
import re, json
B = base()
lines = rho._SRC.split("\n")[1:-2]
ops = []
for ln in lines:
    name, expr = ln.strip().split("=", 1)
    a, op, b_ = re.match(r"^(\w+)\s*(<<|>>|\+|&|\||\^)\s*(\w+)$", expr).groups()
    ops.append((name, a, op, b_))
ret = rho._SRC.strip().split("\n")[-1]
outs = set(re.findall(r"t\d+", ret))
BIG = 10**9

def belady(ops, outs, R, perm=(), const_regs=True, count_shift=True):
    """Min-spill (Belady) count with constants as register operands. perm = extra values live through the whole batch."""
    o2 = []
    for (n, a, op, b_) in ops:
        if a.isdigit(): a = "c" + a
        if b_.isdigit():
            b_ = ("s" + b_) if op in ("<<", ">>") else ("c" + b_)
        o2.append((n, a, op, b_))
    uses = {}
    for k, (n, a, op, b_) in enumerate(o2):
        for x in (a, b_): uses.setdefault(x, []).append(k)
    for p in perm: uses.setdefault(p, []).append(len(o2))
    def nextuse(v, k):
        for u in uses.get(v, []):
            if u >= k: return u
        return BIG - 1 if v in outs else BIG
    consts = {x for x in uses if x[0] in "cs"} if const_regs else set()
    inreg = {f"i{i}" for i in range(8, 16)} | set(perm) | consts
    inmem = set(); stores = loads = 0
    # constants are reloadable (no store needed): treat as in memory already
    inmem |= {x for x in uses if x[0] in "cs"}
    for k, (n, a, op, b_) in enumerate(o2):
        need = [a, b_]
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
res = {}
for label, perm, cr in (("no_imm_all_consts_in_regs", (), True), ("no_imm_group_filter(+8 inputs,+acc,+2 consts)", tuple(f"p{i}" for i in range(11)), True),
                        ("imm_ok_group_filter(+8 inputs,+acc)", tuple(f"p{i}" for i in range(9)), False)):
    row = {}
    for R in (32, 40, 48, 56, 64):
        s, l = belady(ops, outs, R, perm=perm, const_regs=cr)
        row[R] = (s, l, led(ph=595 + s + l)["score"] - B["score"])
    res[label] = row
json.dump(res, open("d_regs.json", "w"), indent=1)
print(json.dumps(res, indent=1))
