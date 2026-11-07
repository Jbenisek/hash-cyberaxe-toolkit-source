"""stage6 completed with a translation cache. Pattern-level checks (chi1 constant clash, z3 common chi2 constants,
chi3 row test) commute with z-rotation (theta, rho, pi, chi all commute with it), so the verdict for a pair/triple of
(word, chi1-output pattern) depends only on its class under simultaneous translation. Each six-bit word w is
T^{s_w}(canonical rep); each variant is identified by its chi1-output pattern translated back to the rep.
Native checks (padding, rate boundary) are NOT translation-invariant and are run per concrete triple if any is SAT.
Usage: python stage6b.py MAXSECS"""
import sys, time, json
import numpy as np
from exact import *

maxsecs = float(sys.argv[1]) if len(sys.argv) > 1 else 500
t0 = time.time()
S = json.load(open(HERE + 'stage1_stats.json')); words = [tuple(w) for w in S['words']]
d = np.load(HERE + 'stage1_kp.npz'); wid, tau, A2, K, N = d['wid'], d['tau'], d['A2'], d['K'], d['N']
starts = np.searchsorted(wid, np.arange(len(words) + 1))
six = [i for i, w in enumerate(words) if len(w) == 6]
tr = lambda bits, t: tuple(sorted(64 * (b // 64) + (b % 64 + t) % 64 for b in bits))
cls = {}; tstar = {}; reps = {}
for w in six:
    best = min((tr(words[w], t), t) for t in range(64))
    reps.setdefault(best[0], len(reps)); cls[w] = reps[best[0]]; tstar[w] = best[1]
vid = {}; vdict = {}
for w in six:
    for i in range(starts[w], starts[w + 1]):
        _, b1, _ = chi1_choice(words[w], int(tau[i]))
        key = (cls[w], tr([int(x) for x in np.nonzero(b1)[0]], tstar[w]))
        vdict.setdefault(key, len(vdict)); vid[i] = vdict[key]
print('classes', len(reps), 'class sizes', np.bincount(list(cls.values())).tolist(), 'canonical variants', len(vdict),
      round(time.time() - t0, 1), flush=True)

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
print('relaxed word pairs', len(rel), 'relaxed variant pairs', nrel, round(time.time() - t0, 1), flush=True)

def pkey(items):  # items: list of (word, variant index); first item fixes the frame
    w0 = items[0][0]
    return tuple((cls[w], vid[i], (tstar[w0] - tstar[w]) % 64) for (w, i) in items)

def exact_ok(items):
    ch = [chi1_choice(words[w], int(tau[i])) for (w, i) in items]
    merged = {}
    for (_, _, pr) in ch:
        for q, v in pr.items():
            if merged.get(q, v) != v: return 'chi1 clash', None, ch
            merged[q] = v
    stt, sol = pattern_z3([ls.Pb(b1)[0] for (_, b1, _) in ch], timeout_ms=10000)
    return stt, sol, ch

cache = {}; pstat = {}; ex = {}; complete = True; uniq = 0
for (a, b), lst in rel.items():
    for (i, j) in lst:
        k = pkey([(a, i), (b, j)])
        if k not in cache:
            if time.time() - t0 > maxsecs * 0.8: complete = False; break
            cache[k] = exact_ok([(a, i), (b, j)])[0]; uniq += 1
        stt = cache[k]; pstat[stt] = pstat.get(stt, 0) + 1
        if stt == 'sat': ex.setdefault((a, b), []).append((i, j))
    if not complete: break
nex = sum(len(v) for v in ex.values())
print('unique exact pair checks', uniq, 'pairs resolved', sum(pstat.values()), 'of', nrel, pstat, 'exact word pairs', len(ex),
      'exact variant pairs', nex, 'complete', complete, round(time.time() - t0, 1), flush=True)

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
wtri = {t[:3] for t in tri}
print('word triangles in exact-pair graph', len(wtri), 'variant triangles', len(tri), round(time.time() - t0, 1), flush=True)
tcache = {}; tstat = {}; found = []
for (a, b, c, i, j, k) in tri:
    if time.time() - t0 > maxsecs: complete = False; break
    key = pkey([(a, i), (b, j), (c, k)])
    if key not in tcache: tcache[key] = exact_ok([(a, i), (b, j), (c, k)])
    stt, sol, ch = tcache[key]
    tstat[stt] = tstat.get(stt, 0) + 1
    if stt == 'sat':
        ok, info, st, Vi = native([words[a], words[b], words[c]], [pr for (_, _, pr) in ch], sol)
        nk = 'native_' + ('ok' if ok else str(info)); tstat[nk] = tstat.get(nk, 0) + 1
        if ok:
            found.append([a, b, c, i, j, k])
            json.dump({'words': [list(words[w]) for w in (a, b, c)], 'pref1': [{str(q): v for q, v in pr.items()} for (_, _, pr) in ch],
                       'pref2': {str(q): v for q, v in sol.items()}, 'rows': [[hex(R), v] for (R, v) in st.rows]},
                      open(HERE + 'found6_rank3_%d.json' % len(found), 'w'))
            break
deg = [len(adj.get(w, ())) for w in six]
out = {'six_words': len(six), 'classes': len(reps), 'word_pairs': len(six) * (len(six) - 1) // 2, 'relaxed_word_pairs': len(rel),
       'relaxed_variant_pairs': nrel, 'unique_exact_pair_checks': uniq, 'pair_outcomes': pstat,
       'exact_word_pairs': len(ex), 'exact_variant_pairs': nex, 'max_exact_word_degree': max(deg),
       'exact_word_pairs_list': sorted([list(k) for k in ex]), 'word_triangles': len(wtri), 'variant_triangles': len(tri),
       'unique_triangle_checks': len(tcache), 'triangle_outcomes': tstat, 'rank3_found': found, 'complete': complete,
       'secs': round(time.time() - t0, 1)}
print(json.dumps(out), flush=True)
json.dump({'summary': out, 'exact_pairs': {f'{a},{b}': v for (a, b), v in ex.items()}}, open(HERE + 'stage6b.json', 'w'))
