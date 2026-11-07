from fractions import Fraction
from math import exp, log, isqrt, lgamma, factorial
LANES=256; D=122; SB=1<<48; KAPPA=11; N=1<<256
def tail_ln(mean,k): return -mean+k*(1+log(mean/k))
def lnmgf(lam, q, uc, uh, steps=4000):
    # ln E exp(lam*z(u)) u~Exp(1) censored at uc: z=256 m^2 + 2 q (m-uh)+, m=min(u,uc)
    def g(u):
        m=min(u,uc); return lam*(256*m*m+2*q*max(0.0,m-uh))-u
    h=uc/steps; pts=[g(i*h) for i in range(steps+1)]
    gtail=lam*(256*uc*uc+2*q*(uc-uh))-uc
    gm=max(max(pts),gtail)
    s=0.0
    for i,v in enumerate(pts):
        wgt=1 if i in (0,steps) else (4 if i%2 else 2)
        s+=wgt*exp(v-gm)
    s*=h/3
    s+=exp(gtail-gm)
    return gm+log(s)
def zquant(q,uc,uh,nmax,eps):
    # smallest z (units L^2) with inf_lam [-lam z + nmax lnmgf(lam)] <= ln eps ; lam in 1/L^2 units
    # for each lam: z(lam)= (nmax*lnmgf - ln eps)/lam ; minimise over lam
    best=None
    lo,hi=1e-7,1e-2
    import math
    for i in range(200):
        lam=lo*(hi/lo)**(i/199)
        z=(nmax*lnmgf(lam,q,uc,uh)-log(eps))/lam
        if best is None or z<best[0]: best=(z,lam)
    # refine
    z0,l0=best
    lo,hi=l0/1.2,l0*1.2
    for i in range(100):
        lam=lo+(hi-lo)*i/99
        z=(nmax*lnmgf(lam,q,uc,uh)-log(eps))/lam
        if z<best[0]: best=(z,lam)
    return best
def model(Tp,B,K=2,eps_n=1e-6,eps_z=1e-6):
    L=Fraction(1<<D,Tp); Q=B*LANES; q=float(Q/L)
    c=-(-KAPPA*L.numerator//L.denominator); cS=c+SB
    uc=float(cS/L); uh=float((c//2)/L)
    # n_fin quantile
    k=int(q)+1
    while tail_ln(q,k)>log(eps_n): k+=1
    nmax=k-1+K+LANES
    z,lam=zquant(q,uc,uh,nmax,eps_z)      # L^2 units
    L2=float(L*L)
    Nf=float(N)
    S0=(q*q/2)  # L^2
    kap=3*q*uc+256*uc*uc                  # per merge, L^2 units
    cutc=K*uc*q
    kN=kap*L2/Nf
    w=1.0
    for _ in range(200): w=exp(w*kN)
    Qq=q*q/2
    th=(w*(S0-z-cutc)-(w-1)*Qq)*L2/Nf
    return dict(q=q,nmax=nmax,z=z,lam=lam,w=w,theta=th,theta_nolosses=S0*L2/Nf,uc=uc,nfin=k-1)
if __name__=="__main__":
    import sys
    # current plan: Tp=68 B=...
    Tp=68
    B=1432349394108965344396540883412795810
    m=model(Tp,B); print(m)
    print(1-exp(-m['theta']))
