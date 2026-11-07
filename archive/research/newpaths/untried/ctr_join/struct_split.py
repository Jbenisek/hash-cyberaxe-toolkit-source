"""ctr x join, part S: structural (word-level) split search over EVERY triangular basis.

Uses the equation system of counter_next/knobs/model.py unchanged (imported).
A triangular basis = an orientation of the equations (each equation solves one of its words),
acyclic, every non-basis word solved exactly once.  With up to `max_checks` equations left
unsolved (checks), the basis grows by that many words.

Targets (from coupling.py diffs(), checked in RESULT.md):
  key1 (E1 side, 128 bits) is a function of T1 = {E1.a2, E1.b1, E1.d1}
  key3 (E3 side, 128 bits) is a function of T3 = {E3.h1, E3.g1, E3.f1, E3.e2}

Split (meet-in-the-middle) = a triangular basis B = U + V + Fx with
  T1 depending on no V word, T3 depending on no U word,
  T1 depending on some U word, T3 depending on some V word.
Then for each Fx, key1 = f(U) and key3 = g(V): a list join decouples the two sides.
With checks allowed, a check equation must contain no word that depends on both U and V
(so it is separable and can be joined on); gain needs min(|U|-cU, |V|-cV) > cX.

Dependency is structural (union over the solving equation's other words); a structural
non-dependency is an exact non-dependency.
"""

# Publication path adapter: resolve data paths from the extracted source tree.
def _hca_public_path_text(value):
    if "__HCA_WORKSPACE__/" not in value:
        return value
    import os as _hca_os
    from pathlib import Path as _hca_Path
    root = _hca_os.environ.get("HASHCYBERAXE_WORKSPACE")
    if root is None:
        here = _hca_Path(__file__).resolve().parent
        root = next((str(p) for p in (here, *here.parents) if (p / "research").is_dir()), None)
    if root is None:
        raise FileNotFoundError("Extract the research source tree, or set HASHCYBERAXE_WORKSPACE to its archive directory.")
    return value.replace("__HCA_WORKSPACE__/", str(_hca_Path(root).resolve()).replace("\\", "/") + "/")

import sys
import time

sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/newpaths/counter_next/knobs'))
import model  # noqa: E402

from z3 import (Bool, Int, Solver, Or, And, Not, Implies, If, Sum, PbEq, AtMost, sat, unsat,
                is_true)  # noqa: E402

T1 = ['E1.a2', 'E1.b1', 'E1.d1']
T3 = ['E3.h1', 'E3.g1', 'E3.f1', 'E3.e2']


def build(counter, w14free, mode, max_checks=0, force_basis=None):
    """mode: 'split' (U and V), 'U' (E1-only word exists), 'V' (E3-only word exists), 'any'."""
    eqs, words = model.system(counter, w14free)
    return build_from(eqs, words, T1, T3, mode, max_checks, force_basis)


