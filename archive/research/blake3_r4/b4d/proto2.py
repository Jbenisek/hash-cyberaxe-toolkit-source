import sys
from proto import *
from math import exp, log
def pl(Tp,q,epsn,epsz,K=2):
    L=Fraction(1<<D,Tp); B=int(q*float(L)/256)+1
    m=model(Tp,B,K,epsn,epsz)
    th=m['theta']
    mu=m['q']*exp(-KAPPA)
    pk=[exp(-mu)*mu**j/factorial(j) for j in range(K+1)]
    pk3=1-sum(pk)
    capl=2.0**((-m['q']+ (int(5251)+1)*(1+log(m['q']/5252)))/log(2))
    loss=epsn+epsz+pk3+2.0**-100+capl
    return 1-exp(-th)-loss, th, m
def solveq(Tp,epsn,epsz,K=2):
    lo,hi=3500.0,9000.0
    for _ in range(30):
        mid=(lo+hi)/2
        if pl(Tp,mid,epsn,epsz,K)[0]>=0.39: hi=mid
        else: lo=mid
    return hi
for Tp in (68,64,60,56):
  for eps in (1e-6,1e-4,3e-4):
    q=solveq(Tp,eps,eps); r=pl(Tp,q,eps,eps)
    print(Tp,eps,"q=%.1f"%q,"P=%.4f th=%.4f z=%.0f nmax=%d"%(r[0],r[1],r[2]['z'],r[2]['nmax']), "L-ratio B/B0=%.4f"%(q/4689.63*68/Tp))
