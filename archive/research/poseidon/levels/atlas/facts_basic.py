"""Exact small facts about the Orchard Poseidon target: field, S-box x^5, MDS, constants.
Run: python facts_basic.py   (prints a report; writes facts_basic.json)
All numbers are exact big-int computations on the pinned constants (read as data)."""

# Publication path adapter: resolve data paths from the extracted source tree.
def _hca_public_path_text(value):
    if "__HCA_WORKSPACE__/" not in value:
        return value
    import os as _hca_os
    from pathlib import Path as _hca_Path
    root = _hca_os.environ.get("HASHCYBERAXE_WORKSPACE")
    if root is None:
        here = _hca_Path(__file__).resolve().parent
        root = next((str(p) for p in (here, *here.parents) if (p / "research").is_dir()), None)
    if root is None:
        raise FileNotFoundError("Extract the research source tree, or set HASHCYBERAXE_WORKSPACE to its archive directory.")
    return value.replace("__HCA_WORKSPACE__/", str(_hca_Path(root).resolve()).replace("\\", "/") + "/")

import sys, os, json, random, math
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/orchard/impl'))
import poseidon_ref as R
P, RC, MDS = R.P, R.RC, R.MDS
out = {}
def inv(a): return pow(a, P-2, P)
def hx(a): return hex(a)
def sg(a):  # signed representative
    return a if a < P//2 else a-P

# ---------- field ----------
def is_prime(n):
    if n < 2: return False
    for q in (2,3,5,7,11,13,17,19,23,29,31,37):
        if n % q == 0: return n == q
    d, s = n-1, 0
    while d % 2 == 0: d//=2; s+=1
    for a in (2,3,5,7,11,13,17,19,23,29,31,37):
        x = pow(a,d,n)
        if x in (1,n-1): continue
        for _ in range(s-1):
            x = x*x % n
            if x == n-1: break
        else: return False
    return True