def build_from(eqs, words, T1, T3, mode, max_checks=0, force_basis=None):
    words = sorted(words)
    s = Solver()
    sol = {}
    chk = {}
    for i, (_, ws) in enumerate(eqs):
        for w in ws:
            sol[i, w] = Bool('s_%d_%s' % (i, w))
        chk[i] = Bool('c_%d' % i)
        s.add(PbEq([(sol[i, w], 1) for w in ws] + [(chk[i], 1)], 1))
    s.add(Sum([If(chk[i], 1, 0) for i in chk]) <= max_checks)
    occ = {w: [i for i, (_, ws) in enumerate(eqs) if w in ws] for w in words}
    basis = {w: Bool('b_%s' % w) for w in words}
    for w in words:
        s.add(AtMost(*[sol[i, w] for i in occ[w]], 1))
        s.add(basis[w] == Not(Or([sol[i, w] for i in occ[w]])))
    lev = {w: Int('l_%s' % w) for w in words}
    for (i, w), v in sol.items():
        for x in eqs[i][1]:
            if x != w:
                s.add(Implies(v, lev[x] < lev[w]))
    isU = {w: Bool('U_%s' % w) for w in words}
    isV = {w: Bool('V_%s' % w) for w in words}
    dU = {w: Bool('dU_%s' % w) for w in words}
    dV = {w: Bool('dV_%s' % w) for w in words}
    for w in words:
        s.add(Implies(isU[w], basis[w]), Implies(isV[w], basis[w]), Not(And(isU[w], isV[w])))
        s.add(Implies(basis[w], dU[w] == isU[w]), Implies(basis[w], dV[w] == isV[w]))
        for i in occ[w]:
            others = [x for x in eqs[i][1] if x != w]
            s.add(Implies(sol[i, w], dU[w] == Or([dU[x] for x in others])))
            s.add(Implies(sol[i, w], dV[w] == Or([dV[x] for x in others])))
    # checks must be separable (no mixed word); count their kinds
    ckind = {}
    for i, (_, ws) in enumerate(eqs):
        s.add(Implies(chk[i], And([Not(And(dU[x], dV[x])) for x in ws])))
        hasU = Or([dU[x] for x in ws])
        hasV = Or([dV[x] for x in ws])
        ckind[i] = (And(chk[i], hasU, Not(hasV)), And(chk[i], hasV, Not(hasU)), And(chk[i], hasU, hasV))
    nU = Sum([If(isU[w], 1, 0) for w in words])
    nV = Sum([If(isV[w], 1, 0) for w in words])
    cU = Sum([If(ckind[i][0], 1, 0) for i in ckind])
    cV = Sum([If(ckind[i][1], 1, 0) for i in ckind])
    cX = Sum([If(ckind[i][2], 1, 0) for i in ckind])
    if mode in ('split', 'split_nogain'):
        s.add(*([Not(dV[t]) for t in T1] + [Not(dU[t]) for t in T3]))
        s.add(Or([dU[t] for t in T1]), Or([dV[t] for t in T3]))
        if max_checks and mode == 'split':
            s.add(nU - cU > cX, nV - cV > cX)
    elif mode == 'U':      # some basis word moves key1 and never key3 (no V side)
        s.add(*[Not(dU[t]) for t in T3], Or([dU[t] for t in T1]))
        s.add(*[Not(isV[w]) for w in words])
    elif mode == 'V':      # some basis word moves key3 and never key1 (no U side)
        s.add(*[Not(dV[t]) for t in T1], Or([dV[t] for t in T3]))
        s.add(*[Not(isU[w]) for w in words])
    if force_basis is not None:
        s.add(*[basis[w] == (w in force_basis) for w in words])
    return s, eqs, words, sol, chk, basis, isU, isV


def brute_split(eqs, words, T1, T3):
    """All triangular bases by enumeration; returns (split, Uonly, Vonly) existence."""
    import itertools
    words = sorted(words)
    nb = len(words) - len(eqs)
    res = [False, False, False]
    if nb < 1:
        return tuple(res)
    for B in itertools.combinations(words, nb):
        ok, order, checks = model.propagate(eqs, set(B))
        if not ok:
            continue
        dep = taint(eqs, words, set(B), [(i, w) for i, w in order if w is not None])
        d1 = set().union(*[dep[t] for t in T1])
        d3 = set().union(*[dep[t] for t in T3])
        u = bool(d1 - d3)
        v = bool(d3 - d1)
        res[0] |= (u and v)
        res[1] |= u
        res[2] |= v
    return tuple(res)


def validate_encoding(ntests, seed):
    """z3 encoding vs brute force on random small systems (max_checks = 0)."""
    import random
    rng = random.Random(seed)
    bad = 0
    counts = [0, 0, 0]
    done = 0
    for _ in range(ntests):
        n = rng.randrange(6, 10)
        m = rng.randrange(2, n - 1)
        W = ['v%d' % i for i in range(n)]
        eqs = [(None, frozenset(rng.sample(W, rng.randrange(2, 5)))) for _ in range(m)]
        words = set().union(*[w for _, w in eqs])
        if len(words) - m < 2:
            continue
        pool = sorted(words)
        rng.shuffle(pool)
        k1 = rng.randrange(1, 3)
        k3 = rng.randrange(1, 3)
        if k1 + k3 > len(pool):
            continue
        t1, t3 = pool[:k1], pool[k1:k1 + k3]
        brute = brute_split(eqs, words, t1, t3)
        z = []
        for mode in ('split', 'U', 'V'):
            s = build_from(eqs, words, t1, t3, mode, 0)[0]
            z.append(s.check() == sat)
        done += 1
        for j in range(3):
            counts[j] += brute[j]
            bad += (brute[j] != z[j])
    return bad, done, counts


