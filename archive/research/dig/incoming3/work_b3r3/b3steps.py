"""Per-quarter-step accounting of the filed blake3-r3 circuit (own tracer subclass of the filed rho.Tracer) and
alternative formulations.  Own code only.  Run: python b3steps.py  -> writes steps.json"""

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

import sys, json, itertools, random
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/blake3_r3/candidate_blake3/experiments'))
import rho
from rho import M32, IV, PERM, GCALLS, REP, _ror

class T2(rho.Tracer):
    def __init__(self, lim=1<<36, order="asc0", tight=False):
        super().__init__(); self.lim=lim; self.order=order; self.tight=tight
        self.tag=None; self.step_by={}; self.step_masks={}
    def emit(self, kind, expr):
        r=super().emit(kind, expr)
        d=self.step_by.setdefault(self.tag,{}); d[kind]=d.get(kind,0)+1
        return r
    def mask(self, a):
        self.step_masks[self.tag]=self.step_masks.get(self.tag,0)+1
        return super().mask(a)
    def add(self, *xs):
        c = sum(x[1] for x in xs if x[0]=="c") & M32
        vs=[x for x in xs if x[0]=="v"]
        if not vs: return ("c", c)
        if self.order=="asc": vs=sorted(vs,key=lambda t:t[2])
        elif self.order=="desc": vs=sorted(vs,key=lambda t:-t[2])
        acc=vs[0]
        for v in vs[1:]:
            while acc[2]+v[2] >= self.lim:
                if acc[2]>=v[2]: acc=self.mask(acc)
                else: v=self.mask(v)
            acc=("v", self.emit("add","%s+%s"%(acc[1],v[1])), acc[2]+v[2])
        if c:
            if acc[2]+c >= self.lim: acc=self.mask(acc)
            acc=("v", self.emit("add","%s+%d"%(acc[1],REP*c)), acc[2]+c)
        return acc

def build(lim=1<<36, order="asc0", record=False, skip_step=None):
    tr=T2(lim,order)
    v=[("c",w) for w in IV]+[("c",w) for w in IV[:4]]+[("c",0),("c",0),("c",64),("c",11)]
    m=[("c",0)]*8+[("v","i%d"%i,M32) for i in range(8,16)]
    info={}
    def st(x): return ("c" if x[0]=="c" else "v%d"%(x[2]).bit_length())
    for rd in range(3):
        for j,(a,b,c,d) in enumerate(GCALLS):
            kind=("C%d"%j) if j<4 else ("D%d"%(j-4))
            nm="R%d%s"%(rd+1,kind)
            x,y=m[2*j],m[2*j+1]
            def go(q, body):
                tr.tag=(nm,q)
                n0=tr.ops
                pre=(st(v[a]),st(v[b]),st(v[c]),st(v[d]))
                body()
                info[(nm,q)]=dict(pre=pre,post=(st(v[a]),st(v[b]),st(v[c]),st(v[d])),ops=tr.ops-n0)
            def q1(): v[a]=tr.add(v[a],v[b],x); v[d]=tr.ror(tr.xor(v[d],v[a]),16)
            def q2(): v[c]=tr.add(v[c],v[d]); v[b]=tr.ror(tr.xor(v[b],v[c]),12)
            def q3(): v[a]=tr.add(v[a],v[b],y); v[d]=tr.ror(tr.xor(v[d],v[a]),8)
            def q4(): v[c]=tr.add(v[c],v[d]); v[b]=tr.ror(tr.xor(v[b],v[c]),7)
            for q,f in (("q1",q1),("q2",q2),("q3",q3),("q4",q4)):
                if skip_step==(nm,q):   # cost-only: run, then roll the op count back (ceiling test)
                    n0=tr.ops; f(); tr.ops=n0; continue
                go(q,f)
            info[(nm,"msg")]=("m%d"%(PERM_idx[rd][2*j]),"m%d"%(PERM_idx[rd][2*j+1]),
                              "const0" if x[0]=="c" else "var", "const0" if y[0]=="c" else "var")
        m=[m[i] for i in PERM]
    tr.tag=("FIN","fin")
    for i in range(8):
        z=tr.xor(v[i],v[i+8])
        if z[2]>M32: z=tr.mask(z)
    return tr, info

PERM_idx=[]; mi=list(range(16))
for _ in range(3):
    PERM_idx.append(list(mi)); mi=[mi[i] for i in PERM]

def lbl(k): return "%s.%s"%k

if __name__=="__main__":
    base,info=build()
    print("baseline",base.ops,base.by)
    print("selftest",rho.selftest())
    print("masks by step",{lbl(k):v for k,v in base.step_masks.items()})
    out={"base_ops":base.ops,"base_by":base.by,"masks":{lbl(k):v for k,v in base.step_masks.items()}}
    steps={}
    for k,d in base.step_by.items():
        steps[lbl(k)]=d
    out["step_by"]=steps
    out["info"]={lbl(k) if isinstance(k,tuple) and k[1]!="msg" else "%s.msg"%k[0]:v for k,v in info.items()}
    alts={}
    for name,kw in (("asc",dict(order="asc")),("desc",dict(order="desc")),("lim33",dict(lim=1<<33)),("lim34",dict(lim=1<<34)),("lim35",dict(lim=1<<35)),("lim36",dict(lim=1<<36))):
        t,_=build(**kw); alts[name]=(t.ops,t.by,{lbl(k):v for k,v in t.step_masks.items()})
        print(name,t.ops,alts[name][2])
    out["alts"]=alts
    json.dump(out,open("steps.json","w"),default=str,indent=0)
