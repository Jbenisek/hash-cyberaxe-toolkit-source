"""Catalogue of the small rings (DM blocks other than the core) of the idea-1 system, with bit-level seed cost.

For many index sets: DM blocks; every block of >= 2 words that is not the largest one is a satellite ring.
Distinct rings (by equation set) are listed with: words, word-level cuts, side words (known words feeding it),
bit-level seeds s (bitgd), and whether every side word is a family constant (then it is solved once, offline).
Usage: python ring_list.py <fixed|outhalf> <n random index sets> <seed>
"""
import os
import random
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from gd_order import build  # noqa: E402
from dm import dm_blocks, tearing  # noqa: E402
from bitgd import BitSystem  # noqa: E402


def main():
    variant, n, seed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    eqs, const, vars_ = build(variant, "len64")
    F = len(vars_) - len(eqs)
    rng = random.Random(seed)
    rings = {}
    cores = []
    msgs = sorted(v for v in vars_ if v.startswith("m"))
    for t in range(n):
        if t % 2 == 0 and len(msgs) >= F:
            idx = tuple(rng.sample(msgs, F))
        else:
            idx = tuple(rng.sample(sorted(vars_), F))
        bl = dm_blocks(eqs, const, vars_, idx)
        if bl is None:
            continue
        big = max(bl, key=lambda b: len(b[0]))
        cores.append(len(big[0]))
        for words, beqs in bl:
            if len(words) < 2 or words is big[0]:
                continue
            key = frozenset(eqs[k][0] for k in beqs)
            if key not in rings:
                rings[key] = (sorted(words), sorted(beqs), idx)
    lines = [f"{variant}: {n} index sets; core size min {min(cores)} max {max(cores)}; distinct satellite rings {len(rings)}"]
    for key, (words, beqs, idx) in sorted(rings.items(), key=lambda kv: (len(kv[1][0]), sorted(kv[0]))):
        t = tearing(eqs, words, beqs, None, rng, 60)
        side = sorted({x for k in beqs for x in eqs[k][1] if x not in words})
        allconst = all(x in const for x in side)
        sub = [eqs[k] for k in beqs]
        bs = BitSystem(sub, set(words), 32)
        mw = bs.solve_multiwindow(random.Random(3), tries=150)
        s = mw[0] if mw else 32 * len(t)
        lines.append(f"  ring {len(words)} words, cuts {len(t)} {t}, bit seeds s={s}; eqs {sorted(key)}; "
                     f"side {side}{' (all constants)' if allconst else ''}")
    txt = "\n".join(lines)
    print(txt)
    with open(os.path.join(HERE, f"rings_{variant}.txt"), "w") as fh:
        fh.write(txt + "\n")


if __name__ == "__main__":
    main()
