"""Part 2b: the per-trial cone of the arrangement 'filed basis with Y4 fixed per outer step, E1.d1 the inner
word, t (= T0) determined'.  Own model (model.py).  Prints the solving order, the words that move with E1.d1,
and the number of per-trial equations before each test word."""
import model as M

eqs, words = M.system(1, False)
outer = ['C0.c1', 'C0.d1', 'D3.d1', 'S15', 'S9', 'w5', 'X2', 'Y4']
inner = 'E1.d1'
ok, order, checks = M.propagate(eqs, set(outer + [inner]))
print('triangular', ok, 'checks', checks, 'equations', len(order))
# uniqueness of the matching: count words that have more than one equation able to determine them last
solve_eq = {w: i for i, w in order}
dep = {inner}
for i, w in order:
    if any(u in dep for u in eqs[i][1] if u != w):
        dep.add(w)
print(f'words that move with {inner} ({len(dep)} incl. itself):', ' '.join(sorted(dep)))
fixed_round0 = [w for w in words if (w.startswith('S') or w.startswith('X')) and w in dep]
print('round-0 words (S*, X*) that move:', fixed_round0 or 'none')


def ancestors(w):
    seen, st = set(), [w]
    while st:
        x = st.pop()
        if x in seen or x not in solve_eq:
            continue
        seen.add(x)
        st.extend(u for u in eqs[solve_eq[x]][1] if u != x)
    return seen


for test in ['E1.b1', 'E1.a2', 'E3.h1', 'E3.g1', 'E3.f1', 'E3.e2', 'T0', 'w0', 'w1']:
    a = ancestors(test)
    print(f'per-trial equations up to {test}: {len([x for x in a if x in dep])}  ->',
          ' '.join(x for _, x in order if x in a and x in dep))
print('\nsolving order (word <- other words of its equation); * = per trial')
for i, w in order:
    print(('* ' if w in dep else '  ') + f'{w:6s} <- ' + ' '.join(sorted(eqs[i][1] - {w})))
