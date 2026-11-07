import random, sys, time
import flint
from collections import Counter
def inv(a,q): return pow(a,-1,q)
def mm(A,B,q): return [[sum(A[i][k]*B[k][j] for k in range(3))%q for j in range(3)] for i in range(3)]
def mn2(A,q):
    out=[]
    for i in range(3):
        for j in range(3):
            r=[k for k in range(3) if k!=i]; c=[k for k in range(3) if k!=j]
            out.append((A[r[0]][c[0]]*A[r[1]][c[1]]-A[r[0]][c[1]]*A[r[1]][c[0]])%q)
    return out
def det(A,q):
    return (A[0][0]*(A[1][1]*A[2][2]-A[1][2]*A[2][1])-A[0][1]*(A[1][0]*A[2][2]-A[1][2]*A[2][0])+A[0][2]*(A[1][0]*A[2][1]-A[1][1]*A[2][0]))%q
def mds(A,q): return all(x for r in A for x in r) and all(mn2(A,q))
def inv3(A,q):
    d=inv(det(A,q),q); m=mn2(A,q)
    return [[(m[3*j+i] if (i+j)%2==0 else -m[3*j+i])*d%q for j in range(3)] for i in range(3)]
class F3:
    def __init__(s,T,S,D,q): s.T,s.S,s.D,s.q=T,S,D,q
    def mul(s,a,b):
        c=[0]*5
        for i in range(3):
            for j in range(3): c[i+j]+=a[i]*b[j]
        c3,c4=c[3],c[4]; c3+=s.T*c4; c[2]+=-s.S*c4; c[1]+=s.D*c4
        c[2]+=s.T*c3; c[1]+=-s.S*c3; c[0]+=s.D*c3
        return (c[0]%s.q,c[1]%s.q,c[2]%s.q)
    def pw(s,a,e):
        r=(1,0,0)
        while e:
            if e&1: r=s.mul(r,a)
            a=s.mul(a,a); e>>=1
        return r
def cp(M,q):
    T=(M[0][0]+M[1][1]+M[2][2])%q; S=sum(mn2(M,q)[i] for i in (0,4,8))%q; return T,S,det(M,q)
def primitive(M,q):
    T,S,D=cp(M,q); K=F3(T,S,D,q); a=(0,1,0); n=q**3-1
    fr=K.pw(a,q)
    if fr==a or K.pw(fr,q)==a or K.pw(K.pw(fr,q),q)!=a: return False
    primes=[int(x) for x,e in flint.fmpz(n).factor()]
    return all(K.pw(a,n//pr)!=(1,0,0) for pr in primes)
def leg(a,q):
    a%=q
    return 0 if a==0 else (1 if pow(a,(q-1)//2,q)==1 else -1)
random.seed(777)
for q in [257,769,1009]:
    # find random Cauchy M with M primitive (alpha generator of F_{q^3}^*)
    while True:
        xs=random.sample(range(q),3); ys=random.sample(range(q),3)
        if all((xs[i]+ys[j])%q for i in range(3) for j in range(3)):
            M=[[inv((xs[i]+ys[j])%q,q) for j in range(3)] for i in range(3)]
            if mds(M,q) and det(M,q) and primitive(M,q): break
    Mi=inv3(M,q)
    m=q*q+q+1
    # projective points a=(a0,a1,a2) -> matrix a0 I + a1 M + a2 M2
    M2=mm(M,M,q); I=[[1,0,0],[0,1,0],[0,0,1]]
    def comb(a): return [[(a[0]*I[i][j]+a[1]*M[i][j]+a[2]*M2[i][j])%q for j in range(3)] for i in range(3)]
    pts=[(1,b,c) for b in range(q) for c in range(q)]+[(0,1,c) for c in range(q)]+[(0,0,1)]
    assert len(pts)==m
    badpts=0; badlines=0
    for a in pts:
        A=comb(a)
        if not mds(A,q): badpts+=1
    # iterate k over 1..m (one projective period if M primitive: projective order = q^2+q+1)
    A=I; Ai=I; badk=[]; mism=0
    for k in range(1,m+1):
        A=mm(A,M,q); Ai=mm(Ai,Mi,q)
        b_mds = not mds(A,q)
        b_ent = (not all(x for r in A for x in r)) or (not all(x for r in Ai for x in r))
        if b_mds!=b_ent: mism+=1
        if b_mds: badk.append(k)
    print(f"q={q} (q mod 4={q%4}, gcd(5,q-1)={__import__('math').gcd(5,q-1)}): alpha primitive in F_q^3 (ord q^3-1): True. projective points {m}")
    print(f"   non-MDS projective points: {badpts} ({badpts/m:.5f}); 18/q = {18/q:.5f}")
    print(f"   non-MDS powers M^k among k=1..{m} (one projective period; note M^m = scalar {mm(A,I,q)[0][1]==0}): {len(badk)} ; first 8 bad k: {badk[:8]}")
    print(f"   minors-zero <=> entry of M^-k zero (and M^k entry zero) agree for all k: mismatches={mism}")
    gaps=[b-a for a,b in zip([0]+badk,badk+[m+1])]
    print(f"   longest run of consecutive MDS powers within one period: {max(gaps)-1}; mean gap {sum(gaps)/len(gaps):.1f} (q/18 = {q/18:.1f})")
    # M^k MDS for small k fraction
    print(f"   smallest k with M^k not MDS: {badk[0] if badk else None}")
    # Legendre pattern of M and relation leg(det)
    print(f"   leg(det)=={leg(det(M,q),q)} ; product of leg(entries) * leg of Vandermonde diffs = {__import__('functools').reduce(lambda u,v:u*v,[leg(M[i][j],q) for i in range(3) for j in range(3)],1)*__import__('functools').reduce(lambda u,v:u*v,[leg((xs[j]-xs[i])*(ys[j]-ys[i]),q) for i in range(3) for j in range(i+1,3)],1)}")
    sys.stdout.flush()
