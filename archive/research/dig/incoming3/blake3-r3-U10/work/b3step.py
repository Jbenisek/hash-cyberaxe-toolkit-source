"""Per-quarter-step scan of the filed 3-round BLAKE3 circuit (own code, no participant code run).
Tracer logic follows the printed definition in research/blake3_r3/candidate_blake3/experiments/rho.py (7 lanes x 36 bits)
but is rewritten here with a per-quarter-step tag, an assoc order switch, and op-deletion variants.
Usage: py b3step.py selftest | scan <outjson>
"""

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

import sys, json, random, re, importlib.util, time
M32=0xFFFFFFFF
IV=(0x6A09E667,0xBB67AE85,0x3C6EF372,0xA54FF53A,0x510E527F,0x9B05688C,0x1F83D9AB,0x5BE0CD19)
PERM=(2,6,3,10,7,0,4,13,1,11,12,5,9,14,15,8)
GC=((0,4,8,12),(1,5,9,13),(2,6,10,14),(3,7,11,15),(0,5,10,15),(1,6,11,12),(2,7,8,13),(3,4,9,14))
def ror(v,k): return ((v>>k)|(v<<(32-k)))&M32

def scalar(m,rounds,blen=64,flags=11,skip=None,rec=None,counter=0):
    v=list(IV)+list(IV[:4])+[counter&M32,counter>>32,blen,flags]; m=list(m)
    for r in range(rounds):
        for j,(a,b,c,d) in enumerate(GC):
            x,y=m[2*j],m[2*j+1]
            for q in (1,2,3,4):
                if skip!=(r,j,q):
                    if q==1: v[a]=(v[a]+v[b]+x)&M32; v[d]=ror(v[d]^v[a],16)
                    elif q==2: v[c]=(v[c]+v[d])&M32; v[b]=ror(v[b]^v[c],12)
                    elif q==3: v[a]=(v[a]+v[b]+y)&M32; v[d]=ror(v[d]^v[a],8)
                    else: v[c]=(v[c]+v[d])&M32; v[b]=ror(v[b]^v[c],7)
                if rec is not None and rec[0]==(r,j,q):
                    rec[1]=((v[a],v[d]) if q in (1,3) else (v[c],v[b]))
        m=[m[i] for i in PERM]
    return [v[i]^v[i+8] for i in range(8)]

class Tr:
    def __init__(s,pitch=36):
        s.pitch=pitch; s.lanes=256//pitch
        s.REP=sum(1<<(pitch*i) for i in range(s.lanes)); s.LIM=1<<pitch
        s.lines=[]; s.k=0; s.tag=None
    def emit(s,kind,expr):
        s.k+=1; n="t%d"%s.k; s.lines.append((n,kind,expr,s.tag)); return n
    def mask(s,a): return ("v",s.emit("and","%s&%d"%(a[1],s.REP*M32)),M32)
    def add(s,*xs):
        c=sum(x[1] for x in xs if x[0]=="c")&M32
        vs=[x for x in xs if x[0]=="v"]
        if not vs: return ("c",c)
        acc=vs[0]
        for v in vs[1:]:
            n=0
            while acc[2]+v[2]>=s.LIM:
                n+=1
                if n>6: raise ValueError("cannot fit")
                if acc[2]>=v[2]: acc=s.mask(acc)
                else: v=s.mask(v)
            acc=("v",s.emit("add","%s+%s"%(acc[1],v[1])),acc[2]+v[2])
        if c:
            if acc[2]+c>=s.LIM: acc=s.mask(acc)
            acc=("v",s.emit("add","%s+%d"%(acc[1],s.REP*c)),acc[2]+c)
        return acc
    def xor(s,a,b):
        if a[0]=="c" and b[0]=="c": return ("c",a[1]^b[1])
        if a[0]=="c": a,b=b,a
        if b[0]=="c":
            if b[1]==0: return a
            return ("v",s.emit("xor","%s^%d"%(a[1],s.REP*b[1])),(1<<max(a[2].bit_length(),b[1].bit_length()))-1)
        return ("v",s.emit("xor","%s^%s"%(a[1],b[1])),(1<<max(a[2].bit_length(),b[2].bit_length()))-1)
    rot4=False
    def ror(s,a,r):
        if a[0]=="c": return ("c",ror(a[1],r))
        if s.rot4 and s.tag in s.rot4:
            s1=s.emit("shr","%s>>%d"%(a[1],r)); s2=s.emit("shl","%s<<%d"%(a[1],32-r)); o=s.emit("or","%s|%s"%(s1,s2))
            return ("v",s.emit("and","%s&%d"%(o,s.REP*M32)),M32)
        s1=s.emit("shr","%s>>%d"%(a[1],r)); h=s.emit("and","%s&%d"%(s1,s.REP*((1<<(32-r))-1)))
        s2=s.emit("shl","%s<<%d"%(a[1],32-r)); lw=s.emit("and","%s&%d"%(s2,s.REP*(((1<<r)-1)<<(32-r))))
        return ("v",s.emit("or","%s|%s"%(h,lw)),M32)

