"""General search: w = z & S (clean, 13 bits per lane); steps v_i = v_a ^ shift(v_b, d), a, b earlier values.
A value is w convolved with a set of offsets.  Find 3-step values with 8 clean read positions spanning T."""
import sys

SINGLES = [8, 9, 24, 25]
GEN = [[b] for b in SINGLES] + [[2, 26], [3, 27], [4, 16, 27], [5, 17, 30]]
S = sorted({b for g in GEN for b in g})
SB = sum(1 << b for b in S)


def span(gens):
    basis = []
    for g in gens:
        for b in basis:
            g = min(g, g ^ b)
        if g:
            basis.append(g)
    return basis


TB = span([sum(1 << b for b in g) for g in GEN])
TSET = set()
for m in range(1, 256):
    v = 0
    for i in range(8):
        if m >> i & 1:
            v ^= TB[i]
    TSET.add(v)

R = 108
OWN, FOR = {}, {}
for d in range(-R, R + 1):
    own = foreign = 0
    for p in range(32):
        q = p + d
        if 0 <= q <= 35:
            if SB >> q & 1:
                own |= 1 << (32 * p + q)
        elif SB >> (q % 36) & 1:
            lane = q // 36 + 3            # 0..6, 3 is the own lane
            foreign |= 1 << (256 * p + 36 * lane + q % 36)
    OWN[d], FOR[d] = own, foreign

M32 = (1 << 32) - 1
M256 = (1 << 256) - 1


def evaluate(poly):
    own = 0
    for d in poly:
        own ^= OWN[d]
    cand = []
    for p in range(32):
        v = own >> (32 * p) & M32
        if v in TSET:
            cand.append((p, v))
    if len(cand) < 8:
        return None
    foreign = 0
    for d in poly:
        foreign ^= FOR[d]
    good = [(p, v) for p, v in cand if not foreign >> (256 * p) & M256]
    if len(span([v for _, v in good])) == 8:
        return good
    return None


def shifted(poly, d):
    return frozenset(x + d for x in poly)


rng = [d for d in range(-35, 36) if d]
P0 = frozenset([0])
count = found = 0
seen = set()
out = open(sys.argv[1], "w")
for a in rng:
    P1 = P0 ^ shifted(P0, a)
    for i2 in range(2):
        for j2 in range(2):
            for b in rng:
                P2 = (P0, P1)[i2] ^ shifted((P0, P1)[j2], b)
                if not P2:
                    continue
                vals = (P0, P1, P2)
                for i3 in range(3):
                    for j3 in range(3):
                        if 2 not in (i3, j3):
                            continue
                        for c in rng:
                            P3 = vals[i3] ^ shifted(vals[j3], c)
                            count += 1
                            if P3 in seen or not P3:
                                continue
                            good = evaluate(P3)
                            if good:
                                seen.add(P3)
                                found += 1
                                out.write("%r %r %r | %r\n" % ((a,), (i2, j2, b), (i3, j3, c),
                                          [(p, [q for q in range(32) if v >> q & 1]) for p, v in good]))
print("candidates", count, "solutions", found)
