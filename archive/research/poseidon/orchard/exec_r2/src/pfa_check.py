# verify the twiddle-free radix-3 + radix-2 row transform (PFA) layout claims in a small prime field
import random
def brv(x,a):
    r=0
    for i in range(a):
        r=(r<<1)|((x>>i)&1)
    return r
def test(q,a):
    n=1<<a; N=3*n
    assert (q-1)%N==0
    # primitive N-th root
    for g in range(2,q):
        th=pow(g,(q-1)//N,q)
        if pow(th,N//2,q)!=1 and pow(th,N//3,q)!=1: break
    w3=pow(th,n,q)
    beta=pow(3,-1,n) if n>1 else 0
    c0=(3*beta-1)//n
    rho=pow(th,3*beta,q)       # row root rho'
    # arbitrary choice check: choose independent rho', w3 and derive theta
    x=[random.randrange(q) for _ in range(N)]
    # stage A
    rows=[[0]*n for _ in range(3)]
    for i0 in range(n):
        u=[x[i0+n*t] for t in range(3)]
        t0=(c0*i0)%3
        v=[u[(t0+i1)%3] for i1 in range(3)]
        for k1 in range(3):
            rows[k1][i0]=sum(v[i1]*pow(w3,i1*k1,q) for i1 in range(3))%q
    # row DIF -> bit reversed
    out=[[0]*n for _ in range(3)]
    for k1 in range(3):
        for k2 in range(n):
            val=sum(rows[k1][i0]*pow(rho,i0*k2,q) for i0 in range(n))%q
            out[k1][brv(k2,a)]=val
    theta=(rho*pow(w3,(-c0)%3,q))%q
    ok=True
    for k in range(N):
        pt=pow(theta,k,q)
        ev=sum(x[i]*pow(pt,i,q) for i in range(N))%q
        if out[k%3][brv(k%n,a)]!=ev: ok=False
    print(q,a,'c0',c0,'theta order ok',pow(theta,N//2,q)!=1,'layout ok',ok)
test(73,2); test(73,3)
test(193,4) if (192%48==0) else None
