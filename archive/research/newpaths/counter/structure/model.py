"""Part 2a: own word-level model of the 55/63 construction and own basis test (no SAT, no team code).

Model: every G assignment is one equation over the unknown words it contains; each equation can be solved
for any one of its unknowns (all are bijective in each argument).  E1/E3 first halves are modelled with the
pinned Y11, Y3, w15 substituted (c1 = Y11 + d1, e1 = Y3 + Y4).  Constants: IV, block length, flags, the pins
X3 X7 X11 X15 w4 w13 w15 (and w14 unless --w14free), hence all of K2's first four values and C3 entirely.
Counter: K0's d input is v12 = T0, K1's d input is v13 = T1; COUNTER=0: both constant 0; 1: T0 unknown;
2: T0 and T1 unknown.

Basis test.  B (|B| = n - m) is a triangular basis iff forward propagation from B determines every word.
Existence of a basis containing a forced set F is decided by REVERSE PEELING: repeatedly delete an equation
that owns a word not in F occurring in no other remaining equation.  Peeling is monotone (a private word stays
private when other equations are deleted), so greedy peeling succeeds iff some order does (proof in
STRUCTURE.md); success <=> a basis containing F exists, and the peeling gives the order (reversed) and the
basis (unclaimed words).  validate() checks this against brute force on random small systems.
"""
import itertools, random, sys

IVN = ['IV0', 'IV1', 'IV2', 'IV3', 'IV4', 'IV5', 'IV6', 'IV7']


def gcall(tag, A, B, C, D, x, y, oa, ob, oc, od):
    a1, d1, c1, b1 = tag + '.a1', tag + '.d1', tag + '.c1', tag + '.b1'
    return [(a1, (A, B, x)), (d1, (D, a1)), (c1, (C, d1)), (b1, (B, c1)),
            (oa, (a1, b1, y)), (od, (d1, oa)), (oc, (c1, od)), (ob, (b1, oc))]


def system(counter=1, w14free=False):
    T0 = 'T0' if counter >= 1 else 'c0'
    T1 = 'T1' if counter >= 2 else 'c0'
    R = []
    R += gcall('K0', 'IV0', 'IV4', 'IV0', T0, 'w0', 'w1', 'S0', 'S4', 'S8', 'S12')
    R += gcall('K1', 'IV1', 'IV5', 'IV1', T1, 'w2', 'w3', 'S1', 'S5', 'S9', 'S13')
    R += gcall('K2', 'IV2', 'IV6', 'IV2', 'len', 'w4', 'w5', 'S2', 'S6', 'S10', 'S14')
    R += gcall('K3', 'IV3', 'IV7', 'IV3', 'flags', 'w6', 'w7', 'S3', 'S7', 'S11', 'S15')
    R += gcall('D0', 'S0', 'S5', 'S10', 'S15', 'w8', 'w9', 'X0', 'X5', 'X10', 'X15')
    R += gcall('D1', 'S1', 'S6', 'S11', 'S12', 'w10', 'w11', 'X1', 'X6', 'X11', 'X12')
    R += gcall('D2', 'S2', 'S7', 'S8', 'S13', 'w12', 'w13', 'X2', 'X7', 'X8', 'X13')
    R += gcall('D3', 'S3', 'S4', 'S9', 'S14', 'w14', 'w15', 'X3', 'X4', 'X9', 'X14')
    R += gcall('C0', 'X0', 'X4', 'X8', 'X12', 'w2', 'w6', 'Y0', 'Y4', 'Y8', 'Y12')
    R += gcall('C1', 'X1', 'X5', 'X9', 'X13', 'w3', 'w10', 'Y1', 'Y5', 'Y9', 'Y13')
    R += gcall('C2', 'X2', 'X6', 'X10', 'X14', 'w7', 'w0', 'Y2', 'Y6', 'Y10', 'Y14')
    R += [('E1.a1', ('Y1', 'Y6', 'w12')), ('E1.d1', ('Y12', 'E1.a1')),
          ('E1.b1', ('Y6', 'E1.d1', 'Y11')), ('E1.a2', ('E1.a1', 'E1.b1', 'w5')),
          ('E3.h1', ('Y14', 'Y3', 'Y4', 'w15')), ('E3.g1', ('Y9', 'E3.h1')),
          ('E3.f1', ('Y4', 'E3.g1')), ('E3.e2', ('Y3', 'Y4', 'w15', 'E3.f1', 'w8'))]
    const = set(IVN) | {'c0', 'len', 'flags', 'X3', 'X7', 'X11', 'X15', 'w4', 'w13', 'w15', 'Y3', 'Y11'}
    if not w14free:
        const.add('w14')
    # K2's first four values are functions of constants only -> constants
    const |= {'K2.a1', 'K2.d1', 'K2.c1', 'K2.b1'}
    eqs = []
    for lhs, args in R:
        ws = frozenset([lhs, *args]) - const
        if not ws:                # an equation among constants only (K2 first half)
            assert lhs.startswith('K2.'), lhs
            continue
        eqs.append((lhs, ws))
    words = set().union(*[w for _, w in eqs])
    return eqs, words


