"""Stage 2: pair / triangle search over the kernel-preserving (kp) transition variants of the 1,157 seed words.
A pair of directions (a, b) can sit in one 3-round affine field only if, on span{a,b}:
  chi1 input (exact, fixed per word), chi2 input (exact per variant), chi3 input (relaxed K/N per variant)
have no adjacent row positions whose forms are fixed, nonzero and different (common.conflict).
Each direction's real chi3-input difference is a single-direction trail, so it contains K and avoids N (sound).
Word level first (AND of K/N/A2 over a word's variants = weakest constraints), then variant level for survivors,
then triangles = three words with pairwise-compatible variants that agree (one variant per word).
Writes stage2.json."""
import time, json, itertools
import numpy as np
from common import *

t0 = time.time()
d = np.load(HERE + 'stage1_kp.npz'); S = json.load(open(HERE + 'stage1_stats.json'))
wid, tau, A2, K, N = d['wid'], d['tau'], d['A2'], d['K'], d['N']
words = [tuple(w) for w in S['words']]; nw = len(words)
starts = np.searchsorted(wid, np.arange(nw + 1))
A1 = np.concatenate([P(bits_to_lanes(w)) for w in words])
K3c = np.stack([np.bitwise_and.reduce(K[starts[i]:starts[i + 1]], axis=0) for i in range(nw)])
N3c = np.stack([np.bitwise_and.reduce(N[starts[i]:starts[i + 1]], axis=0) for i in range(nw)])
K2c = np.stack([np.bitwise_and.reduce(A2[starts[i]:starts[i + 1]], axis=0) for i in range(nw)])
N2c = np.stack([np.bitwise_and.reduce(~A2[starts[i]:starts[i + 1]], axis=0) for i in range(nw)])
print('loaded', nw, 'words', len(wid), 'variants; |K3c| min/median', int(popc(K3c).min()), int(np.median(popc(K3c))),
      round(time.time() - t0, 1), flush=True)

# word level
c1 = c2 = c3 = 0; surv = []
for a in range(nw - 1):
    b = np.arange(a + 1, nw)
    x1 = conflict(A1[a][None], ~A1[a][None], A1[b], ~A1[b])
    x2 = conflict(K2c[a][None], N2c[a][None], K2c[b], N2c[b])
    x3 = conflict(K3c[a][None], N3c[a][None], K3c[b], N3c[b])
    c1 += int(x1.sum()); c2 += int((~x1 & x2).sum()); c3 += int((~x1 & ~x2 & x3).sum())
    for j in b[~(x1 | x2 | x3)]: surv.append((a, int(j)))
npairs = nw * (nw - 1) // 2
print('word pairs', npairs, 'killed chi1', c1, 'chi2', c2, 'chi3', c3, 'survive', len(surv), round(time.time() - t0, 1), flush=True)

# stop-variant (tau=0) pair compatibility for comparison (exact at chi1/chi2 inputs; chi3 exact since chi2 identity)
stop_idx = np.array([starts[i] + int(np.nonzero(tau[starts[i]:starts[i + 1]] == 0)[0][0]) for i in range(nw)])

# variant level
vpairs = {}   # (a,b) -> array of (ia, ib) compatible variant index pairs (global indices)
nvp = 0; done_pairs = 0
for (a, b) in surv:
    if time.time() - t0 > 420:
        print('TIME GUARD: variant level stopped after', done_pairs, 'of', len(surv), 'word pairs', flush=True); break
    done_pairs += 1
    ia = np.arange(starts[a], starts[a + 1]); ib = np.arange(starts[b], starts[b + 1])
    ok = []
    for i in ia:
        x = conflict(A2[i][None], ~A2[i][None], A2[ib], ~A2[ib]) | conflict(K[i][None], N[i][None], K[ib], N[ib])
        for j in ib[~x]: ok.append((int(i), int(j)))
    if ok:
        vpairs[(a, b)] = ok; nvp += len(ok)
print('word pairs with a compatible variant pair', len(vpairs), 'variant pairs', nvp, round(time.time() - t0, 1), flush=True)

# triangles
adj = {}
for (a, b) in vpairs:
    adj.setdefault(a, set()).add(b); adj.setdefault(b, set()).add(a)
wtri = []
for (a, b) in vpairs:
    for c in adj[a] & adj[b]:
        if c > b: wtri.append((a, b, c))
print('word triangles (pairwise, any variants)', len(wtri), round(time.time() - t0, 1), flush=True)
vtri = []
for (a, b, c) in wtri:
    ab = {};
    for (i, j) in vpairs[(a, b)]: ab.setdefault(i, set()).add(j)
    ac = {}
    for (i, k) in vpairs[(a, c)]: ac.setdefault(i, set()).add(k)
    bc = set(vpairs[(b, c)])
    for i in set(ab) & set(ac):
        for j in ab[i]:
            for k in ac[i]:
                if (j, k) in bc: vtri.append((a, b, c, i, j, k))
print('variant triangles (one variant per word)', len(vtri), round(time.time() - t0, 1), flush=True)

stop_pairs = 0
for (a, b) in surv:
    i, j = stop_idx[a], stop_idx[b]
    if not (conflict(A2[i][None], ~A2[i][None], A2[j][None], ~A2[j][None])[0] or
            conflict(K[i][None], N[i][None], K[j][None], N[j][None])[0]): stop_pairs += 1
deg = np.zeros(nw, int)
for (a, b) in vpairs: deg[a] += 1; deg[b] += 1
out = {'words': nw, 'kp_variants': int(len(wid)), 'word_pairs': npairs, 'killed_chi1_exact': c1, 'killed_chi2_relaxed': c2,
       'killed_chi3_relaxed': c3, 'word_pairs_surviving_wordlevel': len(surv),
       'variant_level_pairs_done': done_pairs,
       'word_pairs_with_compatible_variants': len(vpairs), 'compatible_variant_pairs': nvp,
       'stop_variant_pairs_compatible_relaxed': stop_pairs, 'max_word_degree': int(deg.max()),
       'word_triangles': len(wtri), 'variant_triangles': len(vtri), 'variant_triangles_first20': vtri[:20],
       'secs': round(time.time() - t0, 1)}
json.dump({'summary': out, 'vpairs': {f'{a},{b}': v for (a, b), v in vpairs.items()}, 'vtri': vtri},
          open(HERE + 'stage2.json', 'w'))
print(json.dumps(out), flush=True)
