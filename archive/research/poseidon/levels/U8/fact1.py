# U8 q1: extend factorisations of p-1, p+1, p^2+p+1 (trial + Pollard p-1 + sympy ECM, time-limited)
import time, sys, gmpy2
from gmpy2 import mpz, is_prime
from sympy.ntheory import ecm as secm
P=0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
LIM=float(sys.argv[1]) if len(sys.argv)>1 else 600
def trial(n,B=2*10**6):
    fs=[]
    n=mpz(n); p=mpz(2)
    while p<B:
        while n%p==0: fs.append(int(p)); n//=p
        p=gmpy2.next_prime(p)
    return fs,int(n)
def pm1(n,B1=2*10**6):
    n=mpz(n); a=mpz(2); p=mpz(2)
    while p<B1:
        e=1
        while p**(e+1)<=B1: e+=1
        a=gmpy2.powmod(a,p**e,n); p=gmpy2.next_prime(p)
    g=gmpy2.gcd(a-1,n)
    return int(g) if 1<g<n else None
def run(name,N):
    t=time.time()
    fs,rest=trial(N)
    print(name,"trial<2e6 factors",fs,"cofactor bits",rest.bit_length(),flush=True)
    stack=[rest]; prime=[]; comp=[]
    while stack:
        n=stack.pop()
        if n==1: continue
        if is_prime(n,30): prime.append(n); continue
        g=pm1(n)
        if g: stack+= [g,n//g]; print(name,"pollard p-1 found",g,flush=True); continue
        comp.append(n)
    # ECM on composites, time-limited each
    out=[]
    for n in comp:
        t0=time.time(); work=[n]; 
        while work and time.time()-t0<LIM:
            m=work.pop()
            if is_prime(m,30): prime.append(m); continue
            found=None
            for B1 in (11000,50000,250000):
                if time.time()-t0>LIM: break
                try:
                    f=secm(m,B1=B1,B2=100*B1,max_curve=40)
                except Exception as e:
                    f=None
                if f: found=min(f); break
            if found and 1<found<m:
                print(name,"ECM found factor bits",int(found).bit_length(),found,flush=True)
                work+=[int(found),m//int(found)]
            else: out.append(m)
        out+=work
    print(name,"PRIME factors >2e6:",[(q.bit_length(),int(q)) for q in prime])
    print(name,"UNFACTORED:",[(q.bit_length(),q) for q in out],"time",round(time.time()-t,1),flush=True)
run("p-1",P-1); run("p+1",P+1); run("p2+p+1",P*P+P+1)
