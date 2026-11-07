"""w = z & S, then four xorshift steps v ^= shift(v, d) (register friendly).  Also three xorshift steps where the
early mask is any superset choice is pointless; here only S.  Prints solutions."""
import itertools, sys

GEN = [[8], [9], [24], [25], [2, 26], [3, 27], [4, 16, 27], [5, 17, 30]]
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
R = 141
OWN, FOR = {}, {}
for d in range(-R, R + 1):
    own = foreign = 0
    for p in range(32):
        q = p + d
        if 0 <= q <= 35:
            if SB >> q & 1:
                own |= 1 << (32 * p + q)
        elif SB >> (q % 36) & 1:
            lane = q // 36 + 4
            foreign |= 1 << (360 * p + 36 * lane + q % 36)
    OWN[d], FOR[d] = own, foreign
M32, MF = (1 << 32) - 1, (1 << 360) - 1
n = int(sys.argv[1])
rng = [d for d in range(-35, 36) if d]
found = 0
out = open(sys.argv[2], "w")
for ds in itertools.combinations_with_replacement(rng, n):
    sums = {0: 1}
    for d in ds:
        new = dict(sums)
        for s, odd in sums.items():
            new[s + d] = new.get(s + d, 0) ^ odd
        sums = new
    own = 0
    deltas = [s for s, odd in sums.items() if odd]
    for d in deltas:
        own ^= OWN[d]
    cand = []
    for p in range(32):
        v = own >> (32 * p) & M32
        if v in TSET:
            cand.append((p, v))
    if len(cand) < 8:
        continue
    foreign = 0
    for d in deltas:
        foreign ^= FOR[d]
    good = [(p, v) for p, v in cand if not foreign >> (360 * p) & MF]
    if len(span([v for _, v in good])) == 8:
        found += 1
        out.write("%r | %r\n" % (ds, [(p, [q for q in range(32) if v >> q & 1]) for p, v in good]))
print("steps", n, "solutions", found)
