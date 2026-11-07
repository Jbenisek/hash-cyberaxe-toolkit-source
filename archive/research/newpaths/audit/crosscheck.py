"""Cross-check bf.c closure against gd_order.propagate on random guess sets (plain rules)."""
import random, subprocess, sys
sys.dont_write_bytecode = True
sys.path.insert(0, __file__.rsplit("\\", 1)[0] + "\\orig")
from gd_order import build, propagate
for variant in ("fixed", "outhalf"):
    eqs, const, vars_ = build(variant, "len64")
    rng = random.Random(5)
    sets = [["K2.c1", "K3.d1", "K3.d2", "C3.a2", "m0", "D1.d1", "K2.d2", "C0.a1"]] if variant == "fixed" else []
    sets += [rng.sample(vars_, rng.randint(3, 16)) for _ in range(400)]
    py = []
    for s in sets:
        known = set(const) | set(s)
        propagate(eqs, known, [])
        py.append(len(known) - len(const))
    inp = "\n".join(" ".join(s) for s in sets) + "\n"
    r = subprocess.run(["wsl", "-d", "Ubuntu", "--", "bash", "-c",
                        f"./research/newpaths/audit/bf ./research/newpaths/audit/rules_{variant}_len64_plain.txt check"],
                       input=inp, capture_output=True, text=True)
    c = [int(l.split()[1].split("=")[1].split("/")[0]) for l in r.stdout.split("\n") if l.startswith("guesses")]
    mism = sum(a != b for a, b in zip(py, c))
    print(f"{variant}: {len(sets)} guess sets, closure sizes python vs bf.c mismatches: {mism} (n compared {len(c)});"
          f" first set: python {py[0]} bf {c[0]} / {len(vars_)}")
