"""t1_cone.py: words that move when v13 (T1) is varied per trial, in the counter arrangement's basis plus T1.
Own model (copy of counter/structure/model.py) via knobs_model.system('ctr2')."""
import sys
sys.dont_write_bytecode = True
import model as M
import knobs_model as K

eqs, words = K.system('ctr2')
outer8 = ['C0.c1', 'C0.d1', 'D3.d1', 'S15', 'S9', 'w5', 'X2', 'Y4']
for inner in (['T1'], ['E1.d1', 'T1']):
    B = set(outer8) | set(inner) | ({'E1.d1'} if 'E1.d1' not in inner else set())
    ok, order, checks = M.propagate(eqs, B)
    print(f'basis outer8 + E1.d1 + T1: triangular {ok}, checks {checks}')
    dep = {'T1'}
    for i, w in order:
        if w is not None and any(u in dep for u in eqs[i][1] if u != w):
            dep.add(w)
    print(f'words that move with T1 ({len(dep)}):', ' '.join(sorted(dep)))
    print('  Y4 moves with T1:', 'Y4' in dep, '(Y4 is a basis word here, so it cannot move: see below)')
    break
# Y4 is in the basis above, so T1's change must be absorbed elsewhere.  Show what absorbs it in round 0/1:
for w in ('w2', 'w3', 'K1.a1', 'X0', 'X4', 'X8', 'X12', 'C0.a1', 'C0.b1', 'Y0', 'Y8', 'Y12', 'Y1', 'Y9', 'w8',
          'S0', 'S1', 'S5', 'S9', 'S13', 'X15'):
    print(f'  {w:6s} moves with T1: {w in dep}')
