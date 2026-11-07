from u5_lib import *
import itertools
T,S,D = charpoly(MDS); K = F3(T,S,D); al=(0,1,0)
cj = json.load(open("cauchy.json")); xs=[int(x,16) for x in cj["xs"]]; ys=[int(y,16) for y in cj["ys"]]
H = lambda L: [hex(x) for x in L]
def sgn(a):
    a%=P; return a if a<=P//2 else a-P
print("=== Q4 Cauchy relations ===")
quant = {}
for i in range(3):
    for j in range(i+1,3):
        quant[f"x{j}-x{i}"]=(xs[j]-xs[i])%P; quant[f"y{j}-y{i}"]=(ys[j]-ys[i])%P
for i in range(3):
    for j in range(3): quant[f"x{i}+y{j}"]=(xs[i]+ys[j])%P
for i in range(3): quant[f"x{i}"]=xs[i]; quant[f"y{i}"]=ys[i]
quant["detM"]=det3(MDS); quant["T"]=T; quant["S"]=S
for k in ["x1-x0","x2-x0","x2-x1","y1-y0","y2-y0","y2-y1"]:
    print(" ",k,hex(quant[k]), "signed bits", abs(sgn(quant[k])).bit_length(), "legendre",legendre(quant[k]))
names=list(quant); found=[]
for a in names:
    for b in names:
        if a>=b or quant[b]==0 or quant[a]==0: continue
        r = quant[a]*inv(quant[b])%P
        for v in range(1,61):
            u = r*v%P
            if u>P//2: u-=P
            if abs(u)<=60 and u!=0:
                found.append((a,b,u,v)); break
print("pairs of Cauchy quantities with small-rational ratio u/v (|u|,v<=60):", found)
v4=[quant[k] for k in ["x1-x0","x2-x0","y1-y0","y2-y0"]]
lin=[c for c in itertools.product(range(-4,5),repeat=4) if any(c) and sum(ci*vi for ci,vi in zip(c,v4))%P==0]
print("small integer linear relations (|c|<=4) among x1-x0,x2-x0,y1-y0,y2-y0:", lin)
print("(x1-x0)(y2-y0)-(x2-x0)(y1-y0) =", hex((v4[0]*v4[3]-v4[1]*v4[2])%P))
cons=[(r,i,RC[r][i]) for r in range(64) for i in range(3)]
hits=[]
for (r,i,c) in cons:
    for k,q in quant.items():
        if q==0: continue
        rr=c*inv(q)%P
        for v in range(1,13):
            u=rr*v%P
            if u>P//2: u-=P
            if abs(u)<=12 and u!=0: hits.append((r,i,k,u,v)); break
print("round constants that are small-rational multiples (|u|,v<=12) of a Cauchy quantity:",hits)
eqs=[(r,i,k) for (r,i,c) in cons for k,q in quant.items() if c==q or c==(-q)%P]
print("round constants equal to +-Cauchy quantity:",eqs)
print("Legendre x-diffs:",[legendre(quant[k]) for k in ["x1-x0","x2-x0","x2-x1"]],"y-diffs:",[legendre(quant[k]) for k in ["y1-y0","y2-y0","y2-y1"]])
print("Legendre M:",[[legendre(MDS[i][j]) for j in range(3)] for i in range(3)])
def cdet():
    num=1
    for i in range(3):
        for j in range(i+1,3): num=num*(xs[j]-xs[i])*(ys[j]-ys[i])%P
    den=1
    for i in range(3):
        for j in range(3): den=den*(xs[i]+ys[j])%P
    return num*inv(den)%P
print("Cauchy det formula == det M:",cdet()==det3(MDS))
Mi=matinv(MDS)
def pr(f,idx):
    r=1
    for t in idx: r=r*f(t)%P
    return r
def invent(j,i):
    num=pr(lambda k:xs[i]+ys[k],range(3))*pr(lambda k:xs[k]+ys[j],range(3))%P
    den=(xs[i]+ys[j])*pr(lambda k:xs[i]-xs[k],[k for k in range(3) if k!=i])*pr(lambda k:ys[j]-ys[k],[k for k in range(3) if k!=j])%P
    return num*inv(den)%P
