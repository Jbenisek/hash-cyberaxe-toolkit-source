import sys,random,collections
sys.path.insert(0,'.')
from b3ctr import *
R=random.Random(4242)
nm=['K0','K1','K2','K3','D0','D1','D2','D3','C0','C1','C2','C3','E0','E1','E2','E3']
def traces(w,ctr_lo,ctr_hi,n,fl=3):
    v=IV[:8]+IV[:4]+[ctr_lo,ctr_hi,n,fl]; s=list(w); out=[]
    for r in range(2):
        for i,(a,b,c,d) in enumerate(CALLS):
            G(v,a,b,c,d,s[2*i],s[2*i+1]); out.append(list(v))
        s=[s[p] for p in P]
    return out
# absorb a difference in state word v(12+k) by (m_2k, m_2k+1) in call Kk; round 0 must become identical
def route(k,N):
    stat=collections.Counter(); outdiff=collections.defaultdict(collections.Counter); eqwords=collections.Counter(); r0=0
    for _ in range(N):
        w=[R.getrandbits(32) for _ in range(16)]
        st=[R.getrandbits(32),R.getrandbits(32),R.getrandbits(32),R.getrandbits(32)]
        ctr=[st[0],st[1]]; n=55; fl=3
        v12,v13,v14,v15=st[0],st[1],55,3
        init=[v12,v13,v14,v15]
        newv=list(init)
        if k in (0,1): newv[k]=R.getrandbits(32)
        elif k==2: newv[2]=63
        a,b,c,d=CALLS[k]
        x,y=w[2*k],w[2*k+1]
        va=IV[:8]+IV[:4]+init
        a1=(va[a]+va[b]+x)&M; d1=ror(va[d]^a1,16)           # target d1 of A
        # B: want same d1 with d-input newv[k]
        a1p=rol(d1,16)^newv[k]; xp=(a1p-va[a]-va[b])&M
        yp=(y+a1-a1p)&M     # a2 = a1+b1+y  (b1 same since d1,c1 same)
        wb=list(w); wb[2*k]=xp; wb[2*k+1]=yp
        lo=lambda v:(v[0],v[1],v[2],v[3])
        ta=traces(w,init[0],init[1],init[2]); 
        initB=list(init); initB[k]=newv[k] if k<2 else newv[k]
        tb=traces(wb,initB[0],initB[1],initB[2])
        r0+= ta[7]==tb[7]
        if ta[7]!=tb[7]: continue
        # round 1: per call number of differing outputs (4 words), and equal digest words
        for ci in range(8,16):
            prev=ta[ci-1]; cur=ta[ci]; prevb=tb[ci-1]; curb=tb[ci]
            idx=CALLS[ci-8]
            nd=sum(cur[j]!=curb[j] for j in idx)
            outdiff[nm[ci]][nd]+=1
        oa=[ta[15][i]^ta[15][i+8] for i in range(8)]; ob=[tb[15][i]^tb[15][i+8] for i in range(8)]
        eqwords[sum(oa[i]==ob[i] for i in range(8))]+=1
    return r0,outdiff,eqwords
for k,name in ((0,'v12 counter-lo diff absorbed in K0 by (m0,m1)'),(1,'v13 counter-hi diff absorbed in K1 by (m2,m3)'),(2,'v14 length 55 vs 63 absorbed in K2 by (m4,m5) [control, random state, no pins]')):
    N=5000
    r0,od,eq=route(k,N)
    print("==",name)
    print(" round-0 state identical (Lemma L analogue):",r0,"/",N)
    print(" round-1 calls, number of the 4 outputs that differ (histogram):",{c:dict(sorted(v.items())) for c,v in od.items() if set(v)!={0}})
    print(" digest words equal (of 8) histogram:",dict(sorted(eq.items())))
