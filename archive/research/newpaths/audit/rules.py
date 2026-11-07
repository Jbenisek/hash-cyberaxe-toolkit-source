"""Audit step 3: table rules.
(a) gd_sat.table_macros rules ("orig") and a systematic generalisation ("gen"): for every unknown word z let
    A_z = plain closure of constants + {z}.  Every word of A_z is a function of z with family-constant parameters only,
    so a 2^32 table F_w: z -> w inverts it  -> rule  {w} -> z  (type W).
    Every equation e with >= 2 non-constant words in A_z and the rest outside is separable, sum(A-side) = g(outside),
    so a 2^32 table on the A-side solves it -> rule  (e minus A_z) -> z  (type E).
    Only rules not already implied by plain propagation are kept.
(b) numeric validation at w = 8 (toy rotations): for each rule and random messages, constants are the message's own
    family constants; enumerate all 256 values of the target, propagate plainly from constants + triggers + target and
    count the values consistent with every fully known equation.  Valid rule: the true value is always consistent.
    Distribution per target: vary the (first) trigger word over all 256 values and count solutions.
Usage: python rules.py [variant] [length]   (default: both variants, len64)
"""
import random
import sys
from collections import Counter

import numpy as np

sys.dont_write_bytecode = True
HERE = __file__.rsplit("\\", 1)[0]
sys.path.insert(0, HERE + "\\orig")
from gd_order import build  # noqa: E402
from gd_sat import table_macros  # noqa: E402
from ref import trace, rots  # noqa: E402


def nc_eqs(eqs, const):
    return [(n, tuple(v for v in vs if v not in const)) for n, vs in eqs]


def closure(ncq, known):
    known = set(known)
    ch = True
    while ch:
        ch = False
        for _, vs in ncq:
            u = [v for v in vs if v not in known]
            if len(u) == 1:
                known.add(u[0])
                ch = True
    return known


def gen_rules(eqs, const, vars_):
    ncq = nc_eqs(eqs, const)
    rules = []
    for z in vars_:
        A = closure(ncq, {z})
        for w in sorted(A - {z}):
            if z not in closure(ncq, {w}):
                rules.append(((w,), z, "W"))
        for n, vs in ncq:
            ina = [v for v in vs if v in A]
            out = tuple(v for v in vs if v not in A)
            if len(ina) >= 2 and out:
                if z not in closure(ncq, set(out)):
                    rules.append((out, z, "E:" + n))
    return rules


# ---------- numeric propagation at width w (vectorised over candidate arrays) ----------
def plan(eqs, const, start):
    """Plain propagation from const+start: ordered solve steps and the list of check equations."""
    known = set(const) | set(start)
    steps, used = [], set()
    ch = True
    while ch:
        ch = False
        for i, (n, vs) in enumerate(eqs):
            if i in used:
                continue
            u = [j for j, v in enumerate(vs) if v not in known]
            if len(u) == 1:
                steps.append((i, u[0]))
                used.add(i)
                known.add(vs[u[0]])
                ch = True
    checks = [i for i, (n, vs) in enumerate(eqs) if i not in used and all(v in known for v in vs)]
    return steps, checks, known


def rorv(z, r, w):
    m = (1 << w) - 1
    return ((z >> r) | (z << (w - r))) & m if r else z & m


def rolv(z, r, w):
    return rorv(z, (w - r) % w, w)


def solve(name, vs, j, V, out, w):
    m = (1 << w) - 1
    R = rots(w)
    x = [V.get(v) for v in vs]
    if name.startswith("out"):
        o = out[int(name[3:])]
        return (x[1 - j] ^ o) & m
    t = name.split(":")[1]
    if t in ("a1", "a2", "c1", "c2"):
        if j == 0:
            return sum(x[1:]) & m
        return (x[0] - sum(x[k] for k in range(1, len(x)) if k != j)) & m
    r = {"d1": R[0], "b1": R[1], "d2": R[2], "b2": R[3]}[t]
    if j == 0:
        return rorv(x[1] ^ x[2], r, w)
    return rolv(x[0], r, w) ^ x[3 - j]


def holds(name, vs, V, out, w):
    return V[vs[0]] == solve(name, vs, 0, V, out, w)


