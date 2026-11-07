#!/usr/bin/env python3
"""exact lens: on which of the eight words each name of the printed lines depends (read off the lines), and a
numerical confirmation. Says what is shared by the trials of a run of 6.4."""
import os, sys
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from exact_check import read_displays, compile_steps, CONST, EIGHT, SIX, M, shake_words, member
disp, _ = read_displays()
dep = {w: {w} for w in EIGHT}
dep["Y4"] = {"y"}
for d in disp:
    s = set()
    for r in d["reads"]:
        s |= dep.get(r, set())
    dep[d["name"]] = s
def show(title, names):
    print(title)
    for n in names:
        print("   %-6s <- %s" % (n, " ".join(w for w in EIGHT if w in dep[n])))
show("names of the lines and the words they descend from:", ["X9", "X14", "X4", "C0.b1", "w6", "w7", "Y8", "Y12",
     "X8", "X13", "D2.c1", "X12", "X6", "X1", "w12", "w0", "w2", "E1.a1", "E1.d1", "E3.h1"])
run4 = {"C0.c1", "D3.d1", "S15", "S9"}
allrun = [d["name"] for d in disp if dep[d["name"]] <= run4]
noc0d1 = [d["name"] for d in disp if d["step"] == "O" and "C0.d1" not in dep[d["name"]]]
print("names that descend from the four words of step 1 alone (same in EVERY trial of a run):", " ".join(allrun))
print("outer lines that do not descend from C0.d1: %d of 29 (%s ...)" % (len(noc0d1), " ".join(noc0d1[:8])))
print("names of step Y that do not descend from C0.d1:", " ".join(d["name"] for d in disp if d["step"] == "Y"
      and "C0.d1" not in dep[d["name"]]))
# numerical: change C0.d1 and X2, keep the rest
fn = compile_steps(disp)
same = tot = 0
for t in range(2000):
    r = shake_words("exact dep %d" % t, 12)
    vals = []
    for k in range(2):
        e = [r[0], r[1 + 6 * k] % 1424469, r[2], r[3], r[4], r[5], r[6 + 2 * k], member(r[9] % 131072)]
        n = dict(CONST); n.update(zip(EIGHT, e)); n["Y4"] = e[7]
        for s in "OMYTR": fn[s](n)
        vals.append(n)
    tot += 1
    same += all(vals[0][k] == vals[1][k] for k in ("Y8", "Y12", "X9", "X14", "X4", "C0.b1", "w5", "w6", "w7"))
print("numerical: C0.d1 and X2 changed, the other six words kept: Y8, Y12, X9, X14, X4, C0.b1, w5, w6, w7 the "
      "same in %d of %d pairs" % (same, tot))