print("closed Cauchy inverse formula (M^-1)_{ji} matches:", all(invent(a,b)==Mi[a][b] for a in range(3) for b in range(3)))
print("M^-1 Legendre:",[[legendre(Mi[i][j]) for j in range(3)] for i in range(3)])
print("M^-1 Cauchy-like (1/entries second difference zero):", all(((inv(Mi[i][j])-inv(Mi[i][0])-inv(Mi[0][j])+inv(Mi[0][0]))%P)==0 for i in range(3) for j in range(3)))
Xd=[[xs[i] if i==j else 0 for j in range(3)] for i in range(3)]; Yd=[[ys[i] if i==j else 0 for j in range(3)] for i in range(3)]
A=matmul(Yd,Mi); B=matmul(Mi,Xd)
Cm=[[(A[i][j]+B[i][j])%P for j in range(3)] for i in range(3)]
one=[1,1,1]
u=matvec(Mi,one); w=[sum(one[i]*Mi[i][j] for i in range(3))%P for j in range(3)]
print("Y M^-1 + M^-1 X == -(M^-1 1)(1^T M^-1):", all((Cm[i][j]+u[i]*w[j])%P==0 for i in range(3) for j in range(3)))
print("=== Q5/Q6 planes ===")
n = Mi[2]; print("normal n = row2 of M^-1:",H(n))
print("n . col_j of M:",[sum(n[i]*MDS[i][j] for i in range(3))%P for j in range(3)])
d6 = [0, MDS[0][2], (-MDS[0][1])%P]
Md6=matvec(MDS,d6)
print("X6 trail d=(0,M02,-M01); (M d)_0 =",Md6[0]," (Md)_1,(Md)_2 nonzero:",Md6[1]!=0,Md6[2]!=0, " n.d =",hex(sum(n[i]*d6[i] for i in range(3))%P))
L=[[0,MDS[i][2],(-MDS[i][1])%P] for i in range(3)]
print("L_i = {v0=0} ^ {(Mv)_i=0} direction (0,M_i2,-M_i1); L_0 is the X6 vector")
print("  slope relation: -M_i1/M_i2 == -(x_i+y_2)/(x_i+y_1)?", all((-MDS[i][1]*inv(MDS[i][2]))%P==(-(xs[i]+ys[2])*inv(xs[i]+ys[1]))%P for i in range(3)))
print("  n . L_i (is L_i in the P0 direction plane):",[hex(sum(n[k]*L[i][k] for k in range(3))%P) for i in range(3)])
u0 = [0,0xd0c2efd6472f12a3c26fa4b7d25b1e487a7435d30f8be81adc8933c6f3c72ee,0x2138c8da8b0c7ae44b222b4b29badda95c6202ee95282be4223d85aa2b0456f6]
print("  atlas line u = {v0=0}^P0dir: n.u =",sum(n[k]*u0[k] for k in range(3))%P)
for i in range(3): print(f"   row{i}.u =", hex(sum(MDS[i][k]*u0[k] for k in range(3))%P))
M2=matmul(MDS,MDS)
for i in range(3):
    v=[(M2[i][1]*MDS[k][0]-M2[i][0]*MDS[k][1])%P for k in range(3)]
    print(f"  line P_{i}^P0dir = M2[{i}][1]*col0 - M2[{i}][0]*col1 =",H(v))
def cross(a,b): return [(a[1]*b[2]-a[2]*b[1])%P,(a[2]*b[0]-a[0]*b[2])%P,(a[0]*b[1]-a[1]*b[0])%P]
for i in range(3):
    for j in range(i+1,3):
        c=cross(MDS[i],MDS[j]); k3=3-i-j
        rat=[c[k]*inv(Mi[k][k3])%P for k in range(3)]
        print(f"  P_{i}^P_{j} direction = cross(row{i},row{j}) = const * column {k3} of M^-1: ratios equal:", len(set(rat))==1, " const=",hex(rat[0]), " det M =",hex(det3(MDS)))
print("  (so the 3 pairwise plane-intersection lines are the columns of M^-1; the 3 planes Pi={v:(Mv)_i=0} are M^-1 e_i^perp)")
print("=== Q7 Krylov / F_{p^3} picture ===")
e0=[1,0,0]; k1=matvec(MDS,e0); k2=matvec(MDS,k1)
Kry=[[e0[i],k1[i],k2[i]] for i in range(3)]
Kinv=matinv(Kry)
def phi(v):
    c=matvec(Kinv,v); return (c[0],c[1],c[2])