def validate(variant, length, rules, w=8, nmsg=40, seed=11):
    eqs, const, vars_ = build(variant, length)
    rng = random.Random(seed)
    res = []
    for trig, tgt, kind in rules:
        steps, checks, known = plan(eqs, const, set(trig) | {tgt})
        ok = True
        cnt_true = Counter()
        per_target = Counter()
        for _ in range(nmsg):
            msg = [rng.getrandbits(w) for _ in range(16)]
            if length == "len55":
                msg[14] = msg[15] = 0
            vals, Y, out = trace(msg, w, blen=(2 * w) & ((1 << w) - 1))
            cand = np.arange(1 << w, dtype=np.int64)
            # (1) true triggers, all target candidates
            V = {c: np.int64(vals[c]) for c in const}
            for t in trig:
                V[t] = np.full(1 << w, vals[t], dtype=np.int64)
            V[tgt] = cand
            for i, j in steps:
                n, vs = eqs[i]
                V[vs[j]] = solve(n, vs, j, V, out, w)
            good = np.ones(1 << w, dtype=bool)
            for i in checks:
                n, vs = eqs[i]
                good &= np.broadcast_to(holds(n, vs, V, out, w), good.shape)
            if not good[vals[tgt]]:
                ok = False
            cnt_true[int(good.sum())] += 1
            # (2) all values of the first trigger word x all target candidates
            T0 = np.repeat(np.arange(1 << w, dtype=np.int64), 1 << w)
            C0 = np.tile(np.arange(1 << w, dtype=np.int64), 1 << w)
            V = {c: np.int64(vals[c]) for c in const}
            for t in trig:
                V[t] = np.full(1 << (2 * w), vals[t], dtype=np.int64)
            V[trig[0]] = T0
            V[tgt] = C0
            for i, j in steps:
                n, vs = eqs[i]
                V[vs[j]] = solve(n, vs, j, V, out, w)
            good = np.ones(1 << (2 * w), dtype=bool)
            for i in checks:
                n, vs = eqs[i]
                good &= np.broadcast_to(holds(n, vs, V, out, w), good.shape)
            sols = good.reshape(1 << w, 1 << w).sum(axis=1)
            per_target.update(int(s) for s in sols)
        tot = sum(per_target.values())
        zero = per_target.get(0, 0) / tot
        mean = sum(k * v for k, v in per_target.items()) / tot
        res.append((trig, tgt, kind, ok, len(checks), zero, mean, dict(sorted(per_target.items())),
                    dict(sorted(cnt_true.items()))))
    return res


def main():
    variants = [sys.argv[1]] if len(sys.argv) > 1 else ["fixed", "outhalf"]
    length = sys.argv[2] if len(sys.argv) > 2 else "len64"
    lines = []
    for variant in variants:
        eqs, const, vars_ = build(variant, length)
        orig = [(tuple(t), g, "orig") for t, g in table_macros(eqs, const)]
        orig = [r for r in orig if r[1] not in r[0]]          # drop K0 self rule (x)->x
        ncq = nc_eqs(eqs, const)
        orig_eff = [r for r in orig if r[1] not in closure(ncq, set(r[0]))]
        gen = gen_rules(eqs, const, vars_)
        so = {(frozenset(t), g) for t, g, _ in orig_eff}
        sg = {(frozenset(t), g) for t, g, _ in gen}
        lines.append(f"== {variant} {length}: orig table_macros {len(orig)} rules ({len(orig_eff)} not implied by plain"
                     f" propagation); generalised single-z rules {len(gen)}")
        lines.append(f"   orig rules missing from gen: {sorted((sorted(t), g) for t, g in so - sg)}")
        newr = [r for r in gen if (frozenset(r[0]), r[1]) not in so]
        lines.append(f"   gen rules not in orig ({len(newr)}):")
        for t, g, k in newr:
            lines.append(f"      {list(t)} -> {g}   [{k}]")
        lines.append(f"   validation at w=8 (40 random messages each; per-target = solutions for each value of the"
                     f" first trigger word):")
        for trig, tgt, kind, ok, nchk, zero, mean, pt, ct in validate(variant, length, orig_eff + newr):
            lines.append(f"      {'VALID' if ok else 'INVALID'} {list(trig)} -> {tgt} [{kind}] checks={nchk}"
                         f" P(0 sol)={zero:.3f} mean={mean:.3f} sols/target={pt} sols-at-true-instance={ct}")
    txt = "\n".join(lines)
    print(txt)
    open(HERE + f"\\rules_{length}.log", "w").write(txt + "\n")


if __name__ == "__main__":
    main()
