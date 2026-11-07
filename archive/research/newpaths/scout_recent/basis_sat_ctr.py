#!/usr/bin/env python3
"""Exact version of basis_search.py: is there a basis (nine words from which everything else follows by
solving one equation at a time) that contains all the given target words?  Encoded as SAT (kissat):
m[e][v] = "equation e is solved for word v"; every equation is solved for exactly one of its words; no word
is solved for twice; targets are solved for by no equation; a level L[v] (order encoding) makes the
dependency graph acyclic.  UNSAT is a proof that no such basis exists.

    basis_sat.py T1,T2,.. [--not V1,V2,..] [--levels 100] [--time 300]
--not: words that must NOT be in the basis.
"""
import sys, subprocess, tempfile, os
from basis_search_ctr import system   # scout_recent copy: COUNTER / CVWORDS options

def main():
    args = sys.argv[1:]
    targets = [t for t in args[0].split(',') if t] if args and not args[0].startswith('--') else []
    opt = lambda k, d: args[args.index(k) + 1] if k in args else d
    notin = [t for t in opt('--not', '').split(',') if t]
    K = int(opt('--levels', '100')); tmo = int(opt('--time', '300'))
    eqs, names = system()
    nv = 0
    def new():
        nonlocal nv; nv += 1; return nv
    m = {(e, v): new() for e, vs in enumerate(eqs) for v in vs}
    o = {(v, k): new() for v in names for k in range(1, K + 1)}
    cl = []
    for e, vs in enumerate(eqs):
        cl.append([m[e, v] for v in vs])
        for i in range(len(vs)):
            for j in range(i + 1, len(vs)): cl.append([-m[e, vs[i]], -m[e, vs[j]]])
    for v in names:
        es = [e for e, vs in enumerate(eqs) if v in vs]
        for i in range(len(es)):
            for j in range(i + 1, len(es)): cl.append([-m[es[i], v], -m[es[j], v]])
        if v in targets:
            for e in es: cl.append([-m[e, v]])
        if v in notin: cl.append([m[e, v] for e in es])
        for k in range(1, K): cl.append([-o[v, k + 1], o[v, k]])
    for e, vs in enumerate(eqs):
        for v in vs:
            for u in vs:
                if u == v: continue
                cl.append([-m[e, v], o[v, 1]])
                cl.append([-m[e, v], -o[u, K]])
                for k in range(1, K): cl.append([-m[e, v], -o[u, k], o[v, k + 1]])
    # --outer A,B,..: these words must not depend on the "inner" basis words; --inner-min n: at least n inner
    # basis words (1 or 2); --inner-dep V,..: these words must depend on an inner word.
    outer = [t for t in opt('--outer', '').split(',') if t]
    innerdep = [t for t in opt('--inner-dep', '').split(',') if t]
    inner = {}; dep = {}
    if outer:
        inner = {v: new() for v in names}; dep = {v: new() for v in names}
        # exact dependency: dep[v] <-> inner[v] or (v solved from e and some other word of e depends)
        for v in names:
            es = [e for e, vs in enumerate(eqs) if v in vs]
            cl.append([-inner[v], dep[v]])
            for e in es: cl.append([-inner[v], -m[e, v]])
            sup = [inner[v]]
            for e in es:
                for u in eqs[e]:
                    if u == v: continue
                    cl.append([-m[e, v], -dep[u], dep[v]])
                    x = new(); cl.append([-x, m[e, v]]); cl.append([-x, dep[u]]); sup.append(x)
            cl.append([-dep[v]] + sup)
        for t in outer: cl.append([-dep[t]])
        for t in innerdep: cl.append([dep[t]])
        nmin = int(opt('--inner-min', '1'))
        if nmin == 1: cl.append([inner[v] for v in names])
        else:
            for w in names: cl.append([inner[v] for v in names if v != w])
    # --two-level T:B : loops "middle word z, innermost word Y4". Words that depend on Y4 but not on z can be
    # tabulated once per class member and reused for every z; words that depend on z but not on Y4 are computed
    # once per z. Only words that depend on BOTH must be recomputed per trial. Ask for a basis (containing Y4)
    # and a middle basis word z such that at most B words on the way to T depend on both.
    tl = opt('--two-level', '')
    zsel = {}; dY = {}; dZ = {}; both = {}
    if tl:
        t, bnd = tl.split(':'); bnd = int(bnd)
        zsel = {v: new() for v in names}; dY = {v: new() for v in names}; dZ = {v: new() for v in names}
        nd = {v: new() for v in names}; both = {v: new() for v in names}
        cl.append([dY['Y4']]); cl.append([-zsel['Y4']])
        cl.append([zsel[v] for v in names])
        vs_all = list(names)
        for i in range(len(vs_all)):
            for j in range(i + 1, len(vs_all)): cl.append([-zsel[vs_all[i]], -zsel[vs_all[j]]])
        for v in names:
            es = [e for e, vs in enumerate(eqs) if v in vs]
            cl.append([-zsel[v], dZ[v]])
            for e in es: cl.append([-zsel[v], -m[e, v]])          # the middle word is a basis word
            for e in es:
                for u in eqs[e]:
                    if u == v: continue
                    cl.append([-m[e, v], -dY[u], dY[v]])
                    cl.append([-m[e, v], -dZ[u], dZ[v]])
                    cl.append([-nd[v], -m[e, v], nd[u]])
            cl.append([-nd[v], -dY[v], -dZ[v], both[v]])
        cl.append([nd[t]]); cl.append([dY[t]]); cl.append([dZ[t]])
        xs = [both[v] for v in names]
        if bnd == 0:
            for x in xs: cl.append([-x])
        else:
            s = [[new() for _ in range(bnd)] for _ in xs]
            for i, x in enumerate(xs):
                cl.append([-x, s[i][0]])
                if i:
                    for j in range(bnd): cl.append([-s[i - 1][j], s[i][j]])
                    for j in range(1, bnd): cl.append([-x, -s[i - 1][j - 1], s[i][j]])
                    cl.append([-x, -s[i - 1][bnd - 1]])
    # --cone-max T:B : at most B words (inner words included) have to be recomputed per inner step to know T
    cm = opt('--cone-max', '')
    if cm and outer:
        for spec in cm.split(','):
            t, bnd = spec.split(':'); bnd = int(bnd)
            need = {v: new() for v in names}
            cl.append([need[t]]); cl.append([dep[t]])
            for e, vs in enumerate(eqs):
                for v in vs:
                    for u in vs:
                        if u != v: cl.append([-need[v], -m[e, v], -dep[u], need[u]])
            xs = [need[v] for v in names]            # at most bnd of xs (sequential counter)
            s = [[new() for _ in range(bnd)] for _ in xs]
            for i, x in enumerate(xs):
                cl.append([-x, s[i][0]])
                if i:
                    for j in range(bnd): cl.append([-s[i - 1][j], s[i][j]])
                    for j in range(1, bnd): cl.append([-x, -s[i - 1][j - 1], s[i][j]])
                    cl.append([-x, -s[i - 1][bnd - 1]])
    d = tempfile.mkdtemp(prefix='basis-'); p = os.path.join(d, 'p.cnf')
    with open(p, 'w') as f:
        f.write(f'p cnf {nv} {len(cl)}\n')
        for c in cl: f.write(' '.join(map(str, c)) + ' 0\n')
    r = subprocess.run(['kissat', '-q', f'--time={tmo}', p], capture_output=True, text=True)
    out = r.stdout
    tagline = f'targets {targets} not {notin}' + (f' outer {outer} inner-dep {innerdep}' if outer else '')
    if 's UNSATISFIABLE' in out:
        print(f'{tagline}: NO basis (proved)'); return 0
    if 's SATISFIABLE' not in out:
        print(f'{tagline}: no answer in {tmo} s'); return 0
    val = set()
    for line in out.splitlines():
        if line.startswith('v '): val.update(int(x) for x in line[2:].split() if int(x) > 0)
    solved = {v for (e, v), x in m.items() if x in val}
    basis = [v for v in names if v not in solved]
    lev = {v: sum(1 for k in range(1, K + 1) if o[v, k] in val) for v in names}
    if tl:
        z = [v for v in names if zsel[v] in val]
        order = sorted(((lev[v], e, v) for (e, v), x in m.items() if x in val))
        src = {v: [u for u in eqs[e] if u != v] for l, e, v in order}
        # recompute the exact dependencies from the solution (the solver may have over-marked)
        depy = {v: v == 'Y4' for v in names}; depz = {v: v in z for v in names}
        for l, e, v in order:
            depy[v] = any(depy[u] for u in src[v]); depz[v] = any(depz[u] for u in src[v])
        t = tl.split(':')[0]
        cone, stack = [], [t]
        while stack:
            v = stack.pop()
            if v in cone or v not in src: continue
            cone.append(v); stack.extend(src[v])
        cone.sort(key=lambda v: lev[v])
        b = [v for v in cone if depy[v] and depz[v]]; yo = [v for v in cone if depy[v] and not depz[v]]
        zo = [v for v in cone if depz[v] and not depy[v]]
        print(f'two-level {tl}: basis = {" ".join(basis)} | middle = {" ".join(z)} | per trial {len(b)}: {" ".join(b)}')
        print(f'   per member only ({len(yo)}): {" ".join(yo)}')
        print(f'   per middle step only ({len(zo)}): {" ".join(zo)}')
        print('   per-trial lines: ' + ' ; '.join(f'{v}<-{",".join(src[v])}' for v in b))
        if '--order' in args:
            # complete solving order; tag: T = per trial (depends on member and middle word), Y = per member
            # only, Z = per middle step only, - = once per outer step. A star marks words on the way to the test.
            print('   ORDER (tag word <- words of its equation)')
            for l, e, v in order:
                tag = 'T' if depy[v] and depz[v] else 'Y' if depy[v] else 'Z' if depz[v] else '-'
                print(f'   {tag}{"*" if v in cone else " "} {v:7s} <- {" ".join(src[v])}')
        return 0
    if outer:
        inn = [v for v in names if inner[v] in val]
        tg = ['E1.d1', 'E1.b1', 'E1.a2', 'Y4', 'E3.h1', 'E3.g1', 'E3.e2']
        print(f'outer {outer}: basis = {" ".join(basis)} | inner = {" ".join(inn)} | residual words that move: '
              f'{" ".join(t for t in tg if dep[t] in val)}')
    else:
        print(f'targets {targets} not {notin}: basis = {" ".join(basis)}')
    if '--order' in args or '--cone' in args:
        order = sorted(((lev[v], e, v) for (e, v), x in m.items() if x in val))
        src = {v: [u for u in eqs[e] if u != v] for l, e, v in order}
        isdep = (lambda v: dep[v] in val) if outer else (lambda v: False)
        if '--order' in args:
            for l, e, v in order: print(f'   {"*" if isdep(v) else " "} {v:7s} <- {" ".join(src[v])}')
        for t in [x for x in opt('--cone', '').split(',') if x]:
            # words that must be recomputed for every value of the inner words in order to know t
            cone, stack = [], [t]
            while stack:
                v = stack.pop()
                if v in cone or not isdep(v) or v not in src: continue
                cone.append(v); stack.extend(src[v])
            cone.sort(key=lambda v: lev[v])
            print(f'   cone of {t}: {len(cone)} equations per inner step: ' + ' ; '.join(f'{v}<-{",".join(src[v])}' for v in cone))
    return 0

if __name__ == '__main__':
    sys.exit(main())
