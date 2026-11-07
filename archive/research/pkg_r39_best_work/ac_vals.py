import sys, json
sys.path.insert(0, sys.argv[1])
import r39joint as J
req = json.load(open(sys.argv[2]))
for t in req['trials'][:4]: J._e2(t['trial'], int(t['seed'][:16], 16))
G = J._G_SEQ; n = len(G); print("groups", n)
for k, name in enumerate(("W9 in F9", "W17[0]", "W18[0]")):
    xs = [g[k] for g in G]; m = sum(xs) / n; v = sum((x - m) ** 2 for x in xs)
    r = sum((xs[j] - m) * (xs[j + 1] - m) for j in range(n - 1)) / v
    print("%s r=%.4f |r|sqrt(n)=%.2f" % (name, r, abs(r) * n ** 0.5))
