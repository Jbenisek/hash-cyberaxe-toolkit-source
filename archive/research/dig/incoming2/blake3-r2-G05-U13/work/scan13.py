# G05-U13: role of the message word at each of 20 reads (K0..K3,D0..D3 round 0; C0,C1 round 1), counter construction (pkgB3U Sec 8)
import random, json, sys
from b3ctr import *
rng = random.Random(1305)
CALLN = ['K0','K1','K2','K3','D0','D1','D2','D3']
def comp2(w, t, n, ov0=None, ov1=None, flags=3):
    v = IV[:8]+IV[:4]+[t&M, t>>32, n, flags]
    s = list(w); X = None; ins = {}; outs = {}
    for r in range(2):
        if r == 1: s = [s[p] for p in P]
        ov = ov0 if r == 0 else ov1
        if ov:
            for k, d in ov.items(): s[k] ^= d
        for i, (a,b,c,d) in enumerate(CALLS):
            ins[(r,i)] = (v[a],v[b],v[c],v[d])
            G(v,a,b,c,d,s[2*i],s[2*i+1])
            outs[(r,i)] = (v[a],v[b],v[c],v[d])
        if r == 0: X = list(v)
    o = [v[i]^v[i+8] for i in range(8)]
    return o, X, ins, outs, s
def pair(f, ov0=None, ov1=None):
    w, t, _ = build(f); wa, wb = messages(w, t)
    return w, t, wa, wb
N = 2000
# word -> reads
cells = []
for i in range(16):
    r0 = ('r0', i//2, i%2)           # call index in round 0, x/y
    cells.append(i)
rd0 = {i: (CALLN[i//2], 'xy'[i%2]) for i in range(16)}
rd1names = ['C0','C1','C2','C3','E0','E1','E2','E3']
rd1 = {P[p]: (rd1names[p//2], 'xy'[p%2], p) for p in range(16)}
res = {}
# stats over builds
samples = []
for _ in range(N):
    f = rnd_free(rng); w, t, wa, wb = pair(f)
    oa, Xa, ia, oua, sa = comp2(wa, t, 55); ob, Xb, ib, oub, sb = comp2(wb, t, 63)
    samples.append((f, wa, wb, t, ia, ib, oua, oub, oa, ob))
def stat_word(i):
    vals = set(); eqAB = 0; popc = []; zero = 0
    for (f, wa, wb, t, ia, ib, oua, oub, oa, ob) in samples:
        vals.add(wa[i])
        if wa[i] == wb[i]: eqAB += 1
        else: popc.append(bin(wa[i]^wb[i]).count('1'))
    return dict(distinct=len(vals), eqAB=eqAB, diff_popcount_mean=(sum(popc)/len(popc) if popc else 0), diff_popcount_min=min(popc) if popc else 0, diff_popcount_max=max(popc) if popc else 0)
def stat_call(r, ci):
    inEq = outEq = 0; outWords = 0
    for (f, wa, wb, t, ia, ib, oua, oub, oa, ob) in samples:
        inEq += ia[(r,ci)] == ib[(r,ci)]; outEq += oua[(r,ci)] == oub[(r,ci)]
        outWords += sum(1 for k in range(4) if oua[(r,ci)][k] == oub[(r,ci)][k])
    return dict(call_input_state_equal_AB=inEq, call_output_equal_AB=outEq, output_words_equal_mean=outWords/N)
# per-use perturbation
NP = 600
def perturb(i, rnd_):   # rnd_ 0 or 1; position
    pos = i if rnd_ == 0 else rd1[i][2]
    keep = Heq = Xeq = 0; dwa = 0; dwab = 0; Ssame_pins = 0; tot = 0
    for k in range(NP):
        f, wa, wb, t, ia, ib, oua, oub, oa, ob = samples[k]
        d = rng.getrandbits(32) | 1
        ov = {pos: d}
        o1, X1, *_ = comp2(wa, t, 55, ov0=ov if rnd_==0 else None, ov1=ov if rnd_==1 else None)
        o2, X2, *_ = comp2(wb, t, 63, ov0=ov if rnd_==0 else None, ov1=ov if rnd_==1 else None)
        tot += 1
        keep += (X1[3],X1[7],X1[11],X1[15]) == (X3,X7,X11,X15)
        Xeq += X1 == X2
        Heq += all(o1[j]==o2[j] for j in (0,2,5,7))
        dwa += sum(1 for j in range(8) if o1[j] != oa[j])
        dwab += sum(1 for j in range(8) if o1[j] != o2[j])
    return dict(trials=tot, pins_X3_X7_X11_X15_kept=keep, X_equal_AB=Xeq, lemmaH_kept=Heq, digest_words_changed_vs_unperturbed_mean=dwa/tot, digest_words_AB_differ_mean=dwab/tot)
# dependence on the 10 free params
FR = FREE
def dependence(i):
    dep = {}
    for k in FR:
        ch = 0; T = 30
        for _ in range(T):
            f = rnd_free(rng); w, t, _ = build(f); g = dict(f)
            g[k] = (g[k] ^ (1 << rng.randrange(16 if k=='t_hi' else 32))) if k != 't_hi' else (g[k] ^ (1 << rng.randrange(16)))
            w2, t2, _ = build(g)
            ch += w2[i] != w[i]
        dep[k] = ch/T
    return dep
for i in range(16):
    res[i] = dict(word=stat_word(i), dep=dependence(i))
# round-1 reading gives which round1 call pair; per-use
for i in range(16):
    res[i]['use0'] = dict(call=rd0[i], pert=perturb(i, 0), callstat=stat_call(0, i//2))
    p = rd1[i][2]
    res[i]['use1'] = dict(call=rd1[i][:2], pert=perturb(i, 1), callstat=stat_call(1, p//2))
    print('done', i, flush=True)
json.dump(res, open('scan13.out.json', 'w'), indent=1)