def peel(eqs, forced):
    """Reverse peeling.  Returns (ok, order, basis): order = list of (eq_index, solved_word) in SOLVING order."""
    rem = set(range(len(eqs)))
    occ = {}
    for i, (_, ws) in enumerate(eqs):
        for w in ws:
            occ.setdefault(w, set()).add(i)
    removed = []
    progress = True
    while rem and progress:
        progress = False
        for i in sorted(rem):
            priv = [w for w in sorted(eqs[i][1]) if w not in forced and occ[w] == {i}]
            if priv:
                w = priv[0]
                removed.append((i, w))
                rem.discard(i)
                for u in eqs[i][1]:
                    occ[u].discard(i)
                progress = True
    words = set().union(*[w for _, w in eqs])
    claimed = {w for _, w in removed}
    return (not rem), removed[::-1], sorted(words - claimed), rem


def propagate(eqs, basis):
    """Forward: from basis, solve any equation with exactly one unknown.  Returns (ok, order, checks)."""
    known = set(basis)
    used = set()
    order = []
    changed = True
    while changed:
        changed = False
        for i, (_, ws) in enumerate(eqs):
            if i in used:
                continue
            unk = [w for w in ws if w not in known]
            if len(unk) == 1:
                known.add(unk[0]); used.add(i); order.append((i, unk[0])); changed = True
            elif not unk:
                used.add(i); order.append((i, None)); changed = True     # a check: over-determined
    words = set().union(*[w for _, w in eqs])
    checks = sum(1 for _, w in order if w is None)
    return known >= words and checks == 0, order, checks


def validate(ntests=400, seed=1):
    """Peeling existence vs brute force over all bases, random small systems."""
    rng = random.Random(seed)
    bad = 0
    yes = 0
    for _ in range(ntests):
        n = rng.randrange(5, 10)
        m = rng.randrange(2, n - 1)
        W = [f'v{i}' for i in range(n)]
        eqs = [(None, frozenset(rng.sample(W, rng.randrange(2, 5)))) for _ in range(m)]
        words = set().union(*[w for _, w in eqs])
        nb = len(words) - m
        if nb < 1:
            continue
        F = set(rng.sample(sorted(words), rng.randrange(0, min(3, nb) + 1)))
        brute = False
        rest = sorted(words - F)
        for extra in itertools.combinations(rest, nb - len(F)):
            if propagate(eqs, F | set(extra))[0]:
                brute = True
                break
        ok = peel(eqs, F)[0]
        if ok:
            # also check the peeling basis propagates
            _, _, basis, _ = peel(eqs, F)
            ok = propagate(eqs, basis)[0] and F <= set(basis)
        yes += brute
        bad += (ok != brute)
    return bad, yes, ntests


TARGETS = ['E1.d1', 'E1.a1', 'E1.b1', 'E1.a2', 'E3.h1', 'E3.g1', 'E3.f1', 'E3.e2',
           'Y0', 'Y1', 'Y2', 'Y5', 'Y6', 'Y8', 'Y9', 'Y10', 'Y12', 'Y13', 'Y14',
           'w0', 'w1', 'w2', 'w3', 'w5', 'w6', 'w7', 'w8', 'w9', 'w10', 'w11', 'w12', 'X2', 'X9', 'X14']


def main():
    bad, yes, nt = validate(600, 7)
    print(f'validation: peeling vs brute force on {nt} random systems: {bad} mismatches ({yes} with a basis)')
    for w14free in (False, True):
        for counter in (0, 1, 2):
            eqs, words = system(counter, w14free)
            nb = len(words) - len(eqs)
            ok_y4 = peel(eqs, {'Y4'})[0]
            tag = f"counter={counter} {'w14 free' if w14free else 'w14=0 pinned'}"
            print(f'\n[{tag}] words {len(words)}, equations {len(eqs)}, basis size {nb}; Y4 alone: {ok_y4}')
            yes_t, no_t = [], []
            for T in TARGETS:
                if T not in words:
                    continue
                (yes_t if peel(eqs, {'Y4', T})[0] else no_t).append(T)
            print('  Y4 + T basis YES:', ' '.join(yes_t))
            print('  Y4 + T basis NO :', ' '.join(no_t))
            for trip in (('E1.d1', 'E3.h1'), ('E1.d1', 'E3.g1'), ('E1.d1', 'E3.e2'), ('E1.d1', 'Y14'),
                         ('E3.h1', 'E3.g1'), ('E1.d1', 'E1.b1')):
                print(f'  Y4 + {trip[0]} + {trip[1]}: {peel(eqs, {"Y4", *trip})[0]}')
    # the filed basis and the counter arrangement
    eqs, words = system(1, False)
    filed = ['C0.c1', 'C0.d1', 'D3.d1', 'S15', 'S9', 'w5', 'X2', 'Y4']
    for name, B in (('filed 8 + T0 (t free, nothing else)', filed + ['T0']),
                    ('filed 8 + E1.d1 (T0 determined)', filed + ['E1.d1']),
                    ('filed 8 + E3.h1 (T0 determined)', filed + ['E3.h1'])):
        ok, order, checks = propagate(eqs, set(B))
        print(f'\nbasis {name}: triangular {ok} (checks {checks})')
    e0, w0 = system(0, False)
    print('counter=0: filed 8 triangular:', propagate(e0, set(filed))[0],
          '; filed 8 minus X2 plus E1.d1:', propagate(e0, set(filed) - {'X2'} | {'E1.d1'})[0])


if __name__ == '__main__':
    main()
