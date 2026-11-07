from u5_lib import *
import time
T,S,D = charpoly(MDS); K=F3(T,S,D); al=(0,1,0)
Mi = matinv(MDS)
I3=[[1,0,0],[0,1,0],[0,0,1]]
print("=== Q3 real: is M^k MDS ===")
t=time.time()
A=I3; B=I3; bad=[]; KMAX=200000
for k in range(1,KMAX+1):
    A=matmul(A,MDS); B=matmul(B,Mi)
    if not (all(x for r in A for x in r) and all(x for r in B for x in r)):
        bad.append(k)
print(f"k=1..{KMAX}: entries of M^k and M^-k all nonzero except at k in {bad}  ({time.time()-t:.1f}s)")
# full MDS check (entries + minors) for k<=1000, both signs, and equality minors <-> entries of inverse
A=I3; ok=True; first=None
for k in range(1,1001):
    A=matmul(A,MDS)
    if not is_mds(A): ok=False; first=k; break
print("M^k MDS (entries and all 9 minors nonzero) for every k=1..1000:",ok,first)
# identity: cofactor matrix of M^k = det(M^k) * (M^-k)^T  => minors of M^k zero iff entries of M^-k zero
A=I3; B=I3; allok=True
for k in range(1,60):
    A=matmul(A,MDS); B=matmul(B,Mi)
    dm=det3(A); m=minors2(A)
    # cofactor_ij = (-1)^{i+j} minor_ij ; compare with dm*B[j][i]
    for i in range(3):
        for j in range(3):
            c = m[3*i+j] if (i+j)%2==0 else (-m[3*i+j])%P
            if c != dm*B[j][i]%P: allok=False
print("cofactor(M^k) == det(M^k) (M^-k)^T for k=1..59:",allok)
# F_{p^3} coefficient form: M^k = a0 I + a1 M + a2 M^2 with alpha^k=(a0,a1,a2)
M2=matmul(MDS,MDS); ok=True
a=(1,0,0)
for k in range(0,15):
    Mk=I3
    for _ in range(k): Mk=matmul(Mk,MDS)
    lhs=[[ (a[0]*I3[i][j]+a[1]*MDS[i][j]+a[2]*M2[i][j])%P for j in range(3)] for i in range(3)]
    if lhs!=Mk: ok=False
    a=K.mul(a,al)
print("M^k = a0 I + a1 M + a2 M^2 with (a0,a1,a2)=alpha^k, k=0..14:",ok)
# which linear forms in (a0,a1,a2) define the 9 lines; show their normals (entry (i,j): [delta_ij, M_ij, M2_ij])
print("line normals (delta_ij, M_ij, (M^2)_ij) have 3rd coords M2_ij and 2nd M_ij; lines pairwise distinct:",
      len({tuple(x*inv(M2[i][j] if M2[i][j] else 1)%P for x in (I3[i][j],MDS[i][j],M2[i][j])) for i in range(3) for j in range(3)})==9)
