from common import *
from mpmath import mp, gammainc, binomial
import itertools, collections
mp.dps=30
used=[0,1,2,3,4,5,60,61,62,63]
allc=[RC[r][l] for r in range(64) for l in range(3)]
def chi2p(obs,exp):
    x=sum((o-e)**2/e for o,e in zip(obs,exp)); df=len(obs)-1
    return x,df,float(gammainc(df/2,x/2,mp.inf,regularized=True))
print('=== 3. top byte / bit length (192 constants)')
tb=[v>>248 for v in allc]
print('max top byte',hex(max(tb)),'min',hex(min(tb)),' any value >=2^254?',any(v>>254 for v in allc), '(p-2^254)/p = 2^%.1f'%l2((P-(1<<254))/P))
for nb,w in ((64,1),(16,4),(8,8),(4,16),(2,32)):
    obs=[0]*nb
    for t in tb: obs[t//w]+=1
    x,df,pv=chi2p(obs,[192/nb]*nb); print(f' bins {nb} (width {w}): chi2={x:.2f} df={df} p={pv:.3f}',obs if nb<=16 else '')
bl=collections.Counter(v.bit_length() for v in allc)
print('bit-length counts',sorted(bl.items()))
obs=[];exp=[]
for L in range(254,247,-1):
    obs.append(bl.get(L,0)); exp.append(192*2**-(254-L+1))
obs.append(sum(c for L,c in bl.items() if L<248)); exp.append(192*2**-7)
print(' bitlen expected',[round(e,1) for e in exp],'obs',obs,'chi2 p=%.3f'%chi2p(obs,exp)[2])
print(' min bitlen',min(bl))
ham=[bin(v).count('1') for v in allc]
mean=sum(ham)/192; print(' Hamming weight mean %.2f (expect ~127 over 254 bits; se=%.2f)'%(mean,math.sqrt(63.5)/math.sqrt(192)))
low=[v&0xff for v in allc]
obs=[0]*8
for t in low: obs[t//32]+=1
print(' low byte, 8 bins:',obs,'p=%.3f'%chi2p(obs,[24]*8)[2])
print(' used30 top byte (8 bins of 8):',[sum(1 for r in used for l in range(3) if 8*b<=RC[r][l]>>248<8*b+8) for b in range(8)])
print(' parity: odd count',sum(v&1 for v in allc),'of 192')
print('=== 5. Legendre symbols')
leg=lambda a:(1 if pow(a%P,(P-1)//2,P)==1 else -1)
qr=sum(leg(v)==1 for v in allc)
pv=2*min(sum(binomial(192,k) for k in range(0,qr+1)),sum(binomial(192,k) for k in range(qr,193)))/2**192
print('QR count among 192:',qr,' two-sided binomial p~%.3f'%float(pv))
for l in range(3): print(' lane',l,'QR count over 64 rounds',sum(leg(RC[r][l])==1 for r in range(64)))
print(' per-round Legendre pattern (+ QR / - NR) for used rounds:')
for r in used: print('  R%d'%r,''.join('+' if leg(RC[r][l])==1 else '-' for l in range(3)))
seq=[leg(v) for v in allc]; runs=1+sum(seq[i]!=seq[i+1] for i in range(191))
print(' runs in 192-sequence:',runs,'expected ~96 +-%.1f'%(math.sqrt(191)/2))
X=(1<<65)+RC[0][2]; K=pow(X,5,P)
print(' Legendre X=2^65+c02:',leg(X),' K=X^5:',leg(K),'(same, 5 odd)')
print(' Legendre MDS entries',[[leg(M[i][j]) for j in range(3)] for i in range(3)])
det=(M[0][0]*(M[1][1]*M[2][2]-M[1][2]*M[2][1])-M[0][1]*(M[1][0]*M[2][2]-M[1][2]*M[2][0])+M[0][2]*(M[1][0]*M[2][1]-M[1][1]*M[2][0]))%P
print(' det',hex(det),'leg',leg(det))
m4=matvec(M,[0,RC[4][1],RC[4][2]])
e60_r1=[(RC[60][i]+m4[i])%P for i in range(3)]
e5=[(RC[5][i]+m4[i])%P for i in range(3)]
m5=matvec(M,[0,e5[1],e5[2]])
e60_r2=[(RC[60][i]+m5[i])%P for i in range(3)]
print(' effective r=1: R60eff',[hex(v) for v in e60_r1],'legendre',[leg(v) for v in e60_r1])
print(' effective r=2: R5eff',[hex(v) for v in e5],'leg',[leg(v) for v in e5])
print('                R60eff',[hex(v) for v in e60_r2],'leg',[leg(v) for v in e60_r2])
print(' bitlens eff', [v.bit_length() for v in e60_r1],[v.bit_length() for v in e5],[v.bit_length() for v in e60_r2])
print('=== 4. relations among effective constants')
def rep(name,vals):
    rel=lll_relations(vals); k=len(vals); n=norm(rel[0])
    print(f' {name}: k={k} shortest 2^{l2(n):.2f} GH 2^{l2(gh(k)):.2f} ratio {n/gh(k):.2f} coefs {rel[0] if n<30 else "(generic)"}')
mds=[M[i][j] for i in range(3) for j in range(3)]
eff1=[X]+[RC[r][l] for r in (1,2,3) for l in range(3)]+[RC[4][0]]+e60_r1+[RC[r][l] for r in (61,62,63) for l in range(3)]
eff2=[X]+[RC[r][l] for r in (1,2,3) for l in range(3)]+[RC[4][0],e5[0]]+e60_r2+[RC[r][l] for r in (61,62,63) for l in range(3)]
rep('eff r=1 (X,R1-3,c4_0,R60eff,R61-63)',eff1)
rep('eff r=1 +1+MDS',eff1+[1]+mds)
rep('eff r=2 (X,R1-3,c4_0,R5eff0,R60eff,R61-63)',eff2)
rep('eff r=2 +1+MDS',eff2+[1]+mds)
rep('R60eff r1 + R60 raw + m4',e60_r1+list(RC[60])+m4+[1])
rep('R60eff r2 + R60 raw + m5',e60_r2+list(RC[60])+m5+[1])
rep('carried lanes (m4,m5) and constants of R4,R5',m4+m5+list(RC[4])+list(RC[5])+[1])
rep('PLANTED eff: eff1[3]=5*eff1[4]-2*eff1[9]',eff1[:3]+[(5*eff1[4]-2*eff1[9])%P]+eff1[4:])
print('=== 5b. X = 2^65+c02 special properties')
print(' X =',hex(X),'bits',X.bit_length(),' K=X^5=',hex(K))
print(' X mod small primes:',{q:X%q for q in (2,3,5,7,11,13,17,19,23,29,31,37,41,43,47)})
print(' trailing zero bits of X:',(X&-X).bit_length()-1,' of c02:',(RC[0][2]&-RC[0][2]).bit_length()-1)
sq=pow(-1,(P-1)//4,P) if False else None
# sqrt(-1): g^((p-1)/4)
for g in range(2,50):
    t=pow(g,(P-1)//4,P)
    if pow(t,2,P)==P-1: sq=t;break
fixed={'0':0,'1':1,'-1':P-1,'i':sq,'-i':P-sq}
for nm,f in fixed.items():
    d=(X-f)%P; d=min(d,P-d); print(f'  |X-({nm})| = 2^{l2(d):.2f}')
for nm,f in {'p/2':(P-1)//2,'p/3':P//3,'2^254':1<<254,'2^64':1<<64,'2^65':1<<65}.items():
    d=(X-f)%P; d=min(d,P-d); print(f'  |X-({nm})| = 2^{l2(d):.2f}')
Cc=4852402207910482324454106387152561316357015077916052529702775169
assert (P-1)==(2**32)*3*463*Cc
def smooth_order(a):
    b=pow(a,Cc,P)
    ordb=2**32*3*463
    for q in (2,3,463):
        while ordb%q==0 and pow(b,ordb//q,P)==1: ordb//=q
    return ordb
def fact(n):
    out={}
    for q in (2,3,463):
        while n%q==0: n//=q; out[q]=out.get(q,0)+1
    return out
print(' smooth part of ord(X) (2^a 3^b 463^c):',fact(smooth_order(X)),' ord(K) smooth:',fact(smooth_order(K)))
e=1;hit=None
for n in range(1,3001):
    e=e*5%(P-1)
    if pow(X,e,P)==X: hit=n;break
print(' x->x^5 returns X within 3000 steps?',hit)
v2=collections.Counter(fact(smooth_order(v)).get(2,0) for v in allc)
print(' v2(smooth ord) distribution over 192 constants',sorted(v2.items()),'(expected counts 96,48,24,...: P(v2=k)=2^-(k+1) for k<32, 0 -> 96)')
print(' cubes: %d of 192 (exp 64);  463rd powers: %d (exp 0.41); 4th powers: %d (exp 48)'%(
  sum(pow(v,(P-1)//3,P)==1 for v in allc),sum(pow(v,(P-1)//463,P)==1 for v in allc),sum(pow(v,(P-1)//4,P)==1 for v in allc)))
print(' X cube?',pow(X,(P-1)//3,P)==1,' X 4th power?',pow(X,(P-1)//4,P)==1,' X 463rd power?',pow(X,(P-1)//463,P)==1)
print('=== 6. pair relations over all 64*63 ordered round pairs')
def cross(a,b): return [(a[1]*b[2]-a[2]*b[1])%P,(a[2]*b[0]-a[0]*b[2])%P,(a[0]*b[1]-a[1]*b[0])%P]
def det3(a,b,c): return sum(x*y for x,y in zip(cross(a,b),c))%P
def adj(A):
    c=lambda i,j:(A[(i+1)%3][(j+1)%3]*A[(i+2)%3][(j+2)%3]-A[(i+1)%3][(j+2)%3]*A[(i+2)%3][(j+1)%3])%P
    d=(A[0][0]*c(0,0)+A[0][1]*c(0,1)+A[0][2]*c(0,2))%P
    di=inv(d)
    return [[c(j,i)*di%P for j in range(3)] for i in range(3)]
Mi=adj(M); I=[[1,0,0],[0,1,0],[0,0,1]]
assert [[sum(M[i][k]*Mi[k][j] for k in range(3))%P for j in range(3)] for i in range(3)]==I
def mpow(k):
    A=M if k>0 else Mi
    R=I
    for _ in range(abs(k)): R=[[sum(R[i][t]*A[t][j] for t in range(3))%P for j in range(3)] for i in range(3)]
    return R
Mk={k:mpow(k) for k in range(-8,9)}
exact=0;col=0;tested=0
for r in range(64):
    for s in range(64):
        if r==s: continue
        for k in range(-8,9):
            v=matvec(Mk[k],list(RC[r])); tested+=1
            if v==list(RC[s]): exact+=1; print('  EXACT c_%d = M^%d c_%d'%(s,k,r))
            if cross(v,list(RC[s]))==[0,0,0]: col+=1; print('  COLLINEAR c_%d || M^%d c_%d'%(s,k,r))
print(f' tested {tested} (ordered pair, k in -8..8) cases; exact {exact}; collinear {col}')
span=0;cnt=0
for r in range(64):
    for s in range(64):
        if r==s: continue
        c=list(RC[r]);mc=matvec(M,c)
        for A,B in ((c,mc),(c,matvec(Mi,c)),(mc,matvec(M,mc))):
            cnt+=1
            if det3(A,B,list(RC[s]))==0: span+=1; print('  COPLANAR',r,s)
print(f' c_s in plane span(c_r, M^+-1 c_r)-type tests: {cnt}, hits {span}')
tri=0;cn=0
for a,b,c in itertools.combinations(range(64),3):
    cn+=1
    if det3(list(RC[a]),list(RC[b]),list(RC[c]))==0: tri+=1;print('  det0',a,b,c)
print(f' det[c_a,c_b,c_c]=0 triples: {tri} of {cn}')
def gauss(a,mod):
    u=(1,a%mod);v=(0,mod)
    dot=lambda x,y:x[0]*y[0]+x[1]*y[1]
    while True:
        if dot(u,u)>dot(v,v): u,v=v,u
        mu=dot(u,v)//dot(u,u)
        # round to nearest
        if 2*(dot(u,v)-mu*dot(u,u))>dot(u,u): mu+=1
        if mu==0: break
        v=(v[0]-mu*u[0],v[1]-mu*u[1])
    return u
best=[]
for a in range(192):
    for b in range(192):
        if a==b: continue
        ratio=allc[a]*inv(allc[b])%P
        u=gauss(ratio,P); nm=math.sqrt(u[0]**2+u[1]**2)
        best.append((nm,a,b))
best.sort()
print(' smallest "c_a/c_b = n/m" lattice vector over all 192*191 ordered lane pairs: 2^%.2f (typical shortest 2^127.5; expected minimum over ~18k unordered pairs ~2^%.1f)'%(l2(best[0][0]),127.5-0.5*math.log2(18336)),'pair(lane idx=3*round+lane)',best[0][1:])
print(' median shortest-vector 2^%.2f'%l2(best[len(best)//2][0]))
print(' smallest signed constant: 2^%.2f'%l2(min(min(v,P-v) for v in allc)))
