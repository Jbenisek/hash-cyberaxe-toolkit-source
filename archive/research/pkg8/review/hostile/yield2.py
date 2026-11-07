#!/usr/bin/env python3
"""Larger, chunked yield measurement with the between-tuple spread."""
import numpy as np, random, sys
sys.path.insert(0,'.')
from yieldmeas import (stepO,mid_w2w0,mem_part,h1_of,ruleA,gate,e1_of_k,FREE17,IDX,X2BITS,u32)
np.seterr(over='ignore')

NOUT=int(sys.argv[1]) if len(sys.argv)>1 else 256
rng=random.Random(int(sys.argv[2]) if len(sys.argv)>2 else 99)
kk=np.arange(1<<17,dtype=np.uint64)
mask=((kk>>np.uint64(10))&np.uint64(1)==0)&((kk>>np.uint64(15))&np.uint64(1)==0)&((kk>>np.uint64(16))&np.uint64(1)==0)
krep=kk[mask]; NREP=krep.size
e1rep_all=e1_of_k(krep)
dk=np.arange(8,dtype=np.uint64)
p=1/256.
Y=[]; G=[]; A=[]
tot=dict(rep=0,open=0,repA=0,nbA=0,nbw=0,nbw2=0,repw=0,repwA=0,repwO=0,none=0)
per_flip=np.zeros(64,dtype=np.int64)
for o in range(NOUT):
    n=stepO(*[rng.getrandbits(32) for _ in range(6)])
    base=rng.getrandbits(32)
    for b in X2BITS: base &= ~(1<<b)
    dx=np.arange(8,dtype=np.uint64)
    X2v=np.full(8,base,dtype=np.uint64)
    for j,b in enumerate(X2BITS): X2v |= ((dx>>np.uint64(j))&np.uint64(1))<<np.uint64(b)
    X2v=X2v.astype(u32)
    w2v,w0v=mid_w2w0(n,X2v)
    C0a1r,X6r=mem_part(n,e1rep_all)
    h1r=h1_of(n,w2v[0],w0v[0],X2v[0],C0a1r,X6r,e1rep_all)
    gr=gate(h1r); ar=ruleA(h1r)
    tot['rep']+=NREP; tot['open']+=int(gr.sum()); tot['repA']+=int(ar.sum())
    nw=NREP//7
    tot['repw']+=nw
    tot['repwO']+=int(gr[:nw*7].reshape(nw,7).any(axis=1).sum())
    tot['repwA']+=int(ar[:nw*7].reshape(nw,7).any(axis=1).sum())
    sel=np.nonzero(gr)[0]
    nbA_t=0
    for s in range(0,sel.size,8192):
        ks=krep[sel[s:s+8192]]
        kn=np.empty((ks.size,8),dtype=np.uint64); kn[:]=ks[:,None]
        for j,ix in enumerate(IDX): kn |= ((dk>>np.uint64(j))&np.uint64(1))[None,:]<<np.uint64(ix)
        e1n=e1_of_k(kn); C0a1n,X6n=mem_part(n,e1n)
        H=h1_of(n,w2v[None,:,None],w0v[None,:,None],X2v[None,:,None],
                C0a1n[:,None,:],X6n[:,None,:],e1n[:,None,:])
        A64=ruleA(H).reshape(-1,64)
        per_flip+=A64.sum(axis=0)
        nb=A64.copy(); nb[:,0]=False
        nbA_t+=int(nb.sum())
        c=nb.sum(axis=1); tot['none']+=int((c==0).sum())
        lanes=nb[:,1:].reshape(-1,9,7)
        tot['nbw']+=lanes.shape[0]*9; tot['nbw2']+=int(lanes.any(axis=2).sum())
    tot['nbA']+=nbA_t
    Y.append(nbA_t/NREP/p); G.append(gr.sum()/NREP); A.append(ar.sum()/NREP)
Y=np.array(Y)
print("outer tuples %d, representatives %d, opened %d"%(NOUT,tot['rep'],tot['open']))
print("gate-open share   %.7f  (text 0.0624630)"%(tot['open']/tot['rep']))
print("rule-A share/rep  %.8f (2^-8=%.8f, ratio %.5f)"%(tot['repA']/tot['rep'],p,tot['repA']/tot['rep']/p))
y=tot['nbA']/tot['rep']/p
print("YIELD             %.3f  +- %.3f (between-tuple sd %.2f = %.1f%%)   H4 assumes 40.02"
      %(y,Y.std(ddof=1)/np.sqrt(NOUT),Y.std(ddof=1),100*Y.std(ddof=1)/Y.mean()))
print("per-tuple yield   min %.2f max %.2f"%(Y.min(),Y.max()))
print("trial-equivalents %.3f  (text 41.02; lossless 64)"%(1+y))
print("TE/64             %.5f  (text 0.64094)"%((1+y)/64))
print("rule-A nbrs/opened cluster %.4f (text 2.5008)"%(tot['nbA']/tot['open']))
print("opened clusters with none  %.4f (text 0.1436)"%(tot['none']/tot['open']))
print("rep words open lane  %.6f (text 0.241596)"%(tot['repwO']/tot['repw']))
print("rep words rule-A     %.6f (text 0.026178)"%(tot['repwA']/tot['repw']))
print("nb words / rep       %.5f (text 0.5625)"%(tot['nbw']/tot['rep']))
print("nb words into st2    %.5f (text 0.1364)"%(tot['nbw2']/tot['nbw']))
pf=per_flip/tot['open']/p/16
print("63 retention rates   min %.4f max %.4f mean %.4f (text 0.543..0.874)"%(pf[1:].min(),pf[1:].max(),pf[1:].mean()))
stA=(1/7+tot['nbw']/tot['rep'])*47
st2=((tot['repwA']/tot['repw'])/7+(tot['nbw']/tot['rep'])*(tot['nbw2']/tot['nbw']))*135
print("cost/rep %.3f -> per TE %.4f ; per nominal trial %.4f ; stage-2 share of words %.5f"
      %(stA+st2,(stA+st2)/(1+y),(stA+st2)/64,(st2/135)/(stA/47)))
