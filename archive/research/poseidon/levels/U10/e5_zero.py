"""U10 Q5: all constants zero. cap=0 => exact mu4 symmetry y(lam x)=lam y(x) with partial rounds; full scaling when r=0."""
import time, numpy as np
from toylib import *
T0=time.time()
def yfull(t,r):
    q=t.q; out=[]
    for NK,RHO,s in t.run_all(r): out.append(s[0])
    return np.concatenate(out).reshape(q,q)
for q in (769,4099):
  sq=[l for l in range(1,q) if pow(l,4,q)==1]
  for r in (0,1,2):
    print(f"q={q} r={r} (|mu4 in F_q|={len(sq)}):")
    for label,zc,cap in (("zero consts, cap=0",True,0),("zero consts, cap=2^65",True,None),("random consts, cap=0",False,0),("random consts, cap=2^65",False,None)):
        t=Toy(q,1,zero_consts=zc,cap=cap)
        c=keycounts(t,r,lambda s:s[0],q)
        n,ratio,vm,img=stat(c,q*q,q)
        nz=c[1:]
        orb=all(len({int(c[(l*v)%q]) for l in sq})==1 for v in range(1,q))
        print(f"   {label:26s} fibre(0)={int(c[0]):6d} #distinct nonzero fibre sizes={len(set(nz.tolist()))} (min {int(nz.min())} max {int(nz.max())}) mu4-invariant sizes={orb} coll-ratio={ratio:.3f} var/mean={vm:.2f} image={img}",flush=True)
  t=Toy(q,1,zero_consts=True,cap=0); y=yfull(t,1); ok=True
  for l in sq:
      idx=(l*np.arange(q))%q
      ok&=bool(np.all(y[np.ix_(idx,idx)]==(l*y)%q))
  print(f"   direct check y(lam*(nk,rho))=lam*y, lam in mu4, zero consts cap=0 r=1: {ok}")
  t=Toy(q,1,zero_consts=True,cap=0); y0=yfull(t,0); e=pow(5,8,q-1)
  ok=all(bool(np.all(y0[np.ix_((l*np.arange(q))%q,(l*np.arange(q))%q)]==(pow(l,e,q)*y0)%q)) for l in (2,3,5,7))
  print(f"   r=0 zero consts cap=0: y(lam x)=lam^(5^8) y(x) for lam in 2,3,5,7: {ok}")
  z=int((y==0).sum()); print(f"   zero consts cap=0 r=1: inputs mapping to 0: {z} (random function ~{q}); symmetric pairs inside fibre(0)")
  # cap family at r=0 with zero consts: fibre-size multiset identical for every nonzero cap?
  t0=Toy(q,1,zero_consts=True,cap=1); base=sorted(keycounts(t0,0,lambda s:s[0],q).tolist())
  same=0
  for cap in range(2,(40 if q<2000 else 8)):
      tc=Toy(q,1,zero_consts=True,cap=cap)
      same+= sorted(keycounts(tc,0,lambda s:s[0],q).tolist())==base
  print(f"   r=0 zero consts: fibre-size multiset equal to cap=1's for {same}/{(40 if q<2000 else 8)-2} other caps tested")
  same=0
  t1=Toy(q,1,zero_consts=True,cap=1); base1=sorted(keycounts(t1,1,lambda s:s[0],q).tolist())
  for cap in range(2,(40 if q<2000 else 8)):
      tc=Toy(q,1,zero_consts=True,cap=cap)
      same+= sorted(keycounts(tc,1,lambda s:s[0],q).tolist())==base1
  print(f"   r=1 zero consts: fibre-size multiset equal to cap=1's for {same}/{(40 if q<2000 else 8)-2} other caps tested",flush=True)