def build(rounds=3,pitch=36,assoc=None,rot4=None):
    """assoc: dict (r,j,q)->permutation tuple of the 3 add operands (a,b,msg). Returns tracer, source, outputs."""
    tr=Tr(pitch); assoc=assoc or {}; tr.rot4=rot4
    v=[("c",w) for w in IV]+[("c",w) for w in IV[:4]]+[("c",0),("c",0),("c",64),("c",11)]
    m=[("c",0)]*8+[("v","i%d"%i,M32) for i in range(8,16)]
    for r in range(rounds):
        for j,(a,b,c,d) in enumerate(GC):
            x,y=m[2*j],m[2*j+1]
            tr.tag=(r,j,1); ops=[v[a],v[b],x]; p=assoc.get((r,j,1),(0,1,2)); v[a]=tr.add(*[ops[i] for i in p]); v[d]=tr.ror(tr.xor(v[d],v[a]),16)
            tr.tag=(r,j,2); v[c]=tr.add(v[c],v[d]); v[b]=tr.ror(tr.xor(v[b],v[c]),12)
            tr.tag=(r,j,3); ops=[v[a],v[b],y]; p=assoc.get((r,j,3),(0,1,2)); v[a]=tr.add(*[ops[i] for i in p]); v[d]=tr.ror(tr.xor(v[d],v[a]),8)
            tr.tag=(r,j,4); v[c]=tr.add(v[c],v[d]); v[b]=tr.ror(tr.xor(v[b],v[c]),7)
        m=[m[i] for i in PERM]
    tr.tag=("fin",0,0); out=[]
    for i in range(8):
        z=tr.xor(v[i],v[i+8])
        if z[2]>M32: z=tr.mask(z)
        out.append(z[1])
    return tr,out

def compile_(tr,out,delete=None):
    src="def batch(%s):\n"%",".join("i%d"%i for i in range(8,16))
    for idx,(n,kind,expr,tag) in enumerate(tr.lines):
        if delete==idx: expr=re.match(r"[A-Za-z0-9_]+",expr).group(0)
        src+="    %s=%s\n"%(n,expr)
    src+="    return (%s,)\n"%",".join(out)
    ns={}; exec(src,{},ns); return ns["batch"]

def pack(vals,pitch=36): return sum(v<<(pitch*l) for l,v in enumerate(vals))
def unpack(w,l,pitch=36): return (w>>(pitch*l))&M32

def lane_test(tr,out,rounds,nb,rng,delete=None,pitch=36):
    f=compile_(tr,out,delete); bad=0; tot=0
    for _ in range(nb):
        ms=[[rng.getrandbits(32) for _ in range(8)] for _ in range(tr.lanes)]
        res=f(*[pack([ms[l][i] for l in range(tr.lanes)],pitch) for i in range(8)])
        for l in range(tr.lanes):
            exp=scalar([0]*8+ms[l],rounds)
            got=[unpack(res[i],l,pitch) for i in range(8)]
            tot+=1
            if got!=exp: bad+=1
    return bad,tot

def load_verifier():
    p=_hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/pareto_clone/verifier/blake3.py')
    sp=importlib.util.spec_from_file_location("vb3",p); mod=importlib.util.module_from_spec(sp); sp.loader.exec_module(mod); return mod

def selftest():
    res={}
    # official test vector: BLAKE3("") 7 rounds
    d=scalar([0]*16,7,blen=0,flags=11)
    h=b"".join(w.to_bytes(4,"little") for w in d).hex()
    res["empty_7r"]=h; res["empty_7r_ok"]=(h=="af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262")
    vb=load_verifier(); rng=random.Random(7); okv=True
    for rounds in (7,3):
        for _ in range(200):
            x=[rng.getrandbits(32) for _ in range(8)]
            data=bytes(32)+b"".join(w.to_bytes(4,"little") for w in x)
            exp=vb.blake3(data,rounds)
            got=b"".join(w.to_bytes(4,"little") for w in scalar([0]*8+x,rounds))
            okv&=(exp==got)
    res["scalar_vs_verifier_7r_3r_200each"]=okv
    # official 7-round vector for the 64-byte-ish input is covered via verifier; circuit checks
    for rounds in (7,3):
        tr,out=build(rounds); bad,tot=lane_test(tr,out,rounds,300,random.Random(3))
        res["circuit_%dr"%rounds]={"ops":len(tr.lines),"mismatch":bad,"lanes_tested":tot}
    tr,out=build(3); by={}
    for n,k,e,t in tr.lines: by[k]=by.get(k,0)+1
    res["ops3_by_kind"]=by
    print(json.dumps(res,indent=1)); return res



def taint(tr):
    T={}
    for n,k,e,t in tr.lines:
        s=set()
        for nm in re.findall(r"(?<![0-9a-z])[it][0-9]+(?![0-9])",e):
            if nm.startswith("i"): s.add(int(nm[1:]))
            else: s|=T[nm]
        T[n]=s
    return T

def prio():
    try:
        import ctypes; ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
    except Exception: pass

