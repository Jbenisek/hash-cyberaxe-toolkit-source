exec(open("sites.py").read().split("rng=random.Random(5)")[0])
class T3(T2):
    def __init__(s, ov):
        super().__init__(); s.ov=ov
    def add(s,*xs):
        xs=list(xs)
        if any(x[0]=="v" for x in xs):
            sid=("s",len(s.sites)); s.sites.append((sid,s.tag,0))
            if sid in s.ov:
                vs=[x for x in xs if x[0]=="v"]
                xs=vs+([("c",s.ov[sid])] if s.ov[sid] else [])
        return rho.Tracer.add(s,*xs)
    def xor(s,a,b):
        if (a[0]=="c")!=(b[0]=="c"):
            sid=("s",len(s.sites)); s.sites.append((sid,s.tag,0))
            if sid in s.ov:
                v=b if a[0]=="c" else a
                return rho.Tracer.xor(s,v,("c",s.ov[sid]))
        return rho.Tracer.xor(s,a,b)
def tr3(h,flags,ov={}):
    tr=T3(ov)
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
if __name__=="__main__":
    rng=random.Random(5)
    for trial in range(3):
        h=[rng.getrandbits(32)|0x80000000 for _ in range(8)]
        t=tr3(h,10); base=t.ops; n=len(t.sites)
        print("trial",trial,"base",base,"sites",n)
        for k in range(n):
            res=[]
            for L in (0,1,4,8,12,16,20,24,28,30,31):
                val=(1<<L)-1 if L else 0
                s=base-tr3(h,10,{("s",k):val}).ops
                res.append((L,s))
            if any(s>0 for _,s in res):
                print(" site",k,t.sites[k][1],[(L,s) for L,s in res if s>0][:12])
