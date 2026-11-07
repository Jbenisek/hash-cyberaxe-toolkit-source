"""Bit-level pruning of word-level solving orders (main session, Pivot, 2026-10-08).

Start from a word-level covering guess set (8 words = 256 bits for the fixed variant), then try to drop guessed bits one
at a time: a bit may be dropped when propagation from the remaining guesses still determines every bit.  Repeated with
random drop orders and several starting orders.  checks (bits) = guessed bits left - 128.
Usage: python bit_prune.py <variant> <restarts> [seed]
"""
import random
import sys

from bit_gd import build_bits, W
from gd_order import build, run as word_run


def make_closure(m):
    n = len(m.names)
    occ_x = [[] for _ in range(n)]
    for e, vs in enumerate(m.xor_eqs):
        for v in vs:
            occ_x[v].append(e)
    occ_m = [[] for _ in range(n)]
    for e, (out, ins) in enumerate(m.maj_eqs):
        for v in ins:
            occ_m[v].append(e)
    base_known = bytearray(n)
    for c in m.const:
        base_known[c] = 1

    def closure(guess):
        known = bytearray(base_known)
        unk_x = [0] * len(m.xor_eqs)
        unk_m = [0] * len(m.maj_eqs)
        queue = []
        for g in guess:
            known[g] = 1
        for e, vs in enumerate(m.xor_eqs):
            unk_x[e] = sum(1 for v in vs if not known[v])
        for e, (out, ins) in enumerate(m.maj_eqs):
            unk_m[e] = sum(1 for v in ins if not known[v])

        def learn(v):
            if not known[v]:
                known[v] = 1
                queue.append(v)

        for e, vs in enumerate(m.xor_eqs):
            if unk_x[e] == 1:
                for u in vs:
                    if not known[u]:
                        learn(u)
        for e, (out, ins) in enumerate(m.maj_eqs):
            if unk_m[e] == 0:
                learn(out)
        while queue:
            v = queue.pop()
            for e in occ_x[v]:
                unk_x[e] -= 1
                if unk_x[e] == 1:
                    for u in m.xor_eqs[e]:
                        if not known[u]:
                            learn(u)
                            break
            for e in occ_m[v]:
                unk_m[e] -= 1
                if unk_m[e] == 0:
                    learn(m.maj_eqs[e][0])
        return sum(known)

    return closure, n


def main():
    variant = sys.argv[1] if len(sys.argv) > 1 else "fixed"
    restarts = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    m, freedom = build_bits(variant)
    closure, n = make_closure(m)
    eqs, const, vars_ = build(variant, "len64")
    rng = random.Random(seed)
    best = None
    for r in range(restarts):
        words = word_run(eqs, const, vars_, rng)[0]
        # keep only word orders of minimum size
        while len(words) > 8 + (0 if variant == "fixed" else 99):
            words = word_run(eqs, const, vars_, rng)[0]
        guess = [m.vid[f"{w}#{i}"] for w in words for i in range(W)]
        assert closure(guess) == n, "word order does not cover the bit model"
        order = list(guess)
        rng.shuffle(order)
        kept = set(guess)
        for g in order:
            kept.discard(g)
            if closure(kept) < n:
                kept.add(g)
        left = len(kept)
        line = f"restart {r}: start {words} -> {left} guessed bits, checks {left - freedom} bits"
        print(line, flush=True)
        if best is None or left < best[0]:
            best = (left, words, sorted(m.names[g] for g in kept))
    with open(f"bit_prune_{variant}.txt", "w") as fh:
        fh.write(f"best: {best[0]} guessed bits, checks {best[0] - freedom} bits\nstart words: {best[1]}\n")
        fh.write("kept bits: " + " ".join(best[2]) + "\n")
    print(f"BEST {variant}: {best[0]} guessed bits -> checks {best[0] - freedom} bits (word level 128)")


if __name__ == "__main__":
    main()