MY=[((0,4,3),(0,4,4))]+[((0,j,q)) for j in (5,6,7) for q in (1,2,3,4)]+[(1,0,q) for q in (1,2,3,4)]
MYSTEPS=[(0,4,3),(0,4,4)]+[(0,j,q) for j in (5,6,7) for q in (1,2,3,4)]+[(1,0,q) for q in (1,2,3,4)]
LOGPER=-__import__("math").log2(1-0.9944/599.1875)

def scan(outp,nb=1000):
    prio(); t0=time.time(); rng=random.Random(20261012)
    tr,out=build(3); T=taint(tr)
    base_ops=len(tr.lines)
    # alt pitches
    alt_pitch={}
    for pit in (34,35,36):
        try:
            tp,_=build(3,pit); per={}
            for n,k,e,t in tp.lines: per[t]=per.get(t,0)+1
            alt_pitch[pit]=(len(tp.lines),tp.lanes,per)
        except Exception as ex: alt_pitch[pit]=(str(ex),None,{})
    res={"base_ops":base_ops,"logper_op":LOGPER,"alt_pitch_totals":{k:[v[0],v[1]] for k,v in alt_pitch.items()},"steps":{}}
    # random messages for avalanche
    msgs=[[rng.getrandbits(32) for _ in range(8)] for _ in range(1500)]
    for st in MYSTEPS:
        r,j,q=st; key="R%d%s%d.q%d"%(r,"C" if j<4 else "D",j%4,q)
        idxs=[i for i,l in enumerate(tr.lines) if l[3]==st]
        kinds={}
        for i in idxs: kinds[tr.lines[i][1]]=kinds.get(tr.lines[i][1],0)+1
        # unfolded reference count of this quarter step on the same primitive set
        ref=8 if q in (1,3) else 7
        sup=set()
        for i in idxs: sup|=T[tr.lines[i][0]]
        d={"ops":len(idxs),"kinds":kinds,"unfolded_ref_ops":ref,"folded_away":ref-len(idxs),"free_words_in_support":sorted(sup),
           "dof_bits_msg":32*len(sup),"gain_if_one_op_saved":LOGPER,"op_lines":[tr.lines[i][2][:40] for i in idxs]}
        # Q2a bypass avalanche
        flips=0; chg=0
        for x in msgs:
            a=scalar([0]*8+x,3); b=scalar([0]*8+x,3,skip=st)
            f=sum(bin(u^v).count("1") for u,v in zip(a,b)); flips+=f; chg+=(f>0)
        d["bypass_mean_bits_flipped_of_256"]=flips/len(msgs); d["bypass_digest_changed_frac"]=chg/len(msgs)
        # Q2b deletion of each op
        dele=[]
        for i in idxs:
            bad,tot=lane_test(tr,out,3,nb,rng,delete=i)
            dele.append({"line":tr.lines[i][2][:30],"kind":tr.lines[i][1],"bad":bad,"lanes":tot})
        d["delete_each_op"]=dele
        # Q3 injectivity of step output over its support
        rec=[st,None]; seen=set(); N=1<<16; dup=0
        fixed=[rng.getrandbits(32) for _ in range(8)]
        for k in range(N):
            x=list(fixed)
            for w in sup:
                x[w-8]=rng.getrandbits(32) if len(sup)>1 else (k*2654435761+12345)&M32
            rec=[st,None]; scalar([0]*8+x,3,rec=rec)
            o=rec[1]
            if o in seen: dup+=1
            seen.add(o)
        d["inj_sample"]={"N":N,"distinct_outputs":len(seen),"dups":dup,"support_words":len(sup)}
        # Q4 alternatives
        alt={}
        if q in (1,3):
            for p in ((0,1,2),(0,2,1),(1,2,0),(2,1,0),(1,0,2),(2,0,1)):
                try:
                    ta,_=build(3,36,{st:p}); alt[str(p)]={"total":len(ta.lines),"step_ops":sum(1 for l in ta.lines if l[3]==st)}
                except Exception as ex: alt[str(p)]={"err":str(ex)}
        d["alt_add_orders"]=alt
        t4,o4=build(3,36,None,{st})
        n4=sum(1 for l in t4.lines if l[3]==st)
        try:
            bad,tot=lane_test(t4,o4,3,nb,rng)
        except Exception as ex: bad,tot=-1,0
        d["alt_rot_single_and"]={"step_ops":n4,"total":len(t4.lines),"bad":bad,"lanes":tot}
        d["alt_pitch_step_ops"]={str(k):v[2].get(st) for k,v in alt_pitch.items()}
        res["steps"][key]=d
        print(key,d["ops"],d["bypass_mean_bits_flipped_of_256"],[x["bad"] for x in dele],round(time.time()-t0),flush=True)
    json.dump(res,open(outp,"w"),indent=1)


if __name__=="__main__":
    if sys.argv[1]=="selftest": selftest()
    if sys.argv[1]=="scan": scan(sys.argv[2],int(sys.argv[3]) if len(sys.argv)>3 else 1000)

