import sys, random
exec(open('v2.py').read().split("mode=sys.argv")[0])
from math import gcd
r=random.Random(11); c0=R.RC[0][0]
ok=True
for k in range(6):
    nk0=r.randrange(p); rho0=r.randrange(p); x=PC([0,1])
    f=lane0(RCr:=[list(a) for a in R.RC],[list(a) for a in R.MDS],[x,PC([rho0]),PC([R.CAPACITY])])
    q=lev(f,nk0); real=pat(q)
    # g from f: f(x)=g((x+c0)^5); recover g by taking coefficients of f(u-c0) at multiples of 5
    fu=f(PC([-c0,1])) if False else None
    # compose f(x) with x -> x-c0 : Taylor shift
    cs=[int(c) for c in f.coeffs()]
    from math import comb
    sh=[0]*len(cs)
    for i,ci in enumerate(cs):
        for j in range(i+1): sh[j]=(sh[j]+ci*comb(i,j)*pow(-c0,i-j,p))%p   # poly in u=x+c0
    assert all(sh[j]==0 for j in range(len(sh)) if j%5), 'not a function of u^5'
    g=PC([sh[5*j] for j in range(126)]); y0=pow(nk0+c0,5,p)
    h=g-PC([int(g(y0))]); h,rem=divmod(h,PC([-y0,1])); assert rem.degree()<0
    pred=[]
    c,fac=h.factor()
    def lcm(a,b): return a*b//gcd(a,b)
    for phi,e in fac:
        d=phi.degree()
        if d%4: pred+= [d]*e + [lcm(d,4)]*(e*4*d//lcm(d,4))
        else:
            # irreducible 5d or 5 factors of d: test directly
            u=PC([0]*5+[1]); comp=PC([0])
            for co in reversed(phi.coeffs()): comp=comp*u+PC([int(co)])
            pp=pat(comp); pred+=[dd for dd,ee in pp for _ in range(ee*e)]
    pred.append(4) # quartic (u^5-u0^5)/(u-u0)... accounts the y-root y0 factor
    pred.sort(reverse=True); rd=sorted([d for d,e in real for _ in range(e)],reverse=True)
    print(k,'h-factors',fmt(pat(h)),'| pred==real:',pred==rd,flush=True)
    if pred!=rd: print(' pred',pred,'\n real',rd)
