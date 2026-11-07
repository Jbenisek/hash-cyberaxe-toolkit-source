"""Guess-and-determine model for variants of the 2-round BLAKE3 family question (base: ../gd_order.py).

Word-level model: every G call is 8 primitive equations, each solvable for any one of its words.
Options
  half    02 : family holds E0,E2 side (out0,2,5,7)     13 : E1,E3 side (out1,3,4,6)
  mode    fixed   : all 12 input words of the two E calls are constants
          outhalf : the two E calls are modelled; only their 4 output words (out_i = v_i ^ v_{i+8}) are held
          partial : only the input words listed in `held` are constants (the rest of the 12 are free)
  length  64 or 55 (55: m14, m15 constant zero; m13's zero top byte is NOT modelled, treated as free)
  cvvar   chaining value words init0..init7 are unknowns (two-block, CV varying inside the family)
"""
import itertools
import random

PERM = [2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8]
COLS = [(0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15)]
DIAG = [(0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14)]
HALF = {"02": (0, 2), "13": (1, 3)}
OUTW = {"02": (0, 2, 5, 7), "13": (1, 3, 4, 6)}


def e_inputs(half):
    """Names (Y<i> / m<i>) of the 12 input words of the two E calls of this half."""
    s1 = [f"m{PERM[i]}" for i in range(16)]
    out = []
    for j in HALF[half]:
        out += [f"Y{i}" for i in DIAG[j]] + [s1[8 + 2 * j], s1[9 + 2 * j]]
    return out


def build(half="02", mode="fixed", length=64, held=None, cvvar=False):
    eqs = []
    const = set()
    state = [f"init{i}" for i in range(16)]
    const.update(state[8:] if cvvar else state)
    msg = [f"m{i}" for i in range(16)]
    if length == 55:
        const.update(["m14", "m15"])
    order = list(range(16))
    ystate = None

    def G(name, idx, x, y):
        a, b, c, d = (state[i] for i in idx)
        a1, d1, c1, b1, a2, d2, c2, b2 = (f"{name}.{t}" for t in ("a1", "d1", "c1", "b1", "a2", "d2", "c2", "b2"))
        eqs.extend([
            (f"{name}:a1", (a1, a, b, x)), (f"{name}:d1", (d1, d, a1)), (f"{name}:c1", (c1, c, d1)),
            (f"{name}:b1", (b1, b, c1)), (f"{name}:a2", (a2, a1, b1, y)), (f"{name}:d2", (d2, d1, a2)),
            (f"{name}:c2", (c2, c1, d2)), (f"{name}:b2", (b2, b1, c2)),
        ])
        for i, v in zip(idx, (a2, b2, c2, d2)):
            state[i] = v

    for r, pref in ((0, ("K", "D")), (1, ("C", "E"))):
        s = [msg[order[i]] for i in range(16)]
        for j, idx in enumerate(COLS):
            G(f"{pref[0]}{j}", idx, s[2 * j], s[2 * j + 1])
        if r == 1:
            ystate = list(state)
        for j, idx in enumerate(DIAG):
            if r == 1 and (mode != "outhalf" or j not in HALF[half]):
                continue
            G(f"{pref[1]}{j}", idx, s[8 + 2 * j], s[9 + 2 * j])
        order = [order[p] for p in PERM]

    def resolve(name):
        return ystate[int(name[1:])] if name[0] == "Y" else name

    if mode == "fixed":
        held = e_inputs(half)
    if mode in ("fixed", "partial"):
        const.update(resolve(h) for h in held)
    else:
        for i in OUTW[half]:
            eqs.append((f"out{i}", (state[i], state[i + 8])))
    vars_ = sorted({v for _, vs in eqs for v in vs} - const)
    return eqs, const, vars_


def closure(eqs, known, macros=()):
    known = set(known)
    changed = True
    while changed:
        changed = False
        for _, vs in eqs:
            unk = [v for v in vs if v not in known]
            if len(unk) == 1:
                known.add(unk[0])
                changed = True
        for trig, tgt in macros:
            if tgt not in known and all(t in known for t in trig):
                known.add(tgt)
                changed = True
    return known


def _matching(eqsub, unknown):
    """Perfect matching equations -> distinct unknown words (structural determination)."""
    unknown = list(unknown)
    match = {}

    def aug(i, seen):
        for w in eqsub[i]:
            if w in unknown and w not in seen:
                seen.add(w)
                if w not in match or aug(match[w], seen):
                    match[w] = i
                    return True
        return False

    return all(aug(i, set()) for i in range(len(eqsub)))


def table_macros(eqs, const, dmax=1):
    """Sub-systems inside one G call whose non-constant words exceed their equations by d <= dmax:
    any d structurally independent known words give every other word by a 2^(32d) table built in preprocessing
    (all parameters are family constants).  Returns (trigger tuple, target) pairs not already given by propagation."""
    calls = {}
    for name, vs in eqs:
        if ":" in name:
            calls.setdefault(name.split(":")[0], []).append(vs)
    out = set()
    for call, elist in calls.items():
        for r in range(1, len(elist) + 1):
            for sub in itertools.combinations(elist, r):
                W = sorted({v for vs in sub for v in vs} - const)
                d = len(W) - len(sub)
                if not 1 <= d <= dmax:
                    continue
                for S in itertools.combinations(W, d):
                    rest = [w for w in W if w not in S]
                    eqsub = [[w for w in vs if w in rest] for vs in sub]
                    if not _matching(eqsub, rest):
                        continue
                    cl = closure([(None, vs) for vs in sub], set(S) | const)
                    for w in rest:
                        if w not in cl:
                            out.add((tuple(S), w))
    # drop macros whose trigger is a superset of another macro's trigger for the same target
    res = sorted(out)
    keep = [m for m in res if not any(o[1] == m[1] and set(o[0]) < set(m[0]) for o in res)]
    return keep


def greedy(eqs, const, vars_, runs=2000, seed=1, macros=()):
    rng = random.Random(seed)
    best = None
    hist = {}
    for _ in range(runs):
        known = closure(eqs, const, macros)
        guesses = []
        while len(known) < len(const) + len(vars_):
            cand = {}
            for _, vs in eqs:
                unk = [v for v in vs if v not in known]
                if len(unk) == 2:
                    for v in unk:
                        cand[v] = cand.get(v, 0) + 1
            for trig, tgt in macros:
                unk = [v for v in trig if v not in known]
                if tgt not in known and len(unk) == 1:
                    cand[unk[0]] = cand.get(unk[0], 0) + 1
            if not cand:
                cand = {v: 1 for v in vars_ if v not in known}
            top = max(cand.values())
            pool = [v for v, c in cand.items() if c >= top - rng.choice((0, 0, 1))]
            g = rng.choice(pool)
            guesses.append(g)
            known = closure(eqs, known | {g}, macros)
        hist[len(guesses)] = hist.get(len(guesses), 0) + 1
        if best is None or len(guesses) < len(best):
            best = guesses
    return best, dict(sorted(hist.items()))
