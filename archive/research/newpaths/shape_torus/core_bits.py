"""Bit-level seeds for the irreducible core ring (DM block) of the idea-1 system.

For an index set, take the largest DM block; find word-level tearing sets (greedy GD inside the block, many runs,
sizes t and t+1); start from all their bits and drop seed bits while propagation still determines the block.
Also report the G calls that the core touches and the satellite rings.
Usage: python core_bits.py <fixed|outhalf> <index words comma-separated> <tear runs> <min rounds>
"""
import os
import random
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from gd_order import build  # noqa: E402
from dm import dm_blocks  # noqa: E402
from bitgd import BitSystem  # noqa: E402


def tear_sets(eqs, words, beqs, rng, runs):
    bw = set(words)
    beq = [eqs[k][1] for k in beqs]
    found = {}
    for _ in range(runs):
        known, guesses = set(), []
        while True:
            changed = True
            while changed:
                changed = False
                for vs in beq:
                    u = [x for x in vs if x in bw and x not in known]
                    if len(u) == 1:
                        known.add(u[0])
                        changed = True
            if known >= bw:
                break
            cand = {}
            for vs in beq:
                u = [x for x in vs if x in bw and x not in known]
                if len(u) == 2:
                    for x in u:
                        cand[x] = cand.get(x, 0) + 1
            if not cand:
                cand = {x: 1 for x in bw - known}
            m = max(cand.values())
            pool = sorted(x for x, c in cand.items() if c >= m - rng.choice((0, 0, 1)))
            g = rng.choice(pool)
            known.add(g)
            guesses.append(g)
        found.setdefault(len(guesses), set()).add(tuple(sorted(guesses)))
    return found


def main():
    variant = sys.argv[1]
    index = sys.argv[2].split(",")
    truns = int(sys.argv[3])
    rounds = int(sys.argv[4])
    eqs, const, vars_ = build(variant, "len64")
    blocks = dm_blocks(eqs, const, vars_, index)
    rng = random.Random(11)
    lines = [f"{variant} index {index}"]
    core = max(blocks, key=lambda b: len(b[0]))
    for words, beqs in blocks:
        if len(words) > 1 and words is not core[0]:
            names = [eqs[k][0] for k in beqs]
            lines.append(f"  satellite ring: words {sorted(words)} eqs {sorted(names)}")
    words, beqs = core
    calls = {}
    for w_ in words:
        c = w_.split(".")[0]
        calls[c] = calls.get(c, 0) + 1
    lines.append(f"  core: {len(words)} words, {len(beqs)} equations; words per G call {dict(sorted(calls.items()))}")
    ts = tear_sets(eqs, words, beqs, rng, truns)
    tmin = min(ts)
    lines.append(f"  word-level tearing sizes found: { {k: len(v) for k, v in sorted(ts.items())} }")
    sub = [eqs[k] for k in beqs]
    bs = BitSystem(sub, set(words), 32)
    best = None
    tried = 0
    for t in sorted(ts)[:2]:
        for cut in sorted(ts[t])[:3]:
            tried += 1
            for order in ("random", "high"):
                mn = bs.minimize(list(cut), random.Random(tried), rounds=rounds, order=order)
                if best is None or len(mn) < best[0]:
                    best = (len(mn), cut, order)
                lines.append(f"    cut {list(cut)} ({32 * len(cut)} bits) order {order}: minimised seeds {len(mn)}"); print(lines[-1], flush=True)
    lines.append(f"  best bit-level seeds for the core: {best[0]} (word-level {32 * tmin})")
    txt = "\n".join(lines)
    print(txt)
    tag = "_".join(x.replace(".", "") for x in index)[:60]
    with open(os.path.join(HERE, f"core_bits_{variant}_{tag}.txt"), "w") as fh:
        fh.write(txt + "\n")


if __name__ == "__main__":
    main()
