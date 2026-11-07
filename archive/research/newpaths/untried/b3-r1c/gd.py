"""b3-r1c scout: word-level guess-and-determine (GD) search on the 2-round pair system.

Each G call is 8 word relations (a1=a+b+x, d1=ror(d^a1,16), c1=c+d1, b1=ror(b^c1,12),
a2=a1+b1+y, d2=ror(d1^a2,8), c2=c1+d2, b2=ror(b1^c2,7)); any single unknown word in a
relation is determined by the others.  A relation whose words all become known without
being used is a check (a 32-bit filter).  Dimension = guesses - checks (in words).  The
cost of a GD order is 2^(32*peak dimension) candidates.  Search: iterative deepening on
the peak with memoisation on the known set.

Message pair A only (B follows: same X by Lemma L, pins hold for both).
"""
import sys, itertools, time

CALLS = [
    ("K0", ("V0", "V4", "V8", "V12"), ("w0", "w1"), ("S0", "S4", "S8", "S12")),
    ("K1", ("V1", "V5", "V9", "V13"), ("w2", "w3"), ("S1", "S5", "S9", "S13")),
    ("K2", ("V2", "V6", "V10", "V14"), ("w4", "w5"), ("S2", "S6", "S10", "S14")),
    ("K3", ("V3", "V7", "V11", "V15"), ("w6", "w7"), ("S3", "S7", "S11", "S15")),
    ("D0", ("S0", "S5", "S10", "S15"), ("w8", "w9"), ("X0", "X5", "X10", "X15")),
    ("D1", ("S1", "S6", "S11", "S12"), ("w10", "w11"), ("X1", "X6", "X11", "X12")),
    ("D2", ("S2", "S7", "S8", "S13"), ("w12", "w13"), ("X2", "X7", "X8", "X13")),
    ("D3", ("S3", "S4", "S9", "S14"), ("w14", "w15"), ("X3", "X4", "X9", "X14")),
    ("C0", ("X0", "X4", "X8", "X12"), ("w2", "w6"), ("Y0", "Y4", "Y8", "Y12")),
    ("C1", ("X1", "X5", "X9", "X13"), ("w3", "w10"), ("Y1", "Y5", "Y9", "Y13")),
    ("C2", ("X2", "X6", "X10", "X14"), ("w7", "w0"), ("Y2", "Y6", "Y10", "Y14")),
]

VARS, REL = [], []


def vid(n):
    if n not in VARS:
        VARS.append(n)
    return VARS.index(n)


for nm, (a, b, c, d), (x, y), (A, B, C, D) in CALLS:
    a1, b1, c1, d1 = (nm + "." + s for s in ("a1", "b1", "c1", "d1"))
    for r in ((a1, a, b, x), (d1, d, a1), (c1, c, d1), (b1, b, c1),
              (A, a1, b1, y), (D, d1, A), (C, c1, D), (B, b1, C)):
        REL.append(tuple(vid(v) for v in r))

NV, NR = len(VARS), len(REL)
OCC = [[] for _ in range(NV)]
for ri, r in enumerate(REL):
    for v in r:
        OCC[v].append(ri)

CONST = ["V%d" % i for i in range(16) if i != 12] + ["w4", "w13", "w14", "w15", "X3", "X7", "X11", "X15"]
E1IN = ["Y1", "Y6", "Y12", "w12", "w5"]
E3IN = ["Y4", "Y9", "Y14", "w8"]


def mask(names):
    m = 0
    for n in names:
        m |= 1 << VARS.index(n)
    return m


def closure(known, used):
    """Propagate. Returns (known, used, nchecks_new). used = bitmask of relations used or counted."""
    changed, checks = True, 0
    while changed:
        changed = False
        for ri in range(NR):
            if used >> ri & 1:
                continue
            r = REL[ri]
            unk = [v for v in r if not known >> v & 1]
            if len(unk) == 1:
                known |= 1 << unk[0]
                used |= 1 << ri
                changed = True
            elif not unk:
                used |= 1 << ri
                checks += 1
                changed = True
    return known, used, checks


FULL = (1 << NV) - 1


def search(known0, peak, free_ok=0):
    """Is there a GD order with peak dimension <= peak that determines every variable?
    free_ok: number of guesses that are free choices (dof of the system; no check owed).
    Returns (order, trace) or None."""
    k, u, c = closure(known0, 0)
    seen = {}
    best = [None]

    def rec(known, used, dim, order, trace):
        if known == FULL:
            best[0] = (list(order), list(trace))
            return True
        key = known
        if key in seen and seen[key] <= dim:
            return False
        seen[key] = dim
        if dim + 1 > peak:
            return False
        # candidate guesses: unknown vars in a relation with exactly 2 unknowns
        cand = set()
        for ri in range(NR):
            if used >> ri & 1:
                continue
            unk = [v for v in REL[ri] if not known >> v & 1]
            if len(unk) == 2:
                cand.update(unk)
        if not cand:
            cand = {v for v in range(NV) if not known >> v & 1}
        for v in sorted(cand):
            k2, u2, ch = closure(known | (1 << v), used)
            nd = dim + 1 - ch
            order.append(VARS[v]); trace.append((dim + 1, nd))
            if rec(k2, u2, nd, order, trace):
                return True
            order.pop(); trace.pop()
        return False

    rec(k, u, -c, [], [])
    return best[0]


def run(label, known_names, dof, maxpeak=4, budget_s=480):
    known0 = mask(CONST + known_names)
    t0 = time.time()
    for peak in range(dof, maxpeak + 1):
        res = search(known0, peak)
        if res:
            order, tr = res
            print("%s: dof=%d  min peak dimension = %d words (%d free choices + %d scanned)"
                  % (label, dof, peak, dof, peak - dof))
            print("   order:", " -> ".join("%s[%d/%d]" % (o, a, b) for o, (a, b) in zip(order, tr)))
            print("   guesses=%d  time %.1fs" % (len(order), time.time() - t0))
            return peak
        if time.time() - t0 > budget_s:
            print("%s: budget hit at peak %d" % (label, peak))
            return None
    print("%s: no order with peak <= %d" % (label, maxpeak))
    return None


if __name__ == "__main__":
    print("variables %d, relations %d, unknown at start %d" % (NV, NR, NV - len(CONST)))
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("all", "free"):
        # no E words known: 9 free words; dimension counts free choices (expect peak 9 with 0 checks)
        run("front-line system (nothing held)", [], 9, maxpeak=9)
    if which in ("all", "e3"):
        run("hold E3 inputs (Y4,Y9,Y14,w8)", E3IN, 5, maxpeak=7)
    if which in ("all", "e1"):
        run("hold E1 inputs (Y1,Y6,Y12,w12,w5)", E1IN, 4, maxpeak=6)
    if which in ("all", "lift"):
        run("lift: hold all 9 E inputs", E1IN + E3IN, 0, maxpeak=4)
