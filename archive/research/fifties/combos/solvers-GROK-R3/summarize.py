"""Collect z3 outcomes: result line, model vs true guess (point.json), z3 -st time/memory/conflicts. Writes summary.txt."""
import os, re, json
D = os.path.dirname(os.path.abspath(__file__))
truth = json.load(open(os.path.join(D, "point.json")))["true_guess"]
rows = []
for f in sorted(os.listdir(D)):
    if not f.endswith(".out"): continue
    t = open(os.path.join(D, f)).read()
    res = t.split("\n", 1)[0].strip()
    model = dict((k, v.lower()) for k, v in re.findall(r"\(\|([^|]+)\| #x([0-9a-fA-F]{8})\)", t))
    match = (model == truth) if model else None
    st = {k: v for k, v in re.findall(r":([a-z.\-]+)\s+([0-9.]+)", t) if k in ("time", "max-memory", "sat-conflicts", "conflicts", "sat-decisions", "decisions")}
    rows.append(f"{f[:-4]:12s} result={res:8s} model_equals_true_guess={match} stats={st}")
open(os.path.join(D, "summary.txt"), "w").write("\n".join(rows) + "\n")
print("\n".join(rows))
