"""Solutions-per-target distribution of every effective gd_sat table rule at w = 8, 12, 16, 20 (toy rotations).
For rule (t0, rest) -> z: propagate plainly from constants + rest + {z}; t0 is then a function F(z) (checked).
Evaluate F on all 2^w values of z (constants and 'rest' from a random message), bincount over the 2^w values of t0:
P(0) = fraction of targets with no solution, max = largest preimage, and E_inst = mean solutions seen from a true
instance (size-biased, = sum n^2 / 2^w).  Several random messages per width.
"""
import random
import sys

import numpy as np

sys.dont_write_bytecode = True
HERE = __file__.rsplit("\\", 1)[0]
sys.path.insert(0, HERE + "\\orig")
from gd_order import build  # noqa: E402
from gd_sat import table_macros  # noqa: E402
from rules import plan, solve, nc_eqs, closure  # noqa: E402
from ref import trace  # noqa: E402


def main():
    lines = []
    for variant in ("fixed", "outhalf"):
        eqs, const, vars_ = build(variant, "len64")
        ncq = nc_eqs(eqs, const)
        rules = [(tuple(u for u in t if u not in const), g) for t, g in table_macros(eqs, const) if g not in t]
        rules = [r for r in rules if r[1] not in closure(ncq, set(r[0]))]
        lines.append(f"== {variant}: {len(rules)} effective table rules")
        for trig, tgt in rules:
            # put the trigger that is a function of z first (the one derived from rest + z)
            for i in range(len(trig)):
                t0, rest = trig[i], trig[:i] + trig[i + 1:]
                steps, checks, known = plan(eqs, const, set(rest) | {tgt})
                if t0 in known:
                    break
            row = []
            for w in (8, 12, 16, 20):
                rng = random.Random(w)
                p0s, mx, einst = [], 0, []
                for _ in range(4):
                    msg = [rng.getrandbits(w) for _ in range(16)]
                    vals, Y, out = trace(msg, w, blen=(2 * w) & ((1 << w) - 1))
                    V = {c: np.int64(vals[c]) for c in const}
                    for t in rest:
                        V[t] = np.int64(vals[t])
                    V[tgt] = np.arange(1 << w, dtype=np.int64)
                    for i, j in steps:
                        n, vs = eqs[i]
                        V[vs[j]] = solve(n, vs, j, V, out, w)
                    cnt = np.bincount(np.asarray(V[t0], dtype=np.int64), minlength=1 << w)
                    p0s.append(float((cnt == 0).mean()))
                    mx = max(mx, int(cnt.max()))
                    einst.append(float((cnt.astype(np.float64) ** 2).sum() / (1 << w)))
                row.append(f"w={w}: P(0)={np.mean(p0s):.3f} max={mx} E_inst={np.mean(einst):.2f}")
            lines.append(f"   {list(rest) + [t0]} -> {tgt}:  " + "; ".join(row))
    txt = "\n".join(lines)
    print(txt)
    open(HERE + "\\rules_dist.log", "w").write(txt + "\n")


if __name__ == "__main__":
    main()