tr=[K.trace(K.pw(al,k)) for k in range(5)]
G=[[tr[j+k] for k in range(3)] for j in range(3)]
Gi=matinv(G)
beta=[tuple(matvec(Gi,Kry[i])) for i in range(3)]
phis=[phi([1 if k==i else 0 for k in range(3)]) for i in range(3)]
for i in range(3): print(f"phi(e{i}) =",H(phis[i]))
for i in range(3): print(f"beta_lane{i} =",H(beta[i]))
vv=[random.randrange(P) for _ in range(3)]
ph=phi(vv)
for i in range(3): assert K.trace(K.mul(beta[i],ph))==vv[i]
assert phi(matvec(MDS,vv))==K.mul(al,ph)
print("verified: phi(Mv)=alpha*phi(v); v_i = Tr(beta_i*phi(v))")
bout=K.mul(al,beta[0]); print("output functional beta_out = alpha*beta_0 =",H(bout))
nbeta=tuple(matvec(Gi,[sum(n[i]*Kry[i][k] for i in range(3))%P for k in range(3)]))
print("plane-normal functional beta_n (n.v = Tr(beta_n phi(v))) =",H(nbeta))
print("  beta_n vs alpha^-1 * beta_2 (since n=row2 of M^-1 => n.v = (M^-1 v)_2):", nbeta==K.mul(K.inv(al),beta[2]))
for name,el in [("phi(e1)",phis[1]),("phi(e2)",phis[2]),("beta0",beta[0]),("beta1",beta[1]),("beta2",beta[2]),("beta_n",nbeta),("beta_out",bout)]:
    iv=K.inv(el)
    print(f"  {name}: norm {hex(K.norm(el))} trace {hex(K.trace(el))} leg(norm) {legendre(K.norm(el))} | alpha^2-coeff zero: {el[2]==0}; inverse alpha^2-coeff zero: {iv[2]==0}")
for a,b in [(1,0),(2,0),(2,1)]:
    r=K.mul(beta[a],K.inv(beta[b])); print(f"  beta{a}/beta{b} =",H(r)," norm",hex(K.norm(r)))
# lane-0 / e_i functional pairing  Tr(beta_i phi(e_j)) = delta_ij
print("  Tr(beta_i phi(e_j)) matrix:",[[K.trace(K.mul(beta[i],phis[j])) for j in range(3)] for i in range(3)])
print("=== eigenvector vs Cauchy ===")
# eigenvector of M for alpha, as above
def eigvec(lam):
    R=[[ (MDS[i][j],0,0) if i!=j else K.sub((MDS[i][j],0,0),lam) for j in range(3)] for i in range(3)]
    def cr(u,v):
        return [K.sub(K.mul(u[1],v[2]),K.mul(u[2],v[1])),K.sub(K.mul(u[2],v[0]),K.mul(u[0],v[2])),K.sub(K.mul(u[0],v[1]),K.mul(u[1],v[0]))]
    v=cr(R[0],R[1]); i0=K.inv(v[0]); return [K.mul(x,i0) for x in v]
ev=eigvec(al)
# phi relation: phi of F_{p^3}-eigvec? the vector with coordinates in K: eigenvector's coords vs lane functionals
# check: v_i = beta-like: ev[i] proportional to inverse of ... test ev[i]*(alpha-ish) patterns: is ev[i] = c/(x_i + t) for t in K?
t_candidates=[]
# solve t from ev0*(x0+t)=ev1*(x1+t): t=(ev1*x1-ev0*x0)/(ev0-ev1)
t=K.mul(K.sub(K.smul(xs[1],ev[1]),K.smul(xs[0],ev[0])),K.inv(K.sub(ev[0],ev[1])))
c=K.mul(ev[0],K.add((xs[0],0,0),t))
ok2=K.mul(ev[2],K.add((xs[2],0,0),t))==c
print("eigenvector coordinates v_i = c/(x_i + t) for a single t in F_{p^3}?",ok2)
if ok2:
    print("  t =",H(t)); print("  t == alpha-related? t+alpha,  t-alpha:",H(K.add(t,al)),H(K.sub(t,al)))
    print("  t is in F_p:", t[1]==0 and t[2]==0)
    print("  also test v_i = c/(x_i - alpha)?", K.mul(ev[0],K.sub((xs[0],0,0),al))==K.mul(ev[1],K.sub((xs[1],0,0),al)))
