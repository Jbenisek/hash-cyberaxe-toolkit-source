"""End-to-end test of gd_sat.encode (unmodified copy) on random small equation systems.
gd_sat.build is replaced by a generator of random systems (3- and 4-word equations over n words, a few constants).
For each system the exact minimum guess count kmin is found by brute force over subsets (closure = gd_order.propagate),
then CNFs at k = kmin-1 and k = kmin with T = n are solved by kissat in WSL: expect UNSAT then SAT, and the decoded
guess set at kmin must cover everything under gd_order.propagate.
"""

# Publication path adapter: resolve data paths from the extracted source tree.
def _hca_public_path_text(value):
    if "__HCA_WORKSPACE__/" not in value:
        return value
    import os as _hca_os
    from pathlib import Path as _hca_Path
    root = _hca_os.environ.get("HASHCYBERAXE_WORKSPACE")
    if root is None:
        here = _hca_Path(__file__).resolve().parent
        root = next((str(p) for p in (here, *here.parents) if (p / "research").is_dir()), None)
    if root is None:
        raise FileNotFoundError("Extract the research source tree, or set HASHCYBERAXE_WORKSPACE to its archive directory.")
    return value.replace("__HCA_WORKSPACE__/", str(_hca_Path(root).resolve()).replace("\\", "/") + "/")

import itertools
import os
import random
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = __file__.rsplit("\\", 1)[0]
sys.path.insert(0, HERE + "\\orig")
import gd_sat  # noqa: E402
from gd_order import propagate  # noqa: E402

WSL_DIR = _hca_public_path_text('__HCA_WORKSPACE__/research/newpaths/audit/unit')
os.makedirs(HERE + "\\unit", exist_ok=True)


def rand_system(rng, n, m):
    words = [f"w{i}" for i in range(n)]
    const = set(rng.sample(words, 2))
    eqs = []
    for j in range(m):
        size = rng.choice((3, 3, 4))
        eqs.append((f"e{j}:a1", tuple(rng.sample(words, size))))
    vars_ = sorted({v for _, vs in eqs for v in vs} - const)
    return eqs, const, vars_


def kmin_bf(eqs, const, vars_):
    for k in range(len(vars_) + 1):
        for S in itertools.combinations(vars_, k):
            known = set(const) | set(S)
            propagate(eqs, known, [])
            if len(known) == len(const) + len(vars_):
                return k
    return None


def solve(cnf_lines, name):
    fn = HERE + f"\\unit\\{name}.cnf"
    open(fn, "w").write(cnf_lines)
    r = subprocess.run(["wsl", "-d", "Ubuntu", "--", "bash", "-c", f"kissat -q {WSL_DIR}/{name}.cnf"],
                       capture_output=True, text=True, timeout=60)
    true = set()
    for line in r.stdout.split("\n"):
        if line.startswith("v "):
            true.update(int(x) for x in line[2:].split() if int(x) > 0)
    return r.returncode, true


def main():
    rng = random.Random(3)
    bad = 0
    lines = []
    for trial in range(25):
        n, m = rng.randint(8, 13), rng.randint(5, 11)
        sysm = rand_system(rng, n, m)
        gd_sat.build = lambda variant, length, s=sysm: s
        eqs, const, vars_ = sysm
        km = kmin_bf(eqs, const, vars_)
        T = len(vars_)
        res = []
        for k in (km - 1, km):
            if k < 0:
                res.append(("-", None))
                continue
            clauses, nv, g, vs = gd_sat.encode("x", "y", k, T)
            txt = f"p cnf {nv} {len(clauses)}\n" + "".join(" ".join(map(str, c)) + " 0\n" for c in clauses)
            rc, true = solve(txt, f"t{trial}_k{k}")
            guess = [v for v in vs if g[v] in true]
            cover = None
            if rc == 10:
                known = set(const) | set(guess)
                propagate(eqs, known, [])
                cover = len(known) == len(const) + len(vars_) and len(guess) <= k
            res.append((rc, cover))
        ok = (res[0][0] in ("-", 20)) and res[1][0] == 10 and res[1][1]
        bad += not ok
        lines.append(f"trial {trial}: n_vars={len(vars_)} eqs={len(eqs)} kmin(brute force)={km}  "
                     f"SAT k=kmin-1 -> {res[0][0]}  k=kmin -> {res[1][0]} decoded set covers: {res[1][1]}  {'OK' if ok else 'BAD'}")
    lines.append(f"failures: {bad} of 25")
    txt = "\n".join(lines)
    print(txt)
    open(HERE + "\\sat_unit.log", "w").write(txt + "\n")


if __name__ == "__main__":
    main()
