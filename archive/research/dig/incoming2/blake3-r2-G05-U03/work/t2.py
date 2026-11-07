import sys,random,math,collections
sys.path.insert(0,'.')
from b3ctr import *
R=random.Random(77)
def rf(hi):
    f=rnd_free(R,1); f['t_hi']=hi
    f['c1']=(R.getrandbits(32)&~0x0e09818b&M)|0x02008000
    e1=(R.getrandbits(32)&~0x03cf8303&M)|0x030c0303
    f['Y4']=(e1-Y3)&M
    return f
def traces(w,t,n):
    v=IV[:8]+IV[:4]+[t&M,t>>32,n,3]; s=list(w); out=[]
    for r in range(2):
        for i,(a,b,c,d) in enumerate(CALLS):
            G(v,a,b,c,d,s[2*i],s[2*i+1]); out.append(list(v))
        s=[s[p] for p in P]
    return out
def e1b(tr,w):  # E1 = call index 13, inputs v1,v6,v11,v12 as of after call 12
    v=tr[12]; a,b,c,d=v[1],v[6],v[11],v[12]
    a1=(a+b+w[12])&M; d1=ror(d^a1,16); c1=(c+d1)&M; b1=ror(b^c1,12); return b1
def e3d(tr,w):  # E3 = call 15 inputs v3,v4,v9,v14 after call 14
    v=tr[14]; a,b,c,d=v[3],v[4],v[9],v[14]
    a1=(a+b+w[15])&M; d1=ror(d^a1,16); return d1
def hw(x): return bin(x).count('1')
N=4000
res={}
for name,hifn in (('t_hi=0',lambda:0),('t_hi random 32',lambda:R.getrandbits(32))):
    beta=collections.Counter(); eta=collections.Counter(); wt=[]; ok=0; Rw=[0]*4
    for _ in range(N):
        f=rf(hifn()); w,t,L=build(f); wa,wb=messages(w,t)
        ta=traces(wa,t,55); tb=traces(wb,t,63)
        oa=[ta[15][i]^ta[15][i+8] for i in range(8)]; ob=[tb[15][i]^tb[15][i+8] for i in range(8)]
        beta[e1b(ta,wa)^e1b(tb,wb)]+=1; eta[e3d(ta,wa)^e3d(tb,wb)]+=1
        ok+= all(oa[i]==ob[i] for i in (0,2,5,7))
        wt.append(sum(hw(oa[i]^ob[i]) for i in (1,3,4,6)))
    m=sum(wt)/N; sd=(sum((x-m)**2 for x in wt)/(N-1))**.5
    res[name]=(m,sd)
    print("%s: pins ok %d/%d; beta values %s; eta values %s; residual R weight mean %.3f sd %.3f (uniform expects 64, sd 8)"%(name,ok,N,{hex(k):v for k,v in beta.items()},{hex(k):v for k,v in eta.items()},m,sd))
(m0,s0),(m1,s1)=res['t_hi=0'],res['t_hi random 32']
print("difference of means %.3f, z=%.2f"%(m1-m0,(m1-m0)/math.sqrt(s0**2/N+s1**2/N)))
# dependence: fix 9 words, vary t_hi only
chg=collections.Counter(); first=collections.Counter(); Rsame=0; M_=300; Ychg=collections.Counter(); wchg=collections.Counter(); tlo_same=0; dig_same=0
for _ in range(M_):
    f=rf(0); w0_,t0_,_=build(f); a0,_b=messages(w0_,t0_)
    ta0=traces(a0,t0_,55)
    g=dict(f); g['t_hi']=R.getrandbits(32); w1_,t1_,_=build(g); a1_,_b=messages(w1_,t1_)
    ta1=traces(a1_,t1_,55)
    tlo_same+= (t0_&M)==(t1_&M)
    for i in range(16): wchg[i]+= w0_[i]!=w1_[i]
    fd=next((k for k in range(16) if ta0[k]!=ta1[k]),None); first[fd]+=1
    for k in range(16): chg[k]+= ta0[k]!=ta1[k]
    dig_same+= ta0[15]==ta1[15]
nm=['K0','K1','K2','K3','D0','D1','D2','D3','C0','C1','C2','C3','E0','E1','E2','E3']
print("DEP (t_hi alone changed, 9 other free words fixed, %d draws): t_lo unchanged %d; final state identical %d"%(M_,tlo_same,dig_same))
print(" message words changed (of 300):",{('w%d'%i):v for i,v in wchg.items() if v})
print(" calls whose output state changes:",{nm[k]:v for k,v in chg.items() if v})
print(" first differing call:",{(nm[k] if k is not None else None):v for k,v in first.items()})
