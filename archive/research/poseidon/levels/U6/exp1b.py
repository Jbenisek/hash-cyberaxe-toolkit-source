from grain import *
import grain, math
print('=== 1. Grain re-derivation details')
# instrument: count LFSR steps
class GC(G):
    steps=0
    def step(s):
        GC.steps+=1; return super().step()
g=GC(mk())
print('LFSR steps after 160-bit warm-up:',GC.steps)
rej_per_round=[];rcs=[]
for r in range(64):
    rj=0;row=[]
    for l in range(3):
        v,x=g.fe(); rj+=x; row.append(v)
    rej_per_round.append(rj); rcs.append(row)
print('RC match pinned:',sum(rcs[r][l]==pr.RC[r][l] for r in range(64) for l in range(3)),'/192')
print('LFSR steps consumed by 192 constants (incl. rejections):',GC.steps,' output bits taken = steps/2 approx; rejected 255-bit draws:',sum(rej_per_round))
print('rejections per round (R0..R63):',rej_per_round)
used=[0,1,2,3,4,5,60,61,62,63]
print('rejections in used rounds:',{r:rej_per_round[r] for r in used}, 'total used',sum(rej_per_round[r] for r in used))
# MDS: raw draws
raw=[]
for _ in range(6):
    bs=[g.bit() for _ in range(255)]
    raw.append(int(''.join(map(str,bs)),2))
print('raw MDS draws >= p (needing reduction)?',[v>=P for v in raw],' (drawn WITHOUT rejection, reduced mod p)')
xs=[v%P for v in raw[:3]];ys=[v%P for v in raw[3:]]
Mm=[[pow((xs[i]+ys[j])%P,P-2,P) for j in range(3)] for i in range(3)]
print('MDS from Cauchy(xs,ys) match pinned:',Mm==[list(r) for r in pr.MDS])
print('xs =',[hex(v) for v in xs]);print('ys =',[hex(v) for v in ys])
print('raw draws as drawn:',[hex(v) for v in raw])
print('x_i+y_j never 0, xs distinct, ys distinct:',len(set(xs))==3,len(set(ys))==3,all((x+y)%P for x in xs for y in ys))
print('consecutive-draw note: the 2 reduced draws: raw0-p=%s raw1-p=%s'%(hex(raw[0]-P) if raw[0]>=P else '-',hex(raw[1]-P) if raw[1]>=P else '-'))
print('=== 1b. what if regenerated for the reduced round counts (we do NOT; constants stay R_P=56)')
for rp in (1,2,56,57,55):
    g2=G(mk(rp=rp)); c0=g2.fe()[0]
    print(f' R_P={rp}: first constant {hex(c0)[:18]}.. equals pinned: {c0==pr.RC[0][0]}')
for variant,kw in (('sbox=1(inverse)',dict(sbox=1)),('t=2',dict(t=2)),('R_F=6',dict(rf=6)),('nbits=254',dict(nb=254)),('field=0',dict(field=0))):
    g2=G(mk(**kw)); c0=g2.fe()[0]; print(f' {variant}: first const equals pinned: {c0==pr.RC[0][0]}')
print(' discard 159 / 161 bits warm-up:',[G(mk(),d).fe()[0]==pr.RC[0][0] for d in (159,161)])
print('=== TOY: same Grain generation over small primes, exact null rates for the relation detectors')
def toy(q,seed_rf=8,rp=56):
    nb=q.bit_length()
    st=mk(nb=nb,rf=seed_rf,rp=rp); g=G(st)
    def fe_rej():
        while True:
            v=int(''.join(str(g.bit()) for _ in range(nb)),2)
            if v<q: return v
    rc=[[fe_rej() for _ in range(3)] for _ in range(64)]
    def fe_raw(): return int(''.join(str(g.bit()) for _ in range(nb)),2)%q
    xs=[fe_raw() for _ in range(3)];ys=[fe_raw() for _ in range(3)]
    Mq=[[pow((xs[i]+ys[j])%q,q-2,q) for j in range(3)] for i in range(3)]
    return rc,Mq
def matv(A,v,q): return [sum(A[i][j]*v[j] for j in range(3))%q for i in range(3)]
def inv3(A,q):
    c=lambda i,j:(A[(i+1)%3][(j+1)%3]*A[(i+2)%3][(j+2)%3]-A[(i+1)%3][(j+2)%3]*A[(i+2)%3][(j+1)%3])%q
    d=(A[0][0]*c(0,0)+A[0][1]*c(0,1)+A[0][2]*c(0,2))%q
    if d==0: return None
    di=pow(d,q-2,q); return [[c(j,i)*di%q for j in range(3)] for i in range(3)]
def cross(a,b,q): return [(a[1]*b[2]-a[2]*b[1])%q,(a[2]*b[0]-a[0]*b[2])%q,(a[0]*b[1]-a[1]*b[0])%q]
for q in (257,12289,65537,1000003,7340033):
    ok5=math.gcd(5,q-1)==1
    if not ok5: print(q,'gcd(5,q-1)!=1 skipped'); continue
    v2=((q-1)&-(q-1)).bit_length()-1
    rc,Mq=toy(q); Mi=inv3(Mq,q)
    if Mi is None: print(q,'singular M'); continue
    Mk={0:[[int(i==j) for j in range(3)] for i in range(3)]}
    cur=Mk[0]
    for k in range(1,9):
        cur=[[sum(cur[i][t]*Mq[t][j] for t in range(3))%q for j in range(3)] for i in range(3)];Mk[k]=cur
    cur=Mk[0]
    for k in range(1,9):
        cur=[[sum(cur[i][t]*Mi[t][j] for t in range(3))%q for j in range(3)] for i in range(3)];Mk[-k]=cur
    col=0;ex=0;n=0
    for r in range(64):
        for s in range(64):
            if r==s: continue
            for k in range(-8,9):
                v=matv(Mk[k],rc[r],q);n+=1
                if v==rc[s]: ex+=1
                if cross(v,rc[s],q)==[0,0,0]: col+=1
    tri=0;trn=0
    import itertools
    for a,b,c in itertools.combinations(range(64),3):
        trn+=1
        cr=cross(rc[a],rc[b],q)
        if sum(x*y for x,y in zip(cr,rc[c]))%q==0: tri+=1
    # expected: collinear prob ~ 1/q^2 per test actually (2 conditions); coplanar ~1/q
    print(f'q={q} (bits {q.bit_length()}, 2-adicity {v2}, gcd(5,q-1)=1): {n} (pair,k) tests: exact {ex} (expect ~{n/q**3:.3g}), collinear {col} (expect ~{n/q**2:.3g}); coplanar triples {tri}/{trn} (expect ~{trn/q:.3g}); M MDS-ish: det!=0')
