import random, json
from b3lib import *
rng = random.Random(8989)
out = {}
sub = lambda *q: (q[0] - sum(q[1:])) & M
add = lambda *q: sum(q) & M
def constsok(A):
    sa, oa = compress_full(A, 55); X = sa['X']
    return (X[3], X[7], X[11], X[15]) == (X3, X7, X11, X15), sa
# Q1
N = 20000; bc8=[0]*32; bc9=[0]*32; diffA=0; eq89=0; xorfail=0; cond=0
for _ in range(N):
    a=[rnd(rng) for _ in range(8)]; d=build(*a); A,B=d['A'],d['B']
    if A[8]!=B[8] or A[9]!=B[9]: diffA+=1
    if A[8]==A[9]: eq89+=1
    for b in range(32): bc8[b]+=(A[8]>>b)&1; bc9[b]+=(A[9]>>b)&1
for _ in range(2000):
    a=[rnd(rng) for _ in range(8)]; d=build(*a); ok,sa=constsok(d['A']); cond+=ok
out['Q1']=dict(N=N,blocks_where_AB_differ_in_w8_or_w9=diffA,diff_bits=0,max_bit_bias_w8=max(abs(c/N-.5) for c in bc8),
  max_bit_bias_w9=max(abs(c/N-.5) for c in bc9),w8_eq_w9=eq89,pinned_conditions_on_this_word='X15 and X0 of col G(0,5,10,15) (2x32 bits) fix (w8,w9) uniquely',
  consts_hold_trials=2000,consts_hold=cond)
# Q2 necessity
NN=3000; res={}
for name,idx in (('w8',8),('w9',9)):
    eqH=0; nd=[]; keepA=0; keepA_cnt=0; stateeq=0
    for _ in range(NN):
        a=[rnd(rng) for _ in range(8)]; d=build(*a); A,B=d['A'],d['B']
        sa,oa=compress_full(A,55)
        for dl in (1<<rng.randrange(32), rnd(rng)|1):
            B2=B[:]; B2[idx]^=dl
            sb,ob=compress_full(B2,63)
            if all(oa[i]==ob[i] for i in (0,2,5,7)): eqH+=1
            nd.append(sum(1 for i in range(8) if oa[i]!=ob[i]))
            if sa['X']==sb['X']: stateeq+=1
        A2=A[:]; A2[idx]^=(rnd(rng)|1)
        ok,_=constsok(A2); keepA+=ok
    res[name]=dict(trials_diff_in_B_only=2*NN,lemmaH_events_kept=eqH,round1_state_X_equal=stateeq,mean_digest_words_differing=sum(nd)/len(nd),
      min_digest_words_differing=min(nd),value_changed_keep_admissible=keepA,value_changed_trials=NN)
out['Q2']=res
# Q3 dof
def d0(a): # returns pieces needed: S0,S5,S10,S15,X15,X0
    pass
# bijection (w8,w9)->(X0,X15) with context from a build: solve by inversion and check
def ctx(a):
    d=build(*a); A=d['A']; sa,_=compress_full(A,55); return d,A,sa
ok_inv=0; T=20000; uniq=0
for _ in range(T):
    a=[rnd(rng) for _ in range(8)]; d,A,sa=ctx(a)
    S=sa['S']; X=sa['X']
    # col G(0,5,10,15,w8,w9): inputs after first half v0=S0,v5=S5,v10=S10,v15=S15; outputs X0,X15
    a1=A[8]; # verify forward
    v=S[:]; G(v,0,5,10,15,A[8],A[9])
    assert v[0]==X[0] and v[15]==X[15]
    # invert from (X0,X15)
    d2=X[15]; a2=X[0]; d1=rol(d2,8)^a2; a1_=rol(d1,16)^S[15]; w8=sub(a1_,S[0],S[5])
    c1=add(S[10],d1); b1=ror(S[5]^c1,12); w9=sub(a2,a1_,b1)
    if (w8,w9)==(A[8],A[9]): ok_inv+=1
out['Q3_pair_bijection']=dict(trials=T,inverse_recovers_w8_w9=ok_inv,meaning='given round-1 half-state and pinned X0,X15, (w8,w9) is unique: 64 bits fixed by 64 bits of conditions, 0 dof left in this word pair')
# dependence of w8,w9 on the 8 free params, with distinct counts over 2^16 sweeps
names=['C0c1','C0d1','D3d1','S15','S9','w5','X2','y']
dep={}
for k,nm in enumerate(names):
    base=[rnd(rng) for _ in range(8)]
    ch8=ch9=0; s8=set(); s9=set(); sp=set(); L=1<<16
    b0=build(*base)['A']
    for t in range(L):
        a=base[:]; a[k]=rng.getrandbits(32) if t else a[k]
        A=build(*a)['A']; s8.add(A[8]); s9.add(A[9]); sp.add((A[8],A[9]))
    dep[nm]=dict(samples=L,distinct_w8=len(s8),distinct_w9=len(s9),distinct_pair=len(sp))
out['Q3_param_sweeps']=dep
# total dof: rank check - pair map from all 8 params, distinct pairs over random
sp=set(); L=100000
for _ in range(L):
    A=build(*[rnd(rng) for _ in range(8)])['A']; sp.add((A[8],A[9]))
out['Q3_random_pairs']=dict(samples=L,distinct_pairs=len(sp))
# Q4 alternatives: in B change w8 by dl and fix w9 to keep a2 (X0); or keep X15 (d2)
alt=dict(trials=0,X0_kept_X15_kept=0,X0_kept_only=0,X15_kept_only=0,lemmaH_kept=0,X5_kept=0,X10_kept=0); wd=[]
for _ in range(3000):
    a=[rnd(rng) for _ in range(8)]; d,A,sa=ctx(a); B=d['B']; S=sa['S']; X=sa['X']
    sa_,oa=sa,compress_full(A,55)[1]
    dl=rnd(rng)|1
    B2=B[:]; B2[8]=(B[8]+dl)&M
    # keep a2: w9' = a2 - a1' - b1'
    a1=add(S[0],S[5],B2[8]); d1=ror(S[15]^a1,16); c1=add(S[10],d1); b1=ror(S[5]^c1,12)
    B2[9]=sub(X[0],a1,b1)
    sb,ob=compress_full(B2,63); Xb=sb['X']
    k0=Xb[0]==X[0]; k15=Xb[15]==X[15]
    alt['trials']+=1
    alt['X0_kept_X15_kept']+=k0 and k15; alt['X0_kept_only']+=k0 and not k15; alt['X15_kept_only']+=k15 and not k0
    alt['X5_kept']+=Xb[5]==X[5]; alt['X10_kept']+=Xb[10]==X[10]
    if all(oa[i]==ob[i] for i in (0,2,5,7)): alt['lemmaH_kept']+=1
    wd.append(sum(1 for i in range(8) if oa[i]!=ob[i]))
alt['mean_words_differ']=sum(wd)/len(wd); alt['min_words_differ']=min(wd)
out['Q4_compensated_w8w9_alt']=alt
json.dump(out,open('scan_m89.out.json','w'),indent=1); print(json.dumps(out,indent=1))
