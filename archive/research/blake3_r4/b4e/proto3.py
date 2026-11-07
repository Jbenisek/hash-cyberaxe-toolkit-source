import sys
from proto import *
import proto
from math import exp, log
def lnmgf2(lam,q,uc,uh,coef,steps=2000):
    def g(u):
        m=min(u,uc); return lam*(coef*m*m+2*q*max(0.0,m-uh))-u
    h=uc/steps; pts=[g(i*h) for i in range(steps+1)]
    gt=lam*(coef*uc*uc+2*q*(uc-uh))-uc
    gm=max(max(pts),gt); s=0.0
    for i,v in enumerate(pts):
        s+=(1 if i in (0,steps) else (4 if i%2 else 2))*exp(v-gm)
    return gm+log(s*h/3+exp(gt-gm))
def zq(q,uc,uh,nmax,eps,coef):
    best=None
    lo,hi=1e-6,1e-2
    for i in range(60):
        lam=lo*(hi/lo)**(i/59)
        z=(nmax*lnmgf2(lam,q,uc,uh,coef)-log(eps))/lam
        if best is None or z<best[0]: best=(z,lam)
    l0=best[1]
    for i in range(40):
        lam=l0/1.15+(l0*1.15-l0/1.15)*i/39
        z=(nmax*lnmgf2(lam,q,uc,uh,coef)-log(eps))/lam
        if z<best[0]: best=(z,lam)
    return best
def pl(Tp,q,epsn,epsz,coef,K=2,destroy=True):
    L=Fraction(1<<D,Tp); Lf=float(L); L2=Lf*Lf; Nf=float(N)
    c=-(-KAPPA*L.numerator//L.denominator); cS=c+SB
    uc=float(cS/L); uh=float((c//2)/L)
    k=int(q)+1
    while tail_ln(q,k)>log(epsn): k+=1
    nmax=k-1+K+256
    z,lam=zq(q,uc,uh,nmax,epsz,coef)
    S0=q*q/2
    kap=4*q*uc+128*uc*uc+(coef*uc*uc+2*q*(uc-uh))
    kN=kap*L2/Nf
    w=1.0
    for _ in range(100): w=exp(w*kN)
    th=(w*(S0-z-K*uc*q)-(w-1)*S0)*L2/Nf
    mu=q*exp(-KAPPA); pk=[exp(-mu)*mu**j/factorial(j) for j in range(K+1)]
    des=(uc*q*L2/Nf) if destroy else 0.0
    tl=tail_ln(q,5252)/log(2) if q<5252 else 0
    loss=epsn+epsz+(1-sum(pk))+2.0**-100+2.0**tl+des
    return 1-exp(-th)-loss, th, dict(z=z,nmax=nmax,w=w)
def solve(Tp,epsn,epsz,coef):
    lo,hi=3000.0,5252.0
    for _ in range(26):
        mid=(lo+hi)/2
        if pl(Tp,mid,epsn,epsz,coef)[0]>=0.39: hi=mid
        else: lo=mid
    return hi
if __name__=="__main__":
    coef=float(sys.argv[1])
    for Tp in (68,66,64,62,60):
        q=solve(Tp,1e-4,1e-4,coef); r=pl(Tp,q,1e-4,1e-4,coef)
        tl=tail_ln(q,5252)/log(2)
        print(coef,Tp,"q=%.1f"%q,"P=%.4f th=%.4f z=%.0f"%(r[0],r[1],r[2]['z']),"B/B0=%.4f"%((q/Tp)/(4689.63/68)),"capl2=%.1f"%tl, flush=True)
