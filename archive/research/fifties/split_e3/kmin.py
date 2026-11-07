'''Least number k of 32-bit consistency (check) equations when E3's inputs are forced, census word model.
OUTER system (counter 1, trial words removed): F = {Y4, Y9, w8}; FULL system (outer + trial): F = {Y4, Y9, w8, Y14}.
Randomised greedy + minimisation (as pkg13/direct/mink.py), then: can the k checks be solved one word at a time
(sequential order: after free words + g1..gj, propagation has produced j checks, the j-th check new in gj)?'''

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

import random, sys, itertools
sys.dont_write_bytecode = True
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/catalogue/census'))
import model
TRIAL = {'E1.d1', 'E1.a1', 'Y6', 'Y10', 'Y14', 'E3.h1', 'E3.g1', 'E3.f1', 'E1.b1', 'Y2', 'w0', 'K0.a1', 'E3.e2',
         'E1.a2', 'w1', 'T0'}
def systems(counter=1):
    eqs, words = model.system(counter, False)
    full = [(n, frozenset(s)) for n, s in eqs]
    outer = [(n, s) for n, s in full if not s & TRIAL]
    return full, set(words), outer, set(words) - TRIAL
def propagate(eqs, known):
    known, used, changed, checks = set(known), set(), True, []
    while changed:
        changed = False
        for i, (_, s) in enumerate(eqs):
            if i in used: continue
            unk = [w for w in s if w not in known]
            if len(unk) == 1:
                known.add(unk[0]); used.add(i); changed = True
            elif not unk:
                used.add(i); checks.append(i); changed = True
    return known, checks
def greedy(eqs, words, F, rng):
    K = set(F)
    while True:
        kn, _ = propagate(eqs, K)
        if kn >= words: return K
        cand = sorted(words - kn)
        sc = [(len(propagate(eqs, kn | {w})[0]), rng.random(), w) for w in rng.sample(cand, min(len(cand), 25))]
        K.add(max(sc)[2])
def minimise(eqs, words, K, F):
    for w in sorted(K - set(F)):
        if propagate(eqs, K - {w})[0] >= words: K = K - {w}
    return K
def sequential(eqs, words, F, K, dof):
    '''Partitions of K-F into free B (dof-|F| words) and solved G (k words) with a sequential order.'''
    G0 = sorted(K - set(F)); k = len(K) - dof; out = []
    for Gs in itertools.combinations(G0, k):
        B = set(G0) - set(Gs)
        for perm in itertools.permutations(Gs):
            ok, prev = True, 0
            for j in range(1, k + 1):
                kn, ch = propagate(eqs, set(F) | B | set(perm[:j]))
                if len(ch) < j: ok = False; break
            if ok and propagate(eqs, set(F) | B | set(perm))[0] >= words:
                out.append((sorted(B), perm))
    return out
if __name__ == '__main__':
    tries = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    full, fw, outer, ow = systems(1)
    print('full: eqs %d words %d DOF %d ; outer: eqs %d words %d DOF %d' % (len(full), len(fw), len(fw) - len(full),
          len(outer), len(ow), len(ow) - len(outer)))
    for name, eqs, words, F in (('outer', outer, ow, ('Y4', 'Y9', 'w8')), ('full', full, fw, ('Y4', 'Y9', 'w8', 'Y14')),
                                ('outer', outer, ow, ('Y4', 'Y9')), ('outer', outer, ow, ('Y4', 'w8')),
                                ('full', full, fw, ('Y4', 'Y9', 'w8', 'E3.h1'))):
        dof = len(words) - len(eqs)
        rng = random.Random(5); best = None; allk = {}
        for _ in range(tries):
            K = minimise(eqs, words, greedy(eqs, words, F, rng), F)
            allk[len(K) - dof] = allk.get(len(K) - dof, 0) + 1
            if best is None or len(K) < len(best): best = K
        k = len(best) - dof
        print('%s F=%s DOF %d least k=%d (k histogram %s) guesses %s' % (name, '+'.join(F), dof, k, dict(sorted(allk.items())),
              sorted(best - set(F))))
        seq = sequential(eqs, words, F, best, dof)
        print('   sequential partitions:', len(seq), seq[:3])