def taint(eqs, words, basis_set, solving):
    """solving: list of (eq index, word) in solving order. Returns word -> set of basis words."""
    dep = {w: {w} for w in basis_set}
    for i, w in solving:
        d = set()
        for x in eqs[i][1]:
            if x != w:
                d |= dep[x]
        dep[w] = d
    return dep


def classify_basis(eqs, words, B):
    ok, order, checks = model.propagate(eqs, set(B))
    if not ok:
        return ok, checks, None
    dep = taint(eqs, words, set(B), [(i, w) for i, w in order if w is not None])
    d1 = set().union(*[dep[t] for t in T1])
    d3 = set().union(*[dep[t] for t in T3])
    cls = {b: ('E1only' if (b in d1 and b not in d3) else 'E3only' if (b in d3 and b not in d1)
               else 'both' if b in d1 else 'neither') for b in B}
    return ok, checks, cls


def run(counter, w14free, mode, max_checks=0, timeout_ms=None):
    t0 = time.time()
    s, eqs, words, sol, chk, basis, isU, isV = build(counter, w14free, mode, max_checks)
    if timeout_ms:
        s.set('timeout', timeout_ms)
    r = s.check()
    dt = time.time() - t0
    tag = 'counter=%d %s mode=%s max_checks=%d' % (counter, 'w14free' if w14free else 'w14pinned',
                                                   mode, max_checks)
    line = '%s: %s (%.1fs, words %d, equations %d)' % (tag, r, dt, len(words), len(eqs))
    print(line, flush=True)
    out = [line]
    if r == sat:
        m = s.model()
        B = [w for w in words if is_true(m.eval(basis[w], model_completion=True))]
        U = [w for w in B if is_true(m.eval(isU[w], model_completion=True))]
        V = [w for w in B if is_true(m.eval(isV[w], model_completion=True))]
        C = [i for i in chk if is_true(m.eval(chk[i], model_completion=True))]
        out.append('  basis (%d): %s' % (len(B), ' '.join(B)))
        out.append('  U: %s   V: %s   checks: %s' % (' '.join(U), ' '.join(V),
                                                     [eqs[i][0] for i in C]))
        # independent dependency pass from the extracted orientation
        solved = {w: i for (i, w), v in sol.items() if is_true(m.eval(v, model_completion=True))}
        dep = {b: {b} for b in B}
        changed = True
        while changed:
            changed = False
            for w, i in solved.items():
                if w in dep:
                    continue
                others = [x for x in eqs[i][1] if x != w]
                if all(x in dep for x in others):
                    dep[w] = set().union(*[dep[x] for x in others])
                    changed = True
        if len(dep) == len(words):
            Us, Vs = set(U), set(V)
            kinds = []
            for i in C:
                hu = any(dep[x] & Us for x in eqs[i][1])
                hv = any(dep[x] & Vs for x in eqs[i][1])
                kinds.append('cross' if hu and hv else 'U' if hu else 'V' if hv else 'Fx')
            d1 = set().union(*[dep[t] for t in T1])
            d3 = set().union(*[dep[t] for t in T3])
            out.append('  re-derived: check kinds %s; U words reaching key1 %s; V words reaching key3 %s; '
                       'key1 deps in V %s; key3 deps in U %s' % (kinds, sorted(d1 & Us), sorted(d3 & Vs),
                                                                 sorted(d1 & Vs), sorted(d3 & Us)))
        else:
            out.append('  re-derived: orientation did not propagate to all words (%d of %d)' % (len(dep), len(words)))
        if not C:
            ok, nchk, cls = classify_basis(eqs, words, B)
            out.append('  independent re-check: triangular %s checks %d' % (ok, nchk))
            if cls:
                out.append('  basis word classes: ' + ' '.join('%s:%s' % kv for kv in sorted(cls.items())))
        for l in out[1:]:
            print(l, flush=True)
    return r, out


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else 'all'
    lines = []
    configs = [(c, f) for f in (False, True) for c in (0, 1, 2)]
    if which == 'validate':
        t0 = time.time()
        bad, done, counts = validate_encoding(300, 11)
        l = ('validate: z3 encoding vs brute force over all bases, %d random systems x 3 modes: '
             '%d mismatches; brute-force positives split/U/V = %s (%.0fs)' % (done, bad, counts, time.time() - t0))
        print(l, flush=True)
        lines.append(l)
        # positive control: the filed basis must be accepted, and every word classified
        filed = ['C0.c1', 'C0.d1', 'D3.d1', 'S15', 'S9', 'w5', 'X2', 'Y4']
        for c, extra in ((0, []), (1, ['T0']), (1, ['E1.d1']), (1, ['E3.h1']), (2, ['T0', 'T1'])):
            s, eqs, words, *_ = build(c, False, 'any', 0, force_basis=set(filed + extra))
            r = s.check()
            ok, nchk, cls = classify_basis(eqs, words, filed + extra)
            l = ('control counter=%d basis filed8+%s: z3 %s; propagate triangular %s; classes %s'
                 % (c, '+'.join(extra) or '-', r, ok,
                    ' '.join('%s:%s' % kv for kv in sorted(cls.items())) if cls else None))
            print(l, flush=True)
            lines.append(l)
    if which in ('all', 'split'):
        for c, f in configs:
            lines += run(c, f, 'split', 0)[1]
    if which in ('all', 'onesided'):
        for c, f in configs:
            lines += run(c, f, 'U', 0)[1]
            lines += run(c, f, 'V', 0)[1]
    if which in ('all', 'checks'):
        if len(sys.argv) > 3:          # one config, one check budget: checks c,f mc
            c_, f_ = sys.argv[2].split(',')
            lines += run(int(c_), f_ == '1', 'split', int(sys.argv[3]), timeout_ms=1080000)[1]
        else:
            for mc in (1, 2):
                for c, f in configs:
                    lines += run(c, f, 'split', mc)[1]
    if which == 'pairs':
        # sub-events: one E1 key word against one E3 key word (and E1/E3 inputs), no checks
        A1 = T1 + ['E1.a1', 'Y1', 'Y6', 'Y12', 'w12', 'w5']
        A3 = T3 + ['Y4', 'Y9', 'Y14', 'w8']
        for c, f in configs:
            eqs, words = model.system(c, f)
            sat_pairs = []
            t0 = time.time()
            for a in A1:
                for b in A3:
                    if a not in words or b not in words:
                        continue
                    s = build_from(eqs, words, [a], [b], 'split', 0)[0]
                    if s.check() == sat:
                        sat_pairs.append('%s|%s' % (a, b))
            l = ('counter=%d %s pairs E1-word x E3-word (%d x %d): split SAT for %d pairs %s (%.0fs)'
                 % (c, 'w14free' if f else 'w14pinned', len(A1), len(A3), len(sat_pairs),
                    ' '.join(sat_pairs), time.time() - t0))
            print(l, flush=True)
            lines.append(l)
    if which == 'force':
        # minimal number of check equations (= guessed words) for a basis that CONTAINS a set F:
        # F = T1+T3 is "prescribe both keys, then solve the message" (the algebraic decoupling)
        cfgs = [(0, False), (1, False), (2, False), (1, True)]
        if len(sys.argv) > 2:
            c_, f_ = sys.argv[2].split(',')
            cfgs = [(int(c_), f_ == '1')]
        for c, f in cfgs:
            eqs, words = model.system(c, f)
            for name, F in (('T3', T3), ('T1', T1), ('T1+T3', T1 + T3)):
                found = None
                for mc in range(0, 5):
                    t0 = time.time()
                    s = build_from(eqs, words, T1, T3, 'any', mc)[0]
                    s.add(*[Bool('b_%s' % w) for w in F])   # same z3 constants as basis[w]
                    s.set('timeout', 240000)
                    r = s.check()
                    l = '  counter=%d %s force %s with max_checks=%d: %s (%.1fs)' % (
                        c, 'w14free' if f else 'w14pinned', name, mc, r, time.time() - t0)
                    print(l, flush=True)
                    lines.append(l)
                    if r == sat:
                        found = mc
                        break
                l = 'counter=%d %s: minimal checks to prescribe %s = %s' % (
                    c, 'w14free' if f else 'w14pinned', name, found)
                print(l, flush=True)
                lines.append(l)
    if which == 'nogain':
        # with checks allowed but no gain condition: smallest separable cut that decouples at all
        for c, f in ((1, False), (2, True)):
            for mc in (1, 2, 3):
                r, o = run(c, f, 'split_nogain', mc, timeout_ms=360000)
                lines += o
                if r == sat:
                    break
    name = 'struct_split_%s%s.txt' % (which, ('_' + sys.argv[2].replace(',', '_')) if len(sys.argv) > 2 else '')
    open(name, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    print('WROTE', name)


if __name__ == '__main__':
    main()
