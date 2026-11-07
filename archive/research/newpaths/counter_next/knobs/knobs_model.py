"""knobs_model.py (counter_next/knobs; research only).
Word-level basis questions for the extra knobs of tree mode, using a COPY of counter/structure/model.py
(reverse peeling, validated there against brute force on 600 random systems).

Variants (w14 pinned, pin H8):
  ctr1   : T0 (v12) unknown                      - the counter arrangement
  ctr2   : T0 and T1 (v13) unknown
  cv     : multi-block last chunk: cv0..cv7 (K-calls' a and b inputs) unknown, T0 unknown
  cvT    : as cv, but T0 forced into the basis (t fixed per outer step, as a chained CV requires)
Questions:
  Q1  full system: which X give a basis with {Y4, E1.d1, X}?
  Q2  outer subsystem (the per-trial cone of the counter arrangement removed): which outer words X can be
      prescribed next to Y4 per outer step, and does that need T1 (v13) to be SOLVED (2^-13 filter)?
  Q3  multi-block: with t fixed per outer step (T0 in the basis) and the CV words drawn (in the basis), is there a
      basis with {Y4, E1.d1}?  (If not, the chained CV cannot replace the counter.)
"""
import sys
sys.dont_write_bytecode = True
import model as M

IVN = M.IVN


def system(var):
    T0 = 'T0' if var in ('ctr1', 'ctr2', 'cv', 'cvT') else 'c0'
    T1 = 'T1' if var == 'ctr2' else 'c0'
    cv = var in ('cv', 'cvT')
    A = [f'cv{i}' for i in range(8)] if cv else IVN
    R = []
    R += M.gcall('K0', A[0], A[4], 'IV0', T0, 'w0', 'w1', 'S0', 'S4', 'S8', 'S12')
    R += M.gcall('K1', A[1], A[5], 'IV1', T1, 'w2', 'w3', 'S1', 'S5', 'S9', 'S13')
    R += M.gcall('K2', A[2], A[6], 'IV2', 'len', 'w4', 'w5', 'S2', 'S6', 'S10', 'S14')
    R += M.gcall('K3', A[3], A[7], 'IV3', 'flags', 'w6', 'w7', 'S3', 'S7', 'S11', 'S15')
    R += M.gcall('D0', 'S0', 'S5', 'S10', 'S15', 'w8', 'w9', 'X0', 'X5', 'X10', 'X15')
    R += M.gcall('D1', 'S1', 'S6', 'S11', 'S12', 'w10', 'w11', 'X1', 'X6', 'X11', 'X12')
    R += M.gcall('D2', 'S2', 'S7', 'S8', 'S13', 'w12', 'w13', 'X2', 'X7', 'X8', 'X13')
    R += M.gcall('D3', 'S3', 'S4', 'S9', 'S14', 'w14', 'w15', 'X3', 'X4', 'X9', 'X14')
    R += M.gcall('C0', 'X0', 'X4', 'X8', 'X12', 'w2', 'w6', 'Y0', 'Y4', 'Y8', 'Y12')
    R += M.gcall('C1', 'X1', 'X5', 'X9', 'X13', 'w3', 'w10', 'Y1', 'Y5', 'Y9', 'Y13')
    R += M.gcall('C2', 'X2', 'X6', 'X10', 'X14', 'w7', 'w0', 'Y2', 'Y6', 'Y10', 'Y14')
    R += [('E1.a1', ('Y1', 'Y6', 'w12')), ('E1.d1', ('Y12', 'E1.a1')),
          ('E1.b1', ('Y6', 'E1.d1', 'Y11')), ('E1.a2', ('E1.a1', 'E1.b1', 'w5')),
          ('E3.h1', ('Y14', 'Y3', 'Y4', 'w15')), ('E3.g1', ('Y9', 'E3.h1')),
          ('E3.f1', ('Y4', 'E3.g1')), ('E3.e2', ('Y3', 'Y4', 'w15', 'E3.f1', 'w8'))]
    const = set(IVN) | {'c0', 'len', 'flags', 'X3', 'X7', 'X11', 'X15', 'w4', 'w13', 'w15', 'Y3', 'Y11', 'w14'}
    if not cv:   # K2's first half is constant only with the fixed IV (cv2, cv6 enter it otherwise)
        const |= {'K2.a1', 'K2.d1', 'K2.c1', 'K2.b1'}
    eqs = []
    for lhs, args in R:
        ws = frozenset([lhs, *args]) - const
        if not ws:
            continue
        eqs.append((lhs, ws))
    words = set().union(*[w for _, w in eqs])
    return eqs, words


# per-trial cone of the counter arrangement (counter/structure/cone_out.txt, 15 solved words + E1.d1)
INNER = ['E1.d1', 'E1.a1', 'Y6', 'E1.b1', 'E1.a2', 'Y10', 'Y14', 'E3.h1', 'E3.g1', 'E3.f1', 'E3.e2',
         'Y2', 'w0', 'K0.a1', 'T0', 'w1']
INNER_EQ_LHS = None   # identified by the solved word below


