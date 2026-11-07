import random, json
from b3lib import *
rng = random.Random(909)
out = {}
sub = lambda *q: (q[0] - sum(q[1:])) & M
add = lambda *q: sum(q) & M
def lemma(oa, ob): return all(oa[i] == ob[i] for i in (0, 2, 5, 7))
def keeps(A, B, tag=None):
    sa, oa = compress_full(A, 55); sb, ob = compress_full(B, 63)
    X = sa['X']
    return dict(consts=(X[3],X[7],X[11],X[15])==(X3,X7,X11,X15), lemma=lemma(oa,ob),
                S=sa['S']==sb['S'], Xeq=sa['X']==sb['X'], Y4=sa['Y'][4], oa=oa, ob=ob)
# ---- Q1: difference and conditions count on w6,w7 as used
N = 20000
bc = {6:[0]*32, 7:[0]*32}; diffnz = 0; fixedpos = {6:0,7:0}
for _ in range(N):
    a = [rnd(rng) for _ in range(8)]
    d = build(*a); A, B = d['A'], d['B']
    if A[6] != B[6] or A[7] != B[7]: diffnz += 1
    for w in (6,7):
        for b in range(32): bc[w][b] += (A[w]>>b)&1
out['Q1'] = dict(N=N, A_vs_B_diff_nonzero=diffnz,
   differing_words_in_pair=[i for i in range(16) if True and False],
   max_bit_bias_w6=max(abs(c/N-0.5) for c in bc[6]), max_bit_bias_w7=max(abs(c/N-0.5) for c in bc[7]),
   bitcount_range_w6=[min(bc[6]),max(bc[6])], bitcount_range_w7=[min(bc[7]),max(bc[7])],
   fixed_bits_w6=sum(1 for c in bc[6] if c in (0,N)), fixed_bits_w7=sum(1 for c in bc[7] if c in (0,N)))
# ---- Q2: necessity: conditions on w6/w7 = the derived values from K3 inversion (X3,X7,X11,X15 hit + Lemma H + Y4)
NN = 3000
res = {}
for name, idx in (('w6',6),('w7',7)):
    r = dict(trials=0, same_change_A_B_consts_kept=0, same_change_A_B_lemmaH_kept=0, same_change_A_B_S_equal=0,
             B_only_lemmaH_kept=0, B_only_S_equal=0, unchanged_ctrl_lemmaH=0, mean_words_differ_B_only=0)
    nd = []
    for _ in range(NN):
        a = [rnd(rng) for _ in range(8)]
        d = build(*a); A, B = d['A'], d['B']
        r['trials'] += 1
        k0 = keeps(A,B)
        if k0['lemma'] and k0['consts']: r['unchanged_ctrl_lemmaH'] += 1
        dl = rnd(rng) | 1
        A2 = A[:]; B2 = B[:]; A2[idx] ^= dl; B2[idx] ^= dl
        k = keeps(A2,B2)
        r['same_change_A_B_consts_kept'] += k['consts']; r['same_change_A_B_lemmaH_kept'] += k['lemma']; r['same_change_A_B_S_equal'] += k['S']
        B3 = B[:]; B3[idx] ^= dl
        k = keeps(A,B3)
        r['B_only_lemmaH_kept'] += k['lemma']; r['B_only_S_equal'] += k['S']
        nd.append(sum(1 for i in range(8) if k['oa'][i] != k['ob'][i]))
    r['mean_words_differ_B_only'] = sum(nd)/len(nd)
    res[name] = r
out['Q2'] = res
# ---- Q3: degrees of freedom of (w6,w7)
def k3_fwd(w6, w7, n=55, flags=11):
    v = IV[:8]+IV[:4]+[0,0,n,flags]
    G(v,3,7,11,15,w6,w7); return v[3],v[7],v[11],v[15]
def k3_inv(S3,S15):   # state after K3 -> (w6,w7) given S3,S15 (S7,S11 follow); uses K3 inversion
    K3d1 = rol(S15,8)^S3; K3c1 = add(IV[3],K3d1); K3b1 = ror(IV[7]^K3c1,12)
    K3a1 = rol(K3d1,16)^11
    return sub(K3a1,IV[3],IV[7]), sub(S3,K3a1,K3b1)
rt1=rt2=0; M1=200000
for _ in range(M1):
    w6,w7 = rnd(rng),rnd(rng)
    S3,S7,S11,S15 = k3_fwd(w6,w7)
    if k3_inv(S3,S15)==(w6,w7): rt1+=1
    S3,S15 = rnd(rng),rnd(rng); a,b = k3_inv(S3,S15); r_=k3_fwd(a,b)
    if (r_[0],r_[3])==(S3,S15): rt2+=1
