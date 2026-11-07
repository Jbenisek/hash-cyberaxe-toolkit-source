"""bf.c DFS vs brute-force kmin (itertools + gd_order.propagate) on random small systems: bf at kmax=kmin must find
a covering set of size kmin and none smaller."""
import os, random, subprocess, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "orig"))
from sat_unit import rand_system, kmin_bf
from rules import nc_eqs
rng = random.Random(9)
bad = 0
lines = []
os.makedirs(os.path.join(HERE, "unit"), exist_ok=True)
for trial in range(40):
    eqs, const, vars_ = rand_system(rng, rng.randint(9, 16), rng.randint(4, 12))
    km = kmin_bf(eqs, const, vars_)
    ix = {v: i for i, v in enumerate(vars_)}
    ncq = nc_eqs(eqs, const)
    fn = os.path.join(HERE, "unit", f"bf{trial}.txt")
    with open(fn, "w") as fh:
        fh.write(f"{len(vars_)} {len(ncq)} 0\n" + " ".join(vars_) + "\n")
        for _, vs in ncq:
            fh.write(" ".join(str(ix[v]) for v in vs) + "\n")
    r = subprocess.run(["wsl", "-d", "Ubuntu", "--", "bash", "-c",
                        f"cd './research/newpaths/audit' && ./bf3 unit/bf{trial}.txt {km} 0 1"],
                       capture_output=True, text=True)
    sizes = [int(l.split()[1].split("=")[1]) for l in r.stdout.split("\n") if l.startswith("FOUND")]
    ok = (km == 0 or (sizes and min(sizes) == km))
    bad += not ok
    lines.append(f"trial {trial}: vars={len(vars_)} kmin={km} bf found sizes min={min(sizes) if sizes else None} n={len(sizes)} {'OK' if ok else 'BAD'}")
lines.append(f"failures: {bad} of 40")
print("\n".join(lines[-6:]))
open(os.path.join(HERE, "bf_unit.log"), "w").write("\n".join(lines) + "\n")