def rho_factor(n, budget=300000):
    """returns list of primes; unfactored composite cofactors appear as ('C', n)."""
    if n == 1: return []
    if is_prime(n): return [n]
    for q in (2,3,5,7,11,13,17,19,23,29,31,37,41,43,47):
        if n % q == 0: return [q]+rho_factor(n//q, budget)
    for attempt in range(3):
        c = random.randrange(1,n); x=y=random.randrange(n); d=1; steps=0
        f = lambda v:(v*v+c)%n
        while d==1 and steps<budget:
            x=f(x); y=f(f(y)); d=math.gcd(abs(x-y),n); steps+=1
        if 1 < d < n: return rho_factor(d,budget)+rho_factor(n//d,budget)
    return [('C', n)]
def factor(n):
    from collections import Counter
    return dict(sorted(Counter(rho_factor(n)).items(), key=lambda kv: str(kv[0]) if isinstance(kv[0],tuple) else '%080d'%kv[0]))
random.seed(1)
assert is_prime(P)
fac = factor(P-1)
two_adic = fac[2]
out['p_minus_1_factors'] = {str(k): v for k, v in fac.items()}
two_adic = fac[2]
print('p bits', P.bit_length(), 'p mod 5', P % 5, 'p mod 4', P % 4, 'p mod 3', P % 3, 'p mod 8', P%8)
print('p-1 =', ' * '.join((f'{k}^{v}' if v>1 else str(k)) if not isinstance(k,tuple) else 'C(%d bits, unfactored composite, %s)'%(k[1].bit_length(),k[1]) for k,v in fac.items()))
print('(rho budget 300k steps x3; the 212-bit cofactor is composite (Miller-Rabin) but not factored by this small run)')
print('gcd(5,p-1)=', math.gcd(5,P-1), ' 2-adicity', two_adic)
D = pow(5, -1, P-1)
print('d = 5^-1 mod p-1 =', hex(D), D.bit_length(),'bits')
print('p+1 factors', factor(P+1)); print('p^2+p+1 factors (cubic ext. subgroup):', factor(P*P+P+1))
# order of p mod 5 -> degrees of factors of x^4+x^3+x^2+x+1 over Fp
k=1
while pow(P,k,5)!=1: k+=1
print('ord of p mod 5 =', k, '=> Phi5 splits into', 4//k, 'irreducible factors of degree', k, 'over Fp (so x^5=c has exactly 1 root in Fp; 5th roots of 1 live in F_p^%d)'%k)
out['ord_p_mod_5']=k
# root of unity i
g = 5
while pow(g,(P-1)//2,P)==1: g+=1
I = pow(g,(P-1)//4,P)
assert I*I%P==P-1
I = min(I, P-I)
print('sqrt(-1) =', hex(I), 'and', hex(P-I), ' (smaller rep first)')
fixed = [0,1,P-1,I,P-I]
assert all(pow(x,5,P)==x for x in fixed)
# x^5 = x  <=> x^4=1 : exactly {0,1,-1,i,-i}
# x^5 = -x <=> x^4=-1: primitive 8th roots
z8 = pow(g,(P-1)//8,P)
eights = sorted({pow(z8,k,P) for k in (1,3,5,7)})
assert all(pow(x,5,P)==P-x for x in eights)
print('x^5=-x solutions (x^4=-1): 4 of them', [hex(x) for x in eights])
out['sqrt_m1']=[hx(I),hx(P-I)]
out['x4_eq_minus1']=[hx(x) for x in eights]
# cycle structure of x->x^5 on F*: on elements of order m cycles have length ord_m(5)
def ord_mod(a,m,facm):
    o = m
    for q in facm:
        while o % q == 0 and pow(a,o//q,m)==1: o//=q
    return o
print('multiplicative order of 5 modulo each prime power of p-1 (cycle length of x->x^5 on elements of that order):')
for q,e in fac.items():
    if isinstance(q,tuple): print('  (unfactored composite cofactor: skipped)'); continue
    qe = q**e
    print('  mod %s^%d (%d bits): order of 5 = %s' % (q,e,qe.bit_length(), ord_mod(5,qe,[q]) if q!=2 else 2**(e-2)))
# 5 mod 2^32: order is 2^30
assert pow(5,2**30,2**32)==1 and pow(5,2**29,2**32)!=1
out['2^65']=hex(1<<65)
print('2^65 =',hex(1<<65),' < p, bits',(1<<65).bit_length(), ' is 2^65 a QR?', pow(1<<65,(P-1)//2,P)==1)
K_note = None
# ---------- constants ----------
print('\n=== constants: 64 rounds x 3 lanes ===')
flat = [(r,j,RC[r][j]) for r in range(64) for j in range(3)]
bl = [v.bit_length() for _,_,v in flat]
print('bit lengths: min',min(bl),'max',max(bl),'  count <250 bits:',sum(b<250 for b in bl),' <200:',sum(b<200 for b in bl),' <128:',sum(b<128 for b in bl))
vals = [v for _,_,v in flat]
print('distinct values', len(set(vals)), 'of 192; zero count', vals.count(0), '; equal to 1 or -1:', sum(v in (1,P-1) for v in vals))
neg = {(P-v)%P for v in vals}
print('any c == -c\' (opposite pairs):', len(neg & set(vals)))
mn = min(flat, key=lambda t: min(t[2], P-t[2]))
print('smallest |c| (signed) :', mn[0], mn[1], hex(min(mn[2],P-mn[2])), min(mn[2],P-mn[2]).bit_length(),'bits')
fixedset=set(fixed)
print('any constant in {0,+-1,+-i}:', [ (r,j) for r,j,v in flat if v in fixedset])
# square/ nonresidue fractions (heuristic randomness)
qr = sum(pow(v,(P-1)//2,P)==1 for v in vals)
print('quadratic residues among 192 constants:', qr)
# related constants: equal differences / ratios within a round
rel=[]
for r in range(64):
    a,b,c = RC[r]
    for (x,y,lab) in ((a,b,'01'),(a,c,'02'),(b,c,'12')):
        for q in (1,2,3,4,5,P-1,P-2):
            if (x - q*y)%P==0 or (x + q*y)%P==0: rel.append((r,lab,q))
print('simple relations c_i = +-k c_j (k<=5) within a round:', rel)
# between rounds
rel2=[]
for r in range(63):
    for j in range(3):
        for k in range(3):
            if (RC[r][j]-RC[r+1][k])%P==0: rel2.append((r,j,r+1,k))
print('equal constants between consecutive rounds:', rel2)
# does a constant vector row equal MDS-related? check c_{r+1} == M c_r?
n_mc = sum(1 for r in range(63) if [sum(MDS[i][j]*RC[r][j] for j in range(3))%P for i in range(3)]==list(RC[r+1]))
print('c_{r+1} == M c_r count:', n_mc)
out['rc_bits_min_max']=[min(bl),max(bl)]
# used rounds
print('\nused rounds table (original index, lane, hex, bits, signed-bits):')
used = list(range(0,6))+list(range(60,64))
for r in used:
    print(' round %2d: '%r + '  '.join('%s (%d)'%(hx(c), c.bit_length()) for c in RC[r]))
# ---------- MDS ----------
print('\n=== MDS ===')
M = [list(r) for r in MDS]
for i in range(3): print(' row',i,[hx(x) for x in M[i]], [x.bit_length() for x in M[i]])
def det2(a,b,c,d): return (a*d-b*c)%P
def det3(m):
    return (m[0][0]*det2(m[1][1],m[1][2],m[2][1],m[2][2]) - m[0][1]*det2(m[1][0],m[1][2],m[2][0],m[2][2]) + m[0][2]*det2(m[1][0],m[1][1],m[2][0],m[2][1]))%P
det = det3(M)
minors2 = [det2(M[a][c],M[a][d],M[b][c],M[b][d]) for a in range(3) for b in range(a+1,3) for c in range(3) for d in range(c+1,3)]
print('det', hx(det), '; all entries nonzero:', all(x for r in M for x in r), '; all 9 2x2 minors nonzero:', all(minors2), '; det nonzero:', det!=0, '=> MDS (branch number 4) PROVED by these 9+9+1 checks')
print('symmetric?', all(M[i][j]==M[j][i] for i in range(3) for j in range(3)))
# Cauchy test: M_ij = 1/(x_i + y_j)  <=>  N_ij = 1/M_ij = x_i + y_j (rank-one-additive)
N = [[inv(M[i][j]) for j in range(3)] for i in range(3)]
cauchy = all((N[i][j]-N[i][0]-N[0][j]+N[0][0])%P==0 for i in range(3) for j in range(3))
print('Cauchy form (1/M_ij additive: N_ij - N_i0 - N_0j + N_00 == 0) :', cauchy)
# choose x0=0 normalisation: x_i = N_i0 - N_00, y_j = N_0j
xs = [(N[i][0]-N[0][0])%P for i in range(3)]; ys=[N[0][j] for j in range(3)]
if cauchy:
    print(' one valid (x_i, y_j) with x_0=0:  x =',[hx(v) for v in xs],' y =',[hx(v) for v in ys])
    print(' x_i small? ', [sg(v).bit_length() for v in xs],' (shift freedom x->x+s,y->y-s)')
    out['cauchy_x']=[hx(v) for v in xs]; out['cauchy_y']=[hx(v) for v in ys]
    # M determinant formula for Cauchy: prod(x_j-x_i)(y_j-y_i)/prod(x_i+y_j)
    d = 1
    for i in range(3):
        for j in range(i+1,3): d = d*(xs[j]-xs[i])*(ys[j]-ys[i])%P
    for i in range(3):
        for j in range(3): d = d*inv((xs[i]+ys[j])%P)%P
    print(' Cauchy determinant formula matches:', d==det)
# trace, char poly
tr = sum(M[i][i] for i in range(3))%P
s2 = (det2(M[0][0],M[0][1],M[1][0],M[1][1]) + det2(M[0][0],M[0][2],M[2][0],M[2][2]) + det2(M[1][1],M[1][2],M[2][1],M[2][2]))%P
print('char poly  x^3 - T x^2 + S x - D  with  T=%s  S=%s  D=%s'%(hx(tr),hx(s2),hx(det)))
# polynomial mod f arithmetic (cubic)
def pmulmod(a,b,f):  # f monic cubic coeffs [f0,f1,f2] meaning x^3 = -(f2 x^2+f1 x+f0)
    r=[0]*5
    for i in range(3):
        for j in range(3): r[i+j]=(r[i+j]+a[i]*b[j])%P
    for k in (4,3):
        c=r[k]; r[k]=0
        for t in range(3): r[k-3+t]=(r[k-3+t]-c*f[t])%P
    return r[:3]
f = [(-det)%P, s2%P, (-tr)%P]   # x^3 + f2 x^2 + f1 x + f0, with f2=-T, f1=S, f0=-D
def ppow(e):
    res=[1,0,0]; base=[0,1,0]
    while e:
        if e&1: res=pmulmod(res,base,f)
        base=pmulmod(base,base,f); e>>=1
    return res
xp = ppow(P)
# gcd(x^p - x, f) trivial iff no roots; x^p - x mod f:
xpmx = [xp[0], (xp[1]-1)%P, xp[2]]
print('x^p - x mod charpoly =', [hx(c) for c in xpmx], ' => zero would mean split; nonzero & check roots:')
# test root existence: f has a root in Fp iff gcd(x^p-x,f)!=1; for a cubic: irreducible iff x^(p^3)==x mod f and gcd(x^p - x,f)=1 ; do it via x^p != x and x^(p^2)!= x
xp2 = xp
# compute x^(p^2)=(x^p)^p via compose: easier use ppow of ppow? do (x^p) as poly then raise to p
def pmodpow(base,e):
    res=[1,0,0]
    while e:
        if e&1: res=pmulmod(res,base,f)
        base=pmulmod(base,base,f); e>>=1
    return res
xp2 = pmodpow(xp,P); xp3 = pmodpow(xp2,P)
print(' x^(p^3) == x mod f :', xp3==[0,1,0], '; x^p == x mod f :', xp==[0,1,0], '; x^(p^2)==x:', xp2==[0,1,0])
irreducible = (xp3==[0,1,0]) and xp!=[0,1,0]
print(' => charpoly irreducible over Fp (no eigenvalue in Fp, no 1-dim or 2-dim invariant subspace over Fp):', irreducible)
out['charpoly_irreducible']=irreducible
# order of M divides p^3-1
def mmul(A,B): return [[sum(A[i][k]*B[k][j] for k in range(3))%P for j in range(3)] for i in range(3)]
Id=[[1 if i==j else 0 for j in range(3)] for i in range(3)]
def mpow(A,e):
    r=Id
    while e:
        if e&1: r=mmul(r,A)
        A=mmul(A,A); e>>=1
    return r
n3 = P**3-1
print(' M^(p^3-1)==I :', mpow(M,n3)==Id, ' (so order divides p^3-1 = (p-1)(p^2+p+1))')
# the exact order needs the full factorisation of p^3-1 (cofactors unfactored here); report only the proved divisibility and partial tests
known_primes=[q for q in list(fac)+list(factor(P*P+P+1)) if not isinstance(q,tuple)]
parts=[q for q in known_primes]
print(' for each known prime q | p^3-1: is M^((p^3-1)/q) == I ? ->', {q: mpow(M,n3//q)==Id for q in parts if n3%q==0})

# small powers all-nonzero (MDS-like?), inverse, minimal facts
M2=mmul(M,M); M3=mmul(M2,M); Mi=[[0]*3 for _ in range(3)]
# inverse via adjugate
def inv3(m):
    d=det3(m); di=inv(d)
    cof=[[((-1)**(i+j)*det2(*[m[a][b] for a in range(3) if a!=i for b in range(3) if b!=j]))%P for j in range(3)] for i in range(3)]
    return [[cof[j][i]*di%P for j in range(3)] for i in range(3)]
Minv=inv3(M); assert mmul(M,Minv)==Id
print(' M^-1 entries nonzero:', all(x for r in Minv for x in r), '; M^2 entries all nonzero:', all(x for r in M2 for x in r), '; M^3 nonzero:', all(x for r in M3 for x in r))
print(' row sums', [hx(sum(r)%P) for r in M], ' col sums', [hx(sum(M[i][j] for i in range(3))%P) for j in range(3)])
print(' M[0][1]/M[0][0] etc ratios (row 0):', [hx(M[0][j]*inv(M[0][0])%P) for j in range(3)])
# is M a scalar multiple of an involution? M^2 vs I
print(' M^2 == scalar*I:', M2[0][1]==0, '  M == M^T :', M==[list(c) for c in zip(*M)])
# 2-adic / QR of entries
print(' entries QR?', [[pow(x,(P-1)//2,P)==1 for x in r] for r in M])
# ---------- invariant-subspace / partial-round difference trail ----------
print('\n=== partial-round linear structure (difference space not seen by S-box of lane 0) ===')
# V1 = {d: d0=0} dim 2 passes round 4 (r=1) linearly. V2 = {d: d0=0 and (M d)_0=0} dim 1 passes two partial rounds (r=2).
# solve d0=0, M0*d=0 : d=(0,d1,d2), M01 d1+M02 d2=0
d2v = [0, M[0][2], (-M[0][1])%P]
chk = sum(M[0][j]*d2v[j] for j in range(3))%P
print('r=2: vector with d0=0 and (M d)_0 = 0 :', [hx(x) for x in d2v], ' check', chk)
Md = [sum(M[i][j]*d2v[j] for j in range(3))%P for i in range(3)]
print('   its image M d =', [hx(x) for x in Md], ' (image lane0 == 0, lanes 1,2 nonzero; after 2 rounds M(Md) =', [hx(sum(M[i][j]*Md[j] for j in range(3))%P) for i in range(3)],')')
# r=3: need d0=0, (Md)_0=0, (M^2 d)_0=0 -> only d=0 iff e0 cyclic for M^T
mat = [[1 if j==0 else 0 for j in range(3)], M[0], [M2[0][j] for j in range(3)]]
print('r=3: rows e0, e0M, e0M^2 determinant (nonzero => trail dimension 0):', hx(det3(mat)))
mat = [[1 if j==0 else 0 for j in range(3)], M[0]]
# ---------- constants carried through partial rounds (normal form) ----------
print('\n=== partial round constants normal form ===')
c4 = RC[4]
rest = [0, c4[1], c4[2]]
Mrest = [sum(M[i][j]*rest[j] for j in range(3))%P for i in range(3)]
print('M*(0,c4_1,c4_2) =', [hx(x) for x in Mrest])
print(' effect: lanes 1,2 constants of round 4 can be moved after the MDS; next round (r=1: round 60) adds c60 + M*(0,c41,c42)')
c60n = [(RC[60][i]+Mrest[i])%P for i in range(3)]
print(' r=1 round-60 effective constants:', [hx(x) for x in c60n])
out['r1_c60_effective']=[hx(x) for x in c60n]
c5=RC[5]
# r=2: round 5 effective lane0 constant c5_0 + Mrest_0 ; rest of round5: lane1,2: c5_i + Mrest_i, those carried forward
c5e=[(c5[i]+Mrest[i])%P for i in range(3)]
rest5=[0,c5e[1],c5e[2]]
Mrest5=[sum(M[i][j]*rest5[j] for j in range(3))%P for i in range(3)]
c60n2=[(RC[60][i]+Mrest5[i])%P for i in range(3)]
print(' r=2 round-5 effective lane-0 constant:', hx(c5e[0]), ' round-60 effective constants:', [hx(x) for x in c60n2])
out['r2_c5_effective_lane0']=hx(c5e[0]); out['r2_c60_effective']=[hx(x) for x in c60n2]
# verify against reference: rebuild hash with normal form
def hash_nf(nk,rho,r):
    s=[nk,rho,R.CAPACITY]
    for idx in range(4): s=R.round_full(s,idx)
    carry=[0,0,0]
    for idx in range(4,4+r):
        c=[(RC[idx][i]+carry[i])%P for i in range(3)]
        w=pow((s[0]+c[0])%P,5,P)
        s=[(M[i][0]*w+M[i][1]*s[1]+M[i][2]*s[2])%P for i in range(3)]  # lanes 1,2 constants carried, not added here
        carry=[sum(M[i][j]*[0,c[1],c[2]][j] for j in range(3))%P for i in range(3)]
    for idx in range(60,64):
        c=[(RC[idx][i]+carry[i])%P for i in range(3)]; carry=[0,0,0]
        s=[pow((s[i]+c[i])%P,5,P) for i in range(3)]
        s=R.mds_apply(s)
    return s[0]
ok=True
random.seed(7)
for r in (1,2):
    for _ in range(20):
        a,b=random.randrange(P),random.randrange(P)
        ok &= hash_nf(a,b,r)==R.hash_reduced(a,b,r)
print(' normal-form (constants of lanes 1,2 of partial rounds carried forward) reproduces hash_reduced on 40 random inputs:', ok)
# ---------- round 0 specifics ----------
print('\n=== round 0 / capacity ===')
c0=RC[0]
K = pow((CAP:=R.CAPACITY)+c0[2],5,P)
print('2^65 + c02 =', hx((CAP+c0[2])%P), ' bits', ((CAP+c0[2])%P).bit_length())
print('K = (2^65 + c0_2)^5 =', hx(K), ' (the constant that lane 2 contributes after round-0 S-box)')
out['K']=hx(K)
print('nk values making lane-0 S-box input a = nk + c00 in {0,1,-1,i,-i}  (S-box identity or zero):')
for lab,t in zip(('0','1','-1','i','-i'),fixed): print('   a=%-2s -> nk = %s'%(lab,hx((t-c0[0])%P)))
print('rho values making b = rho + c01 in {0,1,-1,i,-i}:')
for lab,t in zip(('0','1','-1','i','-i'),fixed): print('   b=%-2s -> rho = %s'%(lab,hx((t-c0[1])%P)))
print('lane-2 S-box input (2^65+c02) in fixed set?', (CAP+c0[2])%P in fixedset)
# plane after round 0: s = A*col0 + B*col1 + K*col2 ; (M^-1 s)_2 = K
s_test = R.round_full([123456789,987654321,CAP],0)
print('check (M^-1 s)_2 == K for round-0 output:', sum(Minv[2][j]*s_test[j] for j in range(3))%P==K)
print('so after round 0 the state lies on the affine plane  Minv[2].s = K ; row2 of M^-1 =', [hx(x) for x in Minv[2]])
out['Minv_row2']=[hx(x) for x in Minv[2]]
# special directions: lane i degree drop after round 0: M_i0 u^5 + M_i1 v^5 = 0
print('\n=== directions (u:v) of lines nk=a+u t, rho=b+v t on which lane i of round-0 output loses its top degree ===')
for i in range(3):
    ratio = (-M[i][1]*inv(M[i][0]))%P   # (u/v)^5 = -M_i1/M_i0
    uv = pow(ratio, D, P)
    assert pow(uv,5,P)==ratio
    print('  lane %d: u/v = %s  (unique in Fp since gcd(5,p-1)=1)'%(i,hx(uv)))
    out['dropdir_lane%d'%i]=hx(uv)
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'facts_basic.json'),'w'), indent=1)