out['Q3_k3_roundtrip'] = dict(trials=M1, fwd_inv_ok=rt1, inv_fwd_ok=rt2)
# dependence on each of the 8 free parameters
names = ['C0c1','C0d1','D3d1','S15','S9','w5','X2','y']
dep = {n:[0,0,0] for n in names}   # changed w6, changed w7, trials
for _ in range(2000):
    a = [rnd(rng) for _ in range(8)]; d0 = build(*a)
    for i,n in enumerate(names):
        a2 = a[:]; a2[i] = rnd(rng); d1 = build(*a2)
        dep[n][0] += d0['A'][6]!=d1['A'][6]; dep[n][1] += d0['A'][7]!=d1['A'][7]; dep[n][2]+=1
out['Q3_dependence'] = dep
# sweeps: w6 over S15 (all 2^22 values bijective?) and pair surjectivity by solving for S15,S9
import numpy as np
base = [rnd(rng) for _ in range(8)]
ws6=set(); ws7=set()
for s in range(1<<16):
    a = base[:]; a[3] = s*65537 & M if False else rng.getrandbits(32)
    d = build(*a); ws6.add(d['A'][6]); ws7.add(d['A'][7])
out['Q3_S15_sweep'] = dict(n=1<<16, distinct_w6=len(ws6), distinct_w7=len(ws7))
def solve_for_w67(w6t,w7t):
    C0c1,C0d1,D3d1,w5,X2,y = [rnd(rng) for _ in range(6)]
    S3t,S15 = None,None
    K3a1 = add(w6t,IV[3],IV[7]); K3d1 = ror(K3a1^11,16); K3c1 = add(IV[3],K3d1); K3b1 = ror(IV[7]^K3c1,12)
    S3t = add(w7t,K3a1,K3b1); S15 = ror(K3d1^S3t,8)
    K2a1 = add(IV[2],IV[6],W4); K2d1 = ror(55^K2a1,16)
    S2 = add(K2a1, ror(IV[6]^add(IV[2],K2d1),12), w5); S14 = ror(K2d1^S2,8)
    D3a1 = rol(D3d1,16)^S14; D3b1 = sub(X3,D3a1)
    S4 = sub(D3a1,S3t); D3c1 = rol(D3b1,12)^S4; S9 = sub(D3c1,D3d1)
    return [C0c1,C0d1,D3d1,S15,S9,w5,X2,y]
hit=0; T=20000; allok=0
for _ in range(T):
    w6t,w7t = rnd(rng),rnd(rng)
    d = build(*solve_for_w67(w6t,w7t)); A,B=d['A'],d['B']
    if A[6]==w6t and A[7]==w7t: hit+=1
    sa,oa = compress_full(A,55); sb,ob = compress_full(B,63); X=sa['X']
    if A[6]==w6t and A[7]==w7t and (X[3],X[7],X[11],X[15])==(X3,X7,X11,X15) and lemma(oa,ob): allok+=1
out['Q3_surjective_targets'] = dict(trials=T, pair_hit=hit, pair_hit_with_consts_and_lemmaH=allok)
# ---- Q4: alternatives: other signed/modular differences placed on w6/w7 in B (same constraint)
alt = dict(trials=0, S_equal=0, lemmaH=0, K3_state_equal=0)
dist = []
for _ in range(3000):
    a = [rnd(rng) for _ in range(8)]; d = build(*a); A,B = d['A'],d['B']
    dl = rnd(rng)|1; ep = rnd(rng)
    kind = _ % 4
    B2 = B[:]
    if kind==0: B2[6] = (B[6]+dl)&M
    elif kind==1: B2[7] = (B[7]+dl)&M
    elif kind==2: B2[6] = (B[6]+dl)&M; B2[7] = (B[7]-dl)&M       # sum-preserving
    else: B2[6] = (B[6]+dl)&M; B2[7] = (B[7]+ep)&M
    sa,oa = compress_full(A,55); sb,ob = compress_full(B2,63)
    alt['trials']+=1
    alt['S_equal'] += sa['S']==sb['S']; alt['lemmaH'] += lemma(oa,ob)
    alt['K3_state_equal'] += [sa['S'][i] for i in (3,7,11,15)]==[sb['S'][i] for i in (3,7,11,15)]
out['Q4_alt_diff_on_w6_w7'] = alt
# bijectivity of first/second a-step: exhaustive-ish: K3 output state injective in (w6,w7)
seen = {}
coll = 0
for _ in range(300000):
    w6,w7 = rnd(rng),rnd(rng); s = k3_fwd(w6,w7)
    if s in seen and seen[s]!=(w6,w7): coll+=1
    seen[s]=(w6,w7)
out['Q4_K3_injective_check'] = dict(samples=300000, collisions=coll)
json.dump(out, open('scan_m67.out.json','w'), indent=1)
print(json.dumps(out, indent=1))
