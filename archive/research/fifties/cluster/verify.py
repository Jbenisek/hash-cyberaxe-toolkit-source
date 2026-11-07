#!/usr/bin/env python3
"""Cross-check the GPU kernel against outer.scalar_outer on the SAME RNG stream.
Replicates splitmix64 + cluster construction in Python, computes omega with the
authoritative scalar step CO, and counts exceptions / dead-rep partner passes."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "impl")))
import outer

M64 = (1 << 64) - 1
S = outer.Search()


def splitmix(st):
    st = (st + 0x9E3779B97F4A7C15) & M64
    z = st
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & M64
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & M64
    return st, (z ^ (z >> 31)) & M64


def words8(seed, c):
    st = (seed * 0x9E3779B97F4A7C15) & M64
    st ^= (c * 0xD1B54A32D192ED03 + 0x632BE59BD9B4E019) & M64
    w = []
    for _ in range(4):
        st, r = splitmix(st)
        w.append(r & 0xffffffff)
        w.append((r >> 32) & 0xffffffff)
    return w


def omega_for(ctx, e1):
    W = e1 & outer.FREE_MASK           # W whose free bits reproduce e1
    eight = list(ctx) + [W]
    v = outer.scalar_outer(eight)
    assert v["e1"] == e1, ("%08x" % v["e1"], "%08x" % e1)
    return v["omega"]


def main(seed, total):
    pairs = exc = dead = dp = dpn = 0
    for c in range(total):
        w = words8(seed, c)
        ctx = w[:7]; W = w[7]
        base_e1 = outer.CLASS_VALUE | (W & outer.FREE_MASK)
        rep_e1 = base_e1 & ~(0x1F << 10)
        om_rep = omega_for(ctx, rep_e1)
        rep_low9 = om_rep & 0x1ff
        rep_dead = alive9[rep_low9] == 0
        for p in range(1, 32):
            e1p = rep_e1 | (p << 10)
            om = omega_for(ctx, e1p)
            pairs += 1
            is_exc = (om & 0x1ff) != rep_low9
            if is_exc:
                exc += 1
            if rep_dead:
                m2 = outer.look(S.t2, om)
                if m2:
                    dp += 1
                    if not is_exc:
                        dpn += 1
        if rep_dead:
            dead += 1
    print(json.dumps({"seed": seed, "clusters": total, "partner_pairs": pairs,
                      "exceptions": exc, "dead_clusters": dead,
                      "dead_partner_pass2": dp, "dead_partner_pass2_nonexc": dpn}))


if __name__ == "__main__":
    import json as _j
    with open(os.path.join(HERE, "prep.json")) as f:
        alive9_count = _j.load(f)["alive9_count"]
    # rebuild alive9 exactly as prep did
    from fractions import Fraction
    import importlib.util
    spec = importlib.util.spec_from_file_location("prep", os.path.join(HERE, "prep.py"))
    # reuse prep's automaton to get alive9
    th = [outer.ctr_g(t) for t in outer.TAUS]
    targets2 = [(outer.ror(x, 12), outer.EPS) for x in th]
    # inline the bit automaton (same as prep)
    def ctr_bits(targets, dy, n=32):
        layer = [(0, (1,) * len(targets))]; layers = [layer]; trans = []
        for i in range(n):
            ids, rows, e = {}, [], dy >> i & 1
            for k, sets in layer:
                row = []
                for a in (0, 1):
                    b, new = a ^ e ^ k, []
                    for m, (dz, out) in zip(sets, targets):
                        d, r = dz >> i & 1, 0
                        for cc in range(4):
                            if m >> cc & 1 and (cc >> 1) ^ (cc & 1) == (out >> i & 1) ^ a ^ b ^ d:
                                for vv in (0, 1):
                                    r |= 1 << ((a + vv + (cc >> 1)) >> 1) * 2 + ((b + (vv ^ d) + (cc & 1)) >> 1)
                        new.append(r)
                    state = ((a + e + k) >> 1, tuple(new)) if any(new) else (0, (0,) * len(new))
                    row.append(ids.setdefault(state, len(ids)))
                rows.append(row)
            trans.append(rows); layer = list(ids); layers.append(layer)
        return trans, layers
    trans, layers = ctr_bits(targets2, outer.DY3, 32)
    S_IDX = [j for j in range(7) if (outer.S_MASK >> j) & 1]
    alive9 = [0] * 512
    for v in range(512):
        idx = 0
        for i in range(9):
            idx = trans[i][idx][(v >> i) & 1]
        alive9[v] = 1 if any(layers[9][idx][1][t] for t in S_IDX) else 0
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 12345
    total = int(sys.argv[2]) if len(sys.argv) > 2 else 20000
    main(seed, total)
