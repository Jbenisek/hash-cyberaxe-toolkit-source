import sys, random, itertools
sys.argv=[sys.argv[0]]
exec(open("mech.py").read().split("rng=random.Random(1)")[0])
M=rho.M32
class T2(rho.Tracer):
    def __init__(s, zero=()):
        super().__init__(); s.zero=set(zero); s.sites=[]; s.tag=None
    def add(s,*xs):
        xs=list(xs)
        for i,x in enumerate(xs):
            if x[0]=="c" and x[1]!=0 and any(y[0]=="v" for y in xs):
                # a nonzero constant folded into an immediate add: a site
                # (sum of consts is one immediate; count once per call)
                pass
        csum=sum(x[1] for x in xs if x[0]=="c")&M
        hasv=any(x[0]=="v" for x in xs)
        if hasv:
            sid=("add",len(s.sites)); s.sites.append((sid,s.tag,csum))
            if sid in s.zero or ("add",sid[1]) in s.zero:
                xs=[x for x in xs if x[0]=="v"]
        return super().add(*xs)
    def xor(s,a,b):
        if (a[0]=="c")!=(b[0]=="c"):
            c=a if a[0]=="c" else b
            sid=("xor",len(s.sites)); s.sites.append((sid,s.tag,c[1]))
            if sid in s.zero:
                v=b if a[0]=="c" else a
                return super().xor(v,("c",0))
        return super().xor(a,b)
def trace(h,flags,zero=()):
    tr=T2(zero)
    v=[("c",w) for w in h]+[("c",w) for w in rho.IV[:4]]+[("c",0),("c",0),("c",64),("c",flags)]
    m=[("c",0)]*8+[("v","i%d"%i,M) for i in range(8,16)]
    for r in range(3):
        for j,(a,b,c,d) in enumerate(rho.GCALLS):
            tr.tag=(r,j)
            x,y=m[2*j],m[2*j+1]
            v[a]=tr.add(v[a],v[b],x)
            v[d]=tr.ror(tr.xor(v[d],v[a]),16)
            v[c]=tr.add(v[c],v[d])
            v[b]=tr.ror(tr.xor(v[b],v[c]),12)
            v[a]=tr.add(v[a],v[b],y)
            v[d]=tr.ror(tr.xor(v[d],v[a]),8)
            v[c]=tr.add(v[c],v[d])
            v[b]=tr.ror(tr.xor(v[b],v[c]),7)
        m=[m[i] for i in rho.PERM]
    for i in range(8):
        z=tr.xor(v[i],v[i+8])
        if z[2]>M: z=tr.mask(z)
    return tr
rng=random.Random(5)
print("single-block flags 11, IV cv:", trace(rho.IV,11).ops, "(rho.PH=%d)"%rho.PH)
h=[rng.getrandbits(32) for _ in range(8)]
t=trace(h,10); print("last-block flags 10, random h: PH =",t.ops)
base=t.ops
print("sites with variable operand present:",len(t.sites))
for s in t.sites: pass
single={}
for sid,tag,c in t.sites:
    z=trace(h,10,[sid]).ops
    single[sid]=base-z
    if z!=base: print("zero site",sid,"round/G",tag,"saves",base-z)
good=[s for s,v in single.items() if v>0]
print("sites saving >0:",len(good))
best=0
for k in (1,2,3,4):
    b=0;bc=None
    for comb in itertools.combinations(good,k):
        sv=base-trace(h,10,comb).ops
        if sv>b: b,bc=sv,comb
    print("best",k,"zero sites saves",b,bc)