def outer_subsystem(var):
    """Remove the equations that solve the inner words (one per inner word except E1.d1) and the inner words."""
    eqs, words = system(var)
    ok, order, basis, _ = M.peel(eqs, {'Y4', 'E1.d1'})
    assert ok
    # use the counter arrangement's own order: re-derive which equation solves each inner word by propagation
    outer8 = ['C0.c1', 'C0.d1', 'D3.d1', 'S15', 'S9', 'w5', 'X2', 'Y4']
    B = set(outer8) | {'E1.d1'}
    if var == 'ctr2':
        B |= {'T1'}        # T1 constant in the counter arrangement: put it in the basis to read the order
    okp, ordp, checks = M.propagate(eqs, B)
    assert okp and checks == 0, (var, okp, checks)
    solve_eq = {w: i for i, w in ordp if w is not None}
    inner_eqs = {solve_eq[w] for w in INNER if w != 'E1.d1'}
    oeqs = [e for i, e in enumerate(eqs) if i not in inner_eqs]
    inner_words = set(INNER)
    oeqs = [(l, ws - inner_words) for l, ws in oeqs]
    # every remaining equation must have lost no unknown to the inner set (outer equations do not read inner words)
    for (l, ws), (l0, ws0) in zip(oeqs, [e for i, e in enumerate(eqs) if i not in inner_eqs]):
        assert ws == ws0, (l, ws0 & inner_words)
    owords = set().union(*[w for _, w in oeqs])
    return oeqs, owords


TARGETS = ['E1.a1', 'E1.b1', 'E1.a2', 'E3.h1', 'E3.g1', 'E3.f1', 'E3.e2',
           'Y0', 'Y1', 'Y2', 'Y5', 'Y6', 'Y8', 'Y9', 'Y10', 'Y12', 'Y13', 'Y14',
           'w0', 'w1', 'w2', 'w3', 'w5', 'w6', 'w7', 'w8', 'w9', 'w10', 'w11', 'w12', 'X2', 'X9', 'X14',
           'C2.b1', 'C2.c1', 'C2.a1', 'C2.d1']


def main():
    out = []
    p = out.append
    for var in ('ctr1', 'ctr2'):
        eqs, words = system(var)
        nb = len(words) - len(eqs)
        p(f'[{var}] Q1 full system: words {len(words)}, equations {len(eqs)}, basis size {nb}')
        yes = [X for X in TARGETS if X in words and M.peel(eqs, {'Y4', 'E1.d1', X})[0]]
        no = [X for X in TARGETS if X in words and X not in yes]
        p('  Y4 + E1.d1 + X  YES: ' + ' '.join(yes))
        p('  Y4 + E1.d1 + X  NO : ' + ' '.join(no))
    # Q2: outer subsystem
    for var in ('ctr1', 'ctr2'):
        oeqs, owords = outer_subsystem(var)
        nb = len(owords) - len(oeqs)
        p(f'[{var}] Q2 outer subsystem: words {len(owords)}, equations {len(oeqs)}, outer basis size {nb}')
        cand = [X for X in TARGETS + ['Y4'] if X in owords]
        yes = [X for X in cand if X != 'Y4' and M.peel(oeqs, {'Y4', X})[0]]
        p('  Y4 + X (outer) YES: ' + ' '.join(yes))
        p('  Y4 + X (outer) NO : ' + ' '.join(X for X in cand if X not in yes and X != 'Y4'))
        if var == 'ctr2':
            for X in yes:
                # does X need T1 solved?  test: basis containing Y4, X AND T1 (T1 chosen, not solved)
                withT1 = M.peel(oeqs, {'Y4', X, 'T1'})[0]
                p(f'    {X}: basis with T1 also in the basis (T1 chosen per outer step) = {withT1}'
                  + ('' if withT1 else '  -> T1 must be SOLVED per outer step (filter 2^-13 on outer steps)'))
            for pair in (('w8', 'Y9'), ('w8', 'Y12'), ('w8', 'Y1'), ('w8', 'w12'), ('w8', 'w5'), ('w8', 'C2.b1')):
                p(f'    Y4 + {pair[0]} + {pair[1]} (outer, T1 free): {M.peel(oeqs, {"Y4", *pair})[0]}')
    # Q3: multi-block last chunk
    for var in ('cv', 'cvT'):
        eqs, words = system(var)
        nb = len(words) - len(eqs)
        cvw = {f'cv{i}' for i in range(8)}
        p(f'[{var}] words {len(words)}, equations {len(eqs)}, basis size {nb}')
        F = {'Y4', 'E1.d1'} | cvw | ({'T0'} if var == 'cvT' else set())
        ok = M.peel(eqs, F)[0]
        p(f'  basis containing Y4, E1.d1, all eight CV words' + (' and T0' if var == 'cvT' else '') + f': {ok}')
        if var == 'cv':
            # which CV words must be SOLVED (not drawn) for Y4 + E1.d1?  try dropping one CV word from F at a time
            need = []
            for w in sorted(cvw):
                if M.peel(eqs, (F - {w}))[0]:
                    need.append(w)
            p('  dropping one CV word from the forced set gives a basis for: ' + (' '.join(need) or 'none'))
            p('  (a CV word that is SOLVED must hit a prescribed 32-bit value: a 2^-32 preimage filter)')
        # with T0 in the basis, does any single CV word left free make Y4+E1.d1 possible?
        if var == 'cvT':
            for w in sorted(cvw):
                ok1 = M.peel(eqs, (F - {w}))[0]
                if ok1:
                    p(f'  T0 fixed, {w} solved (preimage): Y4 + E1.d1 basis exists')
    print('\n'.join(out))


if __name__ == '__main__':
    main()
