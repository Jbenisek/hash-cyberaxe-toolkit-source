"""Complete run on the sparsest sub-family: the 120 six-bit seed words, all 64 kernel-preserving chi1 variants each,
free chi2 (relaxed, then exact). Steps: relaxed variant-pair graph over ALL 7,140 word pairs (chi1 exact, chi2 exact
input test, chi3 K/N) -> exact pairwise check (chi1 constant clash + z3 common chi2 constants, nd=2) on every relaxed
variant pair -> triangles of exact pairs with one variant per word -> exact triple check (z3, nd=3) -> native.
Time-capped; prints coverage. Usage: python stage6.py MAXSECS"""
import sys, time, json, itertools
import numpy as np
from exact import *

maxsecs = float(sys.argv[1]) if len(sys.argv) > 1 else 470
t0 = time.time()
S = json.load(open(HERE + 'stage1_stats.json')); words = [tuple(w) for w in S['words']]
d = np.load(HERE + 'stage1_kp.npz'); wid, tau, A2, K, N = d['wid'], d['tau'], d['A2'], d['K'], d['N']
starts = np.searchsorted(wid, np.arange(len(words) + 1))
six = [i for i, w in enumerate(words) if len(w) == 6]
A1 = {i: P(bits_to_lanes(words[i]))[0] for i in six}
rel = {}
for x, a in enumerate(six):
    for b in six[x + 1:]:
        if conflict(A1[a][None], ~A1[a][None], A1[b][None], ~A1[b][None])[0]: continue
        ia = np.arange(starts[a], starts[a + 1]); ib = np.arange(starts[b], starts[b + 1])
        X = (conflict(A2[ia][:, None], ~A2[ia][:, None], A2[ib][None], ~A2[ib][None]) |
             conflict(K[ia][:, None], N[ia][:, None], K[ib][None], N[ib][None]))
        ii, jj = np.nonzero(~X)
        if len(ii): rel[(a, b)] = [(int(ia[p]), int(ib[q])) for p, q in zip(ii, jj)]
nrel = sum(len(v) for v in rel.values())
print('six-bit words', len(six), 'word pairs', len(six) * (len(six) - 1) // 2, 'relaxed word pairs', len(rel),
      'relaxed variant pairs', nrel, round(time.time() - t0, 1), flush=True)

chcache = {}
def ch_of(w, i):
    if i not in chcache: chcache[i] = chi1_choice(words[w], int(tau[i]))
    return chcache[i]
def exact_ok(items):
    ch = [ch_of(w, i) for (w, i) in items]
    merged = {}
    for (_, _, pr) in ch:
        for q, v in pr.items():
            if merged.get(q, v) != v: return 'chi1 clash', None, ch
            merged[q] = v
    stt, sol = pattern_z3([ls.Pb(b1)[0] for (_, b1, _) in ch], timeout_ms=10000)
    return stt, sol, ch

ex = {}; pstat = {}; done = 0; complete = True
for (a, b), lst in rel.items():
    for (i, j) in lst:
        if time.time() - t0 > maxsecs * 0.75: complete = False; break
        stt, _, _ = exact_ok([(a, i), (b, j)]); done += 1
        pstat[stt] = pstat.get(stt, 0) + 1
        if stt == 'sat': ex.setdefault((a, b), []).append((i, j))
    if not complete: break
nex = sum(len(v) for v in ex.values())
print('exact pair checks', done, 'of', nrel, pstat, 'exact word pairs', len(ex), 'exact variant pairs', nex,
      round(time.time() - t0, 1), flush=True)

adj = {}
for (a, b) in ex: adj.setdefault(a, set()).add(b); adj.setdefault(b, set()).add(a)
tri = []
for (a, b) in ex:
    for c in adj[a] & adj[b]:
        if c <= b: continue
        ab = {}; [ab.setdefault(i, set()).add(j) for (i, j) in ex[(a, b)]]
        ac = {}; [ac.setdefault(i, set()).add(k) for (i, k) in ex[(a, c)]]
        bc = set(ex[(b, c)])
        for i in set(ab) & set(ac):
            for j in ab[i]:
                for k in ac[i]:
                    if (j, k) in bc: tri.append((a, b, c, i, j, k))
print('word triangles in exact-pair graph', len({t[:3] for t in tri}), 'variant triangles', len(tri), round(time.time() - t0, 1), flush=True)
tstat = {}; found = []; tdone = 0
for (a, b, c, i, j, k) in tri:
    if time.time() - t0 > maxsecs: complete = False; break
    stt, sol, ch = exact_ok([(a, i), (b, j), (c, k)]); tdone += 1
    tstat[stt] = tstat.get(stt, 0) + 1
    if stt == 'sat':
        ok, info, st, Vi = native([words[a], words[b], words[c]], [pr for (_, _, pr) in ch], sol)
        tstat['native_' + ('ok' if ok else str(info))] = tstat.get('native_' + ('ok' if ok else str(info)), 0) + 1
        if ok:
            found.append([a, b, c, i, j, k])
            json.dump({'words': [list(words[w]) for w in (a, b, c)], 'pref1': [{str(q): v for q, v in pr.items()} for (_, _, pr) in ch],
                       'pref2': {str(q): v for q, v in sol.items()}, 'rows': [[hex(R), v] for (R, v) in st.rows]},
                      open(HERE + 'found6_rank3_%d.json' % len(found), 'w'))
            break
deg = [len(adj.get(w, ())) for w in six]
out = {'six_words': len(six), 'word_pairs': len(six) * (len(six) - 1) // 2, 'relaxed_word_pairs': len(rel),
       'relaxed_variant_pairs': nrel, 'exact_pair_checks_done': done, 'exact_pair_outcomes': pstat,
       'exact_word_pairs': len(ex), 'exact_variant_pairs': nex, 'max_exact_word_degree': max(deg),
       'variant_triangles': len(tri), 'triangle_checks_done': tdone, 'triangle_outcomes': tstat,
       'rank3_found': found, 'complete': complete, 'secs': round(time.time() - t0, 1)}
print(json.dumps(out), flush=True)
json.dump({'summary': out, 'exact_pairs': {f'{a},{b}': v for (a, b), v in ex.items()}}, open(HERE + 'stage6.json', 'w'))
