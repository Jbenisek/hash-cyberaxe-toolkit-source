"""Live gate count of the r4 MDFA step for a chosen constant prefix m0..m7 (inputs at m8..m15).
override: dict word-index -> value forced after the round-1 column step (upper-bound probe only)."""
import sys
sys.path.insert(0, sys.argv[1] if len(sys.argv) > 1 else "."); sys.setrecursionlimit(100000)
import bsrho_mdfa as m


def gates(key=(0,) * 8, override=None):
    g = m.Gen(256)
    def s3(A, B, C):
        if all(p[0] != 0 for W in (A, B, C) for p in W):
            return g.add3(A, B, C)
        return g.add(g.add(A, B), C)
    mm = [m._constw(k) for k in key] + [[g.inputs[32 * i + b] for b in range(32)] for i in range(8)]
    v = [m._constw(w) for w in m.IV] + [m._constw(w) for w in m.IV[:4]] + [m._constw(0), m._constw(0), m._constw(64), m._constw(m.FLAGS)]
    for r in range(m.ROUNDS):
        for j, (a, b, c, d) in enumerate(m.GCALLS):
            if r == 0 and j == 4 and override:
                for i, val in override.items():
                    v[i] = m._constw(val)
            x, y = mm[2 * j], mm[2 * j + 1]
            v[a] = s3(v[a], v[b], x); v[d] = m._ror_planes(g.xorw(v[d], v[a]), 16)
            v[c] = g.add(v[c], v[d]); v[b] = m._ror_planes(g.xorw(v[b], v[c]), 12)
            v[a] = s3(v[a], v[b], y); v[d] = m._ror_planes(g.xorw(v[d], v[a]), 8)
            v[c] = g.add(v[c], v[d]); v[b] = m._ror_planes(g.xorw(v[b], v[c]), 7)
        mm = [mm[i] for i in m.PERM]
    out = [s for i in range(8) for s in g.xorw(v[i], v[i + 8])]
    seen = set(o[0] for o in out)
    for k in range(len(g.nodes) - 1, 0, -1):
        if k in seen and g.nodes[k][0] in "xao":
            seen.add(g.nodes[k][1]); seen.add(g.nodes[k][2])
    return sum(1 for k in seen if g.nodes[k][0] in "xao"), all(o[0] != 0 for o in out)


def colstate(key):
    """Scalar state after the round-1 column step for prefix key."""
    v = list(m.IV) + list(m.IV[:4]) + [0, 0, 64, m.FLAGS]
    M = 0xFFFFFFFF
    for j, (a, b, c, d) in enumerate(m.GCALLS[:4]):
        x, y = key[2 * j], key[2 * j + 1]
        v[a] = (v[a] + v[b] + x) & M; v[d] = m._ror(v[d] ^ v[a], 16)
        v[c] = (v[c] + v[d]) & M; v[b] = m._ror(v[b] ^ v[c], 12)
        v[a] = (v[a] + v[b] + y) & M; v[d] = m._ror(v[d] ^ v[a], 8)
        v[c] = (v[c] + v[d]) & M; v[b] = m._ror(v[b] ^ v[c], 7)
    return v


if __name__ == "__main__":
    M = 0xFFFFFFFF
    print("key0", gates())
    v = colstate((0,) * 8)
    # ideal: all four c-words 0 and all four diagonal a+b sums 0 (b kept, a = -b)
    ov = {8: 0, 9: 0, 10: 0, 11: 0, 0: (-v[5]) & M, 1: (-v[6]) & M, 2: (-v[7]) & M, 3: (-v[4]) & M}
    print("ideal8", gates(override=ov))
    ov7 = dict(ov); del ov7[1]
    print("ideal7 (a1+b2 left)", gates(override=ov7))
    print("c-only4", gates(override={8: 0, 9: 0, 10: 0, 11: 0}))
