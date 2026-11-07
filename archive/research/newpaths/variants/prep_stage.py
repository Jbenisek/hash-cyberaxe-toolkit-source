"""Write input for stagecheck.c: classes of the fixed-CV model (members as indices of the CV-variable model) and the
canonical minimum solutions as class ids.  usage: python prep_stage.py <fixed-CV model name> <cv model name> <sol file> <out> <half> <held or ->"""
import sys
from gd_var import build, closure, e_inputs
fm, cm, solf, out, half, heldarg = sys.argv[1:7]
held = e_inputs(half) if heldarg == "-" else heldarg.split(",")
eqs, const, vars_ = build(half, "partial", 64, held)
base = closure(eqs, const)
cls, cid = [], {}
keyidx = {}
for v in vars_:
    if v in base: continue
    k = frozenset(closure(eqs, set(const) | {v}))
    if k not in keyidx:
        keyidx[k] = len(cls); cls.append([])
    cls[keyidx[k]].append(v); cid[v] = keyidx[k]
fnames = open(f"models/{fm}.mdl.vars").read().split()
cnames = open(f"models/{cm}.mdl.vars").read().split()
cix = {v: i for i, v in enumerate(cnames)}
with open(out, "w") as fh:
    fh.write(f"classes {len(cls)}\n")
    for mem in cls:
        fh.write(f"{len(mem)} " + " ".join(str(cix[v]) for v in mem) + "\n")
    sols = [l.split()[1:] for l in open(solf) if l.startswith("SOL")]
    fh.write(f"sols {len(sols)}\n")
    for s in sols:
        fh.write(" ".join(str(cid[fnames[int(x)]]) for x in s) + "\n")
print(out, len(cls), "classes", len(sols), "solutions")
