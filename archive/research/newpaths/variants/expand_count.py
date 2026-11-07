import sys, math
from gd_var import build, closure, e_inputs
w = sys.argv[1]
held = [x for x in e_inputs("02") if x != w] if w != "none" else e_inputs("02")
eqs, const, vars_ = build("02", "partial", 64, held)
base = closure(eqs, const)
cls = {}
for v in vars_:
    if v in base: continue
    cls.setdefault(frozenset(closure(eqs, set(const) | {v})), []).append(v)
rep = {}
for k, mem in cls.items():
    for v in mem: rep[v] = mem
names = open(f"models/part_02_t0_{w}.mdl.vars").read().split() if w != "none" else open("models/fixed_02_64_t0.mdl.vars").read().split()
f = f"res/part_02_t0_{w}_k8.out" if w != "none" else "res/fixed_02_64_t0_k8.out"
tot = 0; mx = 0
for l in open(f):
    if not l.startswith("SOL"): continue
    g = [names[int(x)] for x in l.split()[1:]]
    p = math.prod(len(rep[x]) for x in g); tot += p; mx = max(mx, p)
print(w, "classes", len(cls), "class sizes>1:", sorted([len(m) for m in cls.values() if len(m) > 1], reverse=True), "expanded solutions", tot, "max per canonical", mx)
