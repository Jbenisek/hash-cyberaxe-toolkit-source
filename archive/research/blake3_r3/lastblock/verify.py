import json
exec(open("sites.py").read().split("rng=random.Random(5)")[0])
h=json.load(open("h_tuned.json"))
# real concrete tracer: constants are the real chaining value; zero detection is automatic in Tracer
class TR(rho.Tracer): pass
def build(h,flags):
    tr=TR()
    v=[("c",w) for w in h]+[("c",w) for w in rho.IV[:4]]+[("c",0),("c",0),("c",64),("c",flags)]
    m=[("c",0)]*8+[("v","i%d"%i,M) for i in range(8,16)]
    for _ in range(3):
        for j,(a,b,c,d) in enumerate(rho.GCALLS):
            x,y=m[2*j],m[2*j+1]
            v[a]=tr.add(v[a],v[b],x); v[d]=tr.ror(tr.xor(v[d],v[a]),16)
            v[c]=tr.add(v[c],v[d]); v[b]=tr.ror(tr.xor(v[b],v[c]),12)
            v[a]=tr.add(v[a],v[b],y); v[d]=tr.ror(tr.xor(v[d],v[a]),8)
            v[c]=tr.add(v[c],v[d]); v[b]=tr.ror(tr.xor(v[b],v[c]),7)
        m=[m[i] for i in rho.PERM]
    out=[]
    for i in range(8):
        z=tr.xor(v[i],v[i+8])
        if z[2]>M: z=tr.mask(z)
        out.append(z[1])
    src="def batch(%s):\n"%",".join("i%d"%i for i in range(8,16))+"".join("    %s\n"%l for l in tr.lines)+"    return (%s,)\n"%",".join(out)
    ns={};exec(src,{},ns);return tr.ops,ns["batch"]
ops,batch=build(h,10)
print("PH with concrete tuned h =",ops)
rng=random.Random(9);bad=0;T=300
for t in range(T):
    xs=[rng.getrandbits(256) for _ in range(7)]
    ins=[rho.pack_x(xs)] if False else None
    packed=[sum(((x>>(32*i))&M)<<(rho.PITCH*l) for l,x in enumerate(xs)) for i in range(8)]
    out=batch(*packed)
    for l,x in enumerate(xs):
        d,_=comp(h,[0]*8+[(x>>(32*i))&M for i in range(8)],0,64,10)
        got=[(out[i]>>(rho.PITCH*l))&M for i in range(8)]
        bad+=(got!=d)
print("batch vs scalar digest mismatches:",bad,"of",T*7)
# two-block organizer check with a real P is impossible (h not a real cv); model-level equality already shown in mech.py
