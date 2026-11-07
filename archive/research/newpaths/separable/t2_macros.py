"""Generalised table rules with tables of up to 2^64 entries (preprocessing <= 2^64, allowed by the cost model).

For every G call and every subset Q of its 8 primitive equations: W = non-constant words of Q.
For every P subset of W with |P| <= 2: U = W - P.  Rule P -> U is valid when
  (1) |U| = |Q| and there is a perfect matching equations(Q) <-> U (each equation solved for a distinct word of it)
      [structural rank; a word pair that occurs only through one sum, like (a, x), fails here],
  (2) the solution set of Q (dimension delta = |W| - |Q| = |P|) can be enumerated by plain propagation inside Q
      from some delta words (so the table costs 2^(32 delta) <= 2^64 to build).
Per G call and P the targets of all valid Q are united; targets already reached by plain propagation from P
(inside the G call) are dropped.  Output: the system file of export_sys.py with these macros
(one line per target word).
Usage: python t2_macros.py <fixed|outhalf> <out>
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
import sys

sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/newpaths'))
from gd_order import build          # noqa: E402


def plain_closure(eqs, known):
    known = set(known)
    ch = True
    while ch:
        ch = False
        for ws in eqs:
            unk = [w for w in ws if w not in known]
            if len(unk) == 1:
                known.add(unk[0])
                ch = True
    return known


def perfect_matching(eqs, U):
    """eqs: list of word lists (non-constant words). U: set of unknown words.  Kuhn's algorithm."""
    U = list(U)
    match = {}

    def try_eq(i, seen):
        for w in eqs[i]:
            if w in U and w not in seen:
                seen.add(w)
                if w not in match or try_eq(match[w], seen):
                    match[w] = i
                    return True
        return False

    for i in range(len(eqs)):
        if not try_eq(i, set()):
            return False
    return len(match) == len(eqs)


def main():
    variant, out = sys.argv[1], sys.argv[2]
    eqs, const, vars_ = build(variant, "len64")
    idx = {v: i for i, v in enumerate(vars_)}
    calls = {}
    E = []
    for name, vs in eqs:
        ws = [v for v in vs if v not in const]
        E.append((name, ws))
        if ":" in name:
            calls.setdefault(name.split(":")[0], []).append(ws)
    macros = {}
    for call, ceqs in calls.items():
        Wall = sorted({w for ws in ceqs for w in ws})
        for r in range(1, len(ceqs) + 1):
            for Q in itertools.combinations(range(len(ceqs)), r):
                qe = [ceqs[i] for i in Q]
                W = sorted({w for ws in qe for w in ws})
                d = len(W) - len(qe)
                if d < 0 or d > 2:
                    continue
                # (2) enumerable from d words by plain propagation inside Q
                ok = False
                for B in itertools.combinations(W, d):
                    if plain_closure(qe, B) >= set(W):
                        ok = True
                        break
                if not ok:
                    continue
                for P in itertools.combinations(W, d):
                    U = set(W) - set(P)
                    if not perfect_matching(qe, U):
                        continue
                    key = (call, tuple(sorted(P)))
                    macros.setdefault(key, set()).update(U)
    lines = []
    nnew = 0
    for (call, P), U in sorted(macros.items()):
        ceqs = calls[call]
        reach = plain_closure(ceqs, P)
        new = sorted(U - reach)
        if not new or len(P) == 0:
            continue
        nnew += 1
        for t in new:
            lines.append((P, t))
    F = len(vars_) - len(eqs)
    with open(out, "w") as fh:
        fh.write(f"{len(vars_)} {len(E)} {len(lines)} {F}\n")
        for v in vars_:
            fh.write(v + "\n")
        for name, ws in E:
            fh.write(f"{name} {len(ws)} " + " ".join(str(idx[w]) for w in ws) + "\n")
        for P, t in lines:
            fh.write(f"{len(P)} " + " ".join(str(idx[w]) for w in P) + f" {idx[t]}\n")
    print(variant, "trigger sets with new targets:", nnew, "macro lines:", len(lines))
    by = {}
    for (call, P), U in sorted(macros.items()):
        reach = plain_closure(calls[call], P)
        if U - reach and P:
            by.setdefault(call, []).append((P, sorted(U - reach)))
    for call in by:
        print(call, len(by[call]), "e.g.", by[call][:2])


if __name__ == "__main__":
    main()
