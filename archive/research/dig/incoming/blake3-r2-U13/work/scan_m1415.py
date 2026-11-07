import random, json
from b3lib import *
rng = random.Random(1415)
out = {}
def consts(A):
    sa, oa = compress_full(A, 55); X = sa['X']
    return (X[3], X[7], X[11], X[15]) == (X3, X7, X11, X15)
# Q1
N = 20000; nz = {14:0, 15:0}; dif = {14:0, 15:0}
for _ in range(N):
    d = build(*[rnd(rng) for _ in range(8)]); A, B = d['A'], d['B']
    for i in (14, 15):
        nz[i] += (A[i] != 0); dif[i] += (A[i] != B[i])
c = sum(consts(build(*[rnd(rng) for _ in range(8)])['A']) for _ in range(2000))
out['Q1'] = dict(N=N, A_nonzero=nz, AB_differ=dif, consts_hold=c, consts_trials=2000)
# Q2 necessity: nonzero value in B only, and nonzero in both
NN = 3000; res = {}
for idx, mask in ((14, M), (15, 0x00ffffff)):
    eqH = 0; nd = []; keep = 0; bothH = 0
    for _ in range(NN):
        d = build(*[rnd(rng) for _ in range(8)]); A, B = d['A'], d['B']
        sa, oa = compress_full(A, 55)
        for dl in (1 << rng.randrange(24), (rnd(rng) & mask) | 1):
            B2 = B[:]; B2[idx] ^= dl
            sb, ob = compress_full(B2, 63)
            eqH += all(oa[i] == ob[i] for i in (0, 2, 5, 7)); nd.append(sum(oa[i] != ob[i] for i in range(8)))
        v = (rnd(rng) & mask) | 1
        A2 = A[:]; A2[idx] = v; B2 = B[:]; B2[idx] = v
        keep += consts(A2)
        sa2, oa2 = compress_full(A2, 55); sb2, ob2 = compress_full(B2, 63)
        bothH += all(oa2[i] == ob2[i] for i in (0, 2, 5, 7))
    res['w%d' % idx] = dict(trials_B_only=2*NN, lemmaH_kept=eqH, mean_digest_words_differ=sum(nd)/len(nd), min_digest_words_differ=min(nd),
                            same_nonzero_both_blocks_consts_kept=keep, same_nonzero_both_lemmaH_kept=bothH, trials_both=NN)
out['Q2'] = res
# Q3: dof. A fixed 0 by length 55 (bytes 56..63 are padding); parameter sweeps show no dependence
dep = {}
for idx in (14, 15):
    s = set()
    for _ in range(50000):
        s.add(build(*[rnd(rng) for _ in range(8)])['A'][idx])
    dep['w%d' % idx] = sorted(s)
out['Q3_values_over_50000_builds'] = dep
# Q4: B-only nonzero with compensation by the other word (w14+x, w15 re-chosen) - lemma H check; and shifting w14 by dl, w15 by -dl
alt = dict(trials=0, lemmaH=0); wd = []
for _ in range(3000):
    d = build(*[rnd(rng) for _ in range(8)]); A, B = d['A'], d['B']
    oa = compress_full(A, 55)[1]
    dl = rnd(rng) | 1
    B2 = B[:]; B2[14] = dl; B2[15] = (-dl) & 0x00ffffff
    ob = compress_full(B2, 63)[1]
    alt['trials'] += 1; alt['lemmaH'] += all(oa[i] == ob[i] for i in (0, 2, 5, 7)); wd.append(sum(oa[i] != ob[i] for i in range(8)))
alt['mean_words_differ'] = sum(wd)/len(wd); alt['min_words_differ'] = min(wd)
out['Q4_alt'] = alt
json.dump(out, open('scan_m1415.out.json', 'w'), indent=1); print(json.dumps(out, indent=1))
