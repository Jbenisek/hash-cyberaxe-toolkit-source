"""Sphere / nested (fractal) families in the word-level guess-and-determine model of ../gd_order.py.

Sphere: instead of holding the whole half-digest (out0,2,5,7) constant, hold only a subset S of its 4 words
(outhalf variant with |S| output equations), or hold only some of the 12 E0/E2 input words (fixed variant with
r words released).  The half-digest then spreads over 2^h values, h = 32*(4-|S|) resp. h <= 32*r, and the
birthday needs 2^((128+h)/2) members.  Nested: the levels |S| = 1,2,3,4 are families inside families.
checks = min guesses - freedom (greedy upper bound; with or without the table macros of ../gd_promote.py).
Projected exponent (log2 units, before word-op discounts) = (128 + h)/2 + 32 * checks.
Usage: python gd_sphere.py outhalf <runs> | python gd_sphere.py fixed <runs> <rmax>
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
import random
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/newpaths'))
from gd_order import build  # noqa: E402  (read only)
from gd_promote import macros_for, solve  # noqa: E402  (read only)


def best_checks(eqs, const, runs, tables, seed=3):
    vars_ = sorted({v for _, vs in eqs for v in vs} - const)
    freedom = len(vars_) - len(eqs)
    mac = macros_for(eqs, const) if tables else []
    rng = random.Random(seed)
    best = None
    for _ in range(runs):
        g = solve(eqs, mac, set(const), rng)
        if best is None or len(g) < len(best):
            best = g
    return len(best) - freedom, freedom, best


def run_outhalf(runs):
    eqs, const, _ = build("outhalf", "len64")
    outs = ["out0", "out2", "out5", "out7"]
    print(f"# outhalf sphere/nested, greedy runs={runs}")
    for k in range(1, 5):
        for S in itertools.combinations(outs, k):
            e2 = [e for e in eqs if not (e[0].startswith("out") and e[0] not in S)]
            # drop E-calls whose outputs no longer matter? keep them: they are defined by the other words
            h = 32 * (4 - k)
            for tables in (False, True):
                c, f, g = best_checks(e2, const, runs, tables)
                expo = (128 + h) / 2 + 32 * max(c, 0)
                print(f"held={','.join(S):20s} k={k} h={h:3d} tables={int(tables)} freedom={f:2d} "
                      f"checks={c} exponent~{expo:.0f}  guesses={g}", flush=True)


def run_fixed(runs, rmax):
    eqs, const, _ = build("fixed", "len64")
    held = sorted(w for w in const if not w.startswith("init"))
    print(f"# fixed sphere: release r of the {len(held)} held words, greedy runs={runs}")
    for r in range(1, rmax + 1):
        hist = {}
        bestrow = None
        for rel in itertools.combinations(held, r):
            c2 = set(const) - set(rel)
            for tables in (False, True):
                c, f, g = best_checks(eqs, c2, runs, tables)
                hist[(tables, c)] = hist.get((tables, c), 0) + 1
                expo = (128 + min(128, 32 * r)) / 2 + 32 * max(c, 0)
                if bestrow is None or expo < bestrow[0]:
                    bestrow = (expo, rel, tables, c, f, g)
        print(f"r={r}: (tables,checks)->count {dict(sorted(hist.items()))}; best exponent~{bestrow[0]:.0f} "
              f"released={bestrow[1]} tables={int(bestrow[2])} checks={bestrow[3]} freedom={bestrow[4]}", flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "outhalf":
        run_outhalf(int(sys.argv[2]))
    else:
        run_fixed(int(sys.argv[2]), int(sys.argv[3]))
