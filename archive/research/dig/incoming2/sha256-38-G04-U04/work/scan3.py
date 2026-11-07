import sys,time,json,math,random
import numpy as np
import a0lean38 as L
M=L.M; u=np.uint32
out={}
def ror(x,n): return (x>>u(n))|(x<<u(32-n))
def s0v(x): return ror(x,7)^ror(x,18)^(x>>u(3))
def S0v(x): return ror(x,2)^ror(x,13)^ror(x,22)
def S1v(x): return ror(x,6)^ror(x,11)^ror(x,25)
def CHv(x,y,z): return (x&y)^(~x&z)
def MAJv(x,y,z): return (x&y)|(z&(x|y))
rng=np.random.default_rng(12345)
# (a) x gate: number of the 90 classes passing F7 for random A_-1, sampled
c7s=np.array([c[0] for c in L.CLASSES],dtype=np.uint32)
N=3_000_000
x=rng.integers(0,2**32,size=N,dtype=np.uint64).astype(np.uint32)
k=np.zeros(N,dtype=np.int16)
for c in c7s:
    w=u(c)-x
    k+=((s0v(w+u(L.D7))-s0v(w))==u(L.T7))
hist=np.bincount(k)
out['gate_N']=N; out['gate_mean_pass_classes']=float(k.mean()); out['gate_expected_90p7']=90*L.__dict__.get('P7',287309824/2**32)
out['gate_frac_none']=float((k==0).mean()); out['gate_frac_none_published_HIT0']=L.HIT0/2**32
out['gate_hist']=hist.tolist()
out['gate_var']=float(k.var())
print(out)
# (b) bijection W0..W5 <-> a0 : for random cv and a0 in G (all members of 3 classes), W0 - a0 const, W0..W5 injective, a0 recoverable
a0all=np.load('G_a0.npy'); 
rr=random.Random(3); okinj=0; okrec=0; tot=0
for t in range(20):
    cv=[rr.getrandbits(32) for _ in range(8)]
    cls=L.CLASSES[rr.randrange(90)]
    mem=L.class_members(*cls)
    seen=set(); ok=True
    base=None
    for a in mem:
        wx,wy=L.words_from_cv(cv,a)
        key=tuple(wx[:6]); seen.add(key)
        d=(wx[0]-a)&M
        if base is None: base=d
        ok&=(d==base)
        # recover a0 from W0..W5 and cv by running the forward steps: A0 from E0 = ...
        a_,b_,c_,d_,e_,f_,g_,h_=cv
        E0=(wx[0]+d_+h_+L.S1(e_)+L.CH(e_,f_,g_)+L.K[0])&M
        a0r=(E0-d_+L.S0(a_)+L.MAJ(a_,b_,c_))&M
        okrec+=(a0r==a); tot+=1
    okinj+= (len(seen)==len(mem) and ok)
out['bij_cvs_tested']=20; out['bij_inj_and_W0shift_const_ok']=okinj; out['bij_recover_a0_ok']=okrec; out['bij_total_variants']=tot
# check: W0..W5 of y member = W0..W5 of x (dW0..dW5=0)
rr2=random.Random(9); dz=0
for t in range(200):
    cv=[rr2.getrandbits(32) for _ in range(8)]; a=int(a0all[rr2.randrange(len(a0all))])
    wx,wy=L.words_from_cv(cv,a); dz+= (wx[:6]==wy[:6] and wx[6]==wy[6]) 
out['dW0_6_zero_ok_of_200']=dz
print(out)
# (c) r16 uniformity over all of G for random cvs
cvs=[[rr.getrandbits(32) for _ in range(8)] for _ in range(36)]
chosen=set(int(c) for c in c7s)
c7all=np.load('G_c7.npy')
inchosen=np.isin(c7all,c7s)
out['chosen_variants_in_G']=int(inchosen.sum())
res=[]
sa=L.SAx
t0=time.time()
for cv in cvs:
    a,b,c,d,e,f,g,h=cv; cnt=0; cntch=0; hits=[]
    for lo in range(0,len(a0all),1<<23):
        a0=a0all[lo:lo+(1<<23)]
        E0=a0+u(d)-u(L.S0(a))-u(L.MAJ(a,b,c))
        W0=E0-u(d)-u(h)-u(L.S1(e))-u(L.CH(e,f,g))-u(L.K[0])
        E1=u(sa[1])+u(c)-S0v(a0)-MAJv(a0,u(a),u(b))
        W1=E1-u(c)-u(g)-S1v(E0)-CHv(E0,u(e),u(f))-u(L.K[1])
        E16=u(L.C16)+W0+s0v(W1)
        ok=((E16-u(L.R16B))&~u(L.R16F))==0
        # cross check with scalar on hits
        idx=np.nonzero(ok)[0]
        for i in idx:
            assert L.r16ok(L.e16x(cv,int(a0[i])))
        cnt+=len(idx); cntch+=int(inchosen[lo:lo+(1<<23)][idx].sum())
    res.append((cnt,cntch))
print('r16 per cv',res,time.time()-t0)
cs=[r[0] for r in res]
out['r16_cvs']=len(cvs); out['r16_counts_per_cv']=cs; out['r16_mean']=sum(cs)/len(cs); out['r16_expected']=len(a0all)*32/2**32
out['r16_var']=float(np.var(cs)); out['r16_chosen_total']=sum(r[1] for r in res)
# scalar cross-check on random a0 in G for E16x formula
out['e16_formula_ok']=all(L.e16x(cvs[0],int(a0all[i]))==L.e16x_ref(cvs[0],int(a0all[i])) for i in range(0,len(a0all),len(a0all)//50))
json.dump(out,open('scan3.json','w'),indent=1)
print(json.dumps(out)[:3000])
