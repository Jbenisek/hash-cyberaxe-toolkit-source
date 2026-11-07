# BLAKE3 3-round probe: r2 length-cancellation start (55 vs 63 bytes, last chunk, CV=IV, flags 3,
# counter t free). Round 0 shared; rounds 1 encoded for A and B. Constraint: HW(stateA xor stateB)
# entering round 3 (after 2 rounds) <= W.  Usage: gen.py W out.cnf
import sys
from pysat.card import CardEnc, EncType
W = int(sys.argv[1]); out = sys.argv[2]
IV=[0x6A09E667,0xBB67AE85,0x3C6EF372,0xA54FF53A,0x510E527F,0x9B05688C,0x1F83D9AB,0x5BE0CD19]
SIG=[2,6,3,10,7,0,4,13,1,11,12,5,9,14,15,8]
nv=[0]; cl=[]
def new():
    nv[0]+=1; return nv[0]
T=new(); cl.append([T])
def word(): return [new() for _ in range(32)]
def const(x): return [T if (x>>i)&1 else -T for i in range(32)]
def xor2(a,b):
    out=[]
    for x,y in zip(a,b):
        z=new(); cl.extend([[-z,x,y],[-z,-x,-y],[z,-x,y],[z,x,-y]]); out.append(z)
    return out
def add(a,b):
    s=[]; c=-T
    for i in range(32):
        x,y=a[i],b[i]; z=new()
        cl.extend([[-z,x,y,c],[-z,x,-y,-c],[-z,-x,y,-c],[-z,-x,-y,c],[z,-x,-y,-c],[z,-x,y,c],[z,x,-y,c],[z,x,y,-c]])
        s.append(z)
        if i<31:
            n=new()
            cl.extend([[-n,x,y],[-n,x,c],[-n,y,c],[n,-x,-y],[n,-x,-c],[n,-y,-c]]); c=n
    return s
def rotr(a,n): return [a[(i+n)%32] for i in range(32)]
def G(v,a,b,c,d,mx,my):
    v[a]=add(add(v[a],v[b]),mx); v[d]=rotr(xor2(v[d],v[a]),16)
    v[c]=add(v[c],v[d]); v[b]=rotr(xor2(v[b],v[c]),12)
    v[a]=add(add(v[a],v[b]),my); v[d]=rotr(xor2(v[d],v[a]),8)
    v[c]=add(v[c],v[d]); v[b]=rotr(xor2(v[b],v[c]),7)
def rnd(v,m):
    G(v,0,4,8,12,m[0],m[1]);G(v,1,5,9,13,m[2],m[3]);G(v,2,6,10,14,m[4],m[5]);G(v,3,7,11,15,m[6],m[7])
    G(v,0,5,10,15,m[8],m[9]);G(v,1,6,11,12,m[10],m[11]);G(v,2,7,8,13,m[12],m[13]);G(v,3,4,9,14,m[14],m[15])
perm=lambda m:[m[i] for i in SIG]
m=[word() for _ in range(16)]
for i in range(24,32): cl.append([-m[13][i]])          # 55-byte block: top byte of w13 zero
for i in range(32): cl.append([-m[14][i]]); cl.append([-m[15][i]])
t0=word(); t1=word()
for i in range(22,32): cl.append([-t1[i]])             # t < 2^54
K=IV[2]+IV[6]
w4b=word(); w5b=word()
sA=add(const(K),m[4]); sB=add(const(K),w4b)
for i in range(32):
    cl.append([sB[i],-sA[i]] if i!=3 else [sB[i],sA[i]]); cl.append([-sB[i],sA[i]] if i!=3 else [-sB[i],-sA[i]])
uA=add(m[4],m[5]); uB=add(w4b,w5b)
for x,y in zip(uA,uB): cl.extend([[x,-y],[-x,y]])
v=[const(x) for x in IV]+[const(x) for x in IV[:4]]+[t0,t1,const(55),const(3)]
rnd(v,m)                     # round 0 (Lemma L: identical for B; verified on any solution)
mA=perm(m); mB=list(m); mB[4]=w4b; mB[5]=w5b; mB=perm(mB)
vA=list(v); vB=list(v)
rnd(vA,mA); rnd(vB,mB)       # round 1 -> state entering round index 1 done; now round index 1 of 0-based = second round
# vA/vB are now after 2 rounds = state entering round 3
d=[]
for a,b in zip(vA,vB): d+=xor2(a,b)
card=CardEnc.atmost(lits=d,bound=W,top_id=nv[0],encoding=EncType.seqcounter)
nv[0]=max(nv[0],card.nv); cl+=card.clauses
cl.append(d)   # at least one active bit (nonzero difference)
with open(out,'w') as f:
    f.write(f"p cnf {nv[0]} {len(cl)}\n")
    for c in cl: f.write(' '.join(map(str,c))+' 0\n')
with open(out+'.map','w') as f:
    import json; json.dump({'m':m,'t0':t0,'t1':t1,'w4b':w4b,'w5b':w5b},f)
print(nv[0],len(cl))
