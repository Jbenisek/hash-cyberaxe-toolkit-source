import os, sys, time, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "impl"))
import outer, solver
recs = []
c = {}
for r in outer.iter_passes(3, 0, 6000, counts=c):
    recs.append(r)
print("steps", c["steps"], "passes", len(recs))
solver.arrays()
rnd = random.Random(1)
t = time.time(); roots = 0
for r in recs:
    Q, y, E, X = int(r["Y9"], 16), int(r["y"], 16), int(r["omega"], 16), int(r["X"], 16)
    s = solver.solve(Q, y, E, X=X, g7=False, precheck=False)
    roots += len(s["roots"])
print("nog7 per step s", (time.time() - t) / len(recs), "roots", roots)
t = time.time(); roots = 0
for r in recs:
    Q, y, E, X = int(r["Y9"], 16), int(r["y"], 16), int(r["omega"], 16), int(r["X"], 16)
    s = solver.solve(Q, y, E, C=rnd.getrandbits(32), B=rnd.getrandbits(32), X=X, g7=True, precheck=True)
    roots += len(s["roots"])
print("g7+pre per step s", (time.time() - t) / len(recs), "roots", roots)
