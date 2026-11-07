"""Print the solving order of one solution: guesses, number of words solved after each guess, and the check equations."""
import sys
from export_model import model
mdl, solfile, half, mode, L, t, idx = sys.argv[1:8]
eqs, const, vars_, macros = model(half, mode, int(L), int(t))
sols = [list(map(int, l.split()[1:])) for l in open(solfile) if l.startswith("SOL")]
g = [vars_[i] for i in sols[int(idx)]]
known = set(const); used = set(); order = []
def prop():
    ch = True
    while ch:
        ch = False
        for name, vs in eqs:
            if name in used: continue
            unk = [v for v in vs if v not in known]
            if len(unk) == 1:
                known.add(unk[0]); used.add(name); ch = True
        for trig, tgt in macros:
            if tgt not in known and all(x in known for x in trig):
                known.add(tgt); ch = True
prop()
for x in g:
    before = len(known); known.add(x); prop()
    order.append(f"{x}(+{len(known) - before})")
checks = [n for n, vs in eqs if n not in used]
print("order:", " ".join(order))
print("checks:", checks)