print("diagonal of M^k: entry (i,i)=a0+a1*M_ii+a2*M2_ii ; off-diagonal: a1*M_ij+a2*M2_ij  => off-diagonal zero-planes all pass through the point a=(1,0,0)?? (no: they pass through (1,0,0) since a0 absent)")
print("    -> off-diagonal entry (i,j) of M^k vanishes iff a1 M_ij + a2 M2_ij=0, i.e. a2/a1 = -M_ij/M2_ij  (a0 free)")
print("    ratios -M_ij/M2_ij for the 6 off-diagonal:", [hex((-MDS[i][j]*inv(M2[i][j]))%P) for i in range(3) for j in range(3) if i!=j])
print("=== Q8 random Cauchy comparison ===")
random.seed(20261012)
n=P**3-1
smallq={2:32,3:2,463:1,73:1,5839:1,12221196943:1,5187662682403:1}
def stats(M):
    d=det3(M); mn=minors2(M)
    Tt,Ss,Dd=charpoly(M); KK=F3(Tt,Ss,Dd); a=(0,1,0)
    irr = (KK.pw(a,P)!=a) and (KK.pw(a,P*P+P+1) == (Dd,0,0))  # alpha^p!=alpha and degree 3 => (cubic w/o root) irreducible iff alpha^(p^3)=alpha and alpha^p != alpha
    irr = irr and KK.pw(KK.pw(a,P),P)==KK.pw(a,P*P)
    # proper irreducibility: cubic irreducible iff no root in F_p iff gcd(x^p - x, f)=1 ; test via alpha^p != alpha in a basis AND f has no root: use (x^p mod f) not in F_p-span issues -> use frobenius orbit size 3
    fr=KK.pw(a,P)
    irr = fr!=a and KK.pw(fr,P)!=a and KK.pw(KK.pw(fr,P),P)==a
    full = None
    if irr:
        full = all(KK.pw(a,n//q)!=KK.one() for q in smallq)
    return dict(res_entries=sum(1 for r in M for x in r if legendre(x)==1), pattern=tuple(legendre(x) for r in M for x in r),
                legdet=legendre(d), res_minors=sum(1 for x in mn if legendre(x)==1), legT=legendre(Tt), legS=legendre(Ss),
                irr=irr, full=full, minbits=min(x.bit_length() for r in M for x in r),
                M2mds=is_mds(matmul(M,M)), Mi_pattern=tuple(legendre(x) for r in matinv(M) for x in r))
real=stats(MDS)
print("real:",real)
N=1000; samples=[]
t=time.time()
for _ in range(N):
    while True:
        xs=[random.randrange(P) for _ in range(3)]; ys=[random.randrange(P) for _ in range(3)]
        if len(set(xs))==3 and len(set(ys))==3 and all((xs[i]+ys[j])%P for i in range(3) for j in range(3)): break
    M=[[inv(xs[i]+ys[j]) for j in range(3)] for i in range(3)]
    samples.append(stats(M))
print(f"{N} random Cauchy matrices done in {time.time()-t:.0f}s")
from collections import Counter
print("residue-count of 9 entries distribution (random):",sorted(Counter(s['res_entries'] for s in samples).items()),"; real:",real['res_entries'])
print("residue-count of 9 minors distribution (random):",sorted(Counter(s['res_minors'] for s in samples).items()),"; real:",real['res_minors'])
print("leg(det) -1 fraction:",sum(1 for s in samples if s['legdet']==-1)/N,"; real -1")
print("exact same 9-entry Legendre pattern as real:",sum(1 for s in samples if s['pattern']==real['pattern']),"of",N,"(expected about",N/512,")")
print("same pattern of M^-1:",sum(1 for s in samples if s['Mi_pattern']==real['Mi_pattern']))
print("same pattern M and M^-1:",sum(1 for s in samples if s['Mi_pattern']==real['Mi_pattern'] and s['pattern']==real['pattern']))
print("charpoly irreducible fraction:",sum(1 for s in samples if s['irr'])/N,"(1/3 expected; real: irreducible)")
irrs=[s for s in samples if s['irr']]
print("among irreducible: smooth-part order full (alpha^(n/q)!=1 for all 7 known primes):",sum(1 for s in irrs if s['full']),"of",len(irrs),"; real: ",True)
print("legendre T -1 frac:",sum(1 for s in samples if s['legT']==-1)/N,"legendre S -1 frac:",sum(1 for s in samples if s['legS']==-1)/N,"; real legT,legS:",real['legT'],real['legS'])
print("min entry bit length distribution (random):",sorted(Counter(s['minbits'] for s in samples).items()),"; real:",real['minbits'])
print("M^2 MDS in all samples:",all(s['M2mds'] for s in samples))
print("joint: irreducible and leg(det)=-1 and full-smooth-order frac:",sum(1 for s in samples if s['irr'] and s['legdet']==-1 and s['full'])/N)
