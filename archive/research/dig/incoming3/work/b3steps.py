"""blake3-r3 dig-scan (own code). Parameterised copy of the Tracer of research/blake3_r3/candidate_blake3/experiments/rho.py
with per-quarter-step accounting, folding barriers, constants and lane layout as parameters."""
import sys, os, random, hashlib
M32 = 0xFFFFFFFF
IV = (0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19)
PERM = (2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8)
GC = ((0,4,8,12),(1,5,9,13),(2,6,10,14),(3,7,11,15),(0,5,10,15),(1,6,11,12),(2,7,8,13),(3,4,9,14))
NAMES = ["C0","C1","C2","C3","D0","D1","D2","D3"]
def _ror(v,k): return ((v>>k)|(v<<(32-k)))&M32

def digest_words(m, rounds, flags=11, blen=64, counter=0, trace=None):
    v = list(IV)+list(IV[:4])+[counter&M32, counter>>32, blen, flags]
    m = list(m)
    for r in range(rounds):
        for j,(a,b,c,d) in enumerate(GC):
            x,y = m[2*j], m[2*j+1]
            v[a]=(v[a]+v[b]+x)&M32; v[d]=_ror(v[d]^v[a],16)
            if trace is not None: trace[(r,NAMES[j],1)]=(v[a],v[d])
            v[c]=(v[c]+v[d])&M32; v[b]=_ror(v[b]^v[c],12)
            if trace is not None: trace[(r,NAMES[j],2)]=(v[c],v[b])
            v[a]=(v[a]+v[b]+y)&M32; v[d]=_ror(v[d]^v[a],8)
            if trace is not None: trace[(r,NAMES[j],3)]=(v[a],v[d])
            v[c]=(v[c]+v[d])&M32; v[b]=_ror(v[b]^v[c],7)
            if trace is not None: trace[(r,NAMES[j],4)]=(v[c],v[b])
        m=[m[i] for i in PERM]
    return [v[i]^v[i+8] for i in range(8)]

class Tr:
    def __init__(s, pitch=36, lanes=7):
        s.P, s.L = pitch, lanes
        s.REP = sum(1<<(pitch*i) for i in range(lanes)); s.LIM = 1<<pitch
        s.lines=[]; s.ops=0; s.by={}; s.k=0
    def emit(s,kind,expr):
        s.k+=1; n="t%d"%s.k; s.lines.append("%s=%s"%(n,expr)); s.ops+=1; s.by[kind]=s.by.get(kind,0)+1; return n
    def mask(s,a): return ("v",s.emit("and","%s&%d"%(a[1],s.REP*M32)),M32)
    def add(s,*xs):
        c=sum(x[1] for x in xs if x[0]=="c")&M32
        vs=[x for x in xs if x[0]=="v"]
        if not vs: return ("c",c)
        acc=vs[0]
        for v in vs[1:]:
            while acc[2]+v[2]>=s.LIM:
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
    def ror(s,a,r):
        if a[0]=="c": return ("c",_ror(a[1],r))
        s1=s.emit("shr","%s>>%d"%(a[1],r)); h=s.emit("and","%s&%d"%(s1,s.REP*((1<<(32-r))-1)))
        s2=s.emit("shl","%s<<%d"%(a[1],32-r)); lw=s.emit("and","%s&%d"%(s2,s.REP*(((1<<r)-1)<<(32-r))))
        return ("v",s.emit("or","%s|%s"%(h,lw)),M32)

def build(rounds=3, pitch=36, lanes=7, free=range(8,16), consts=None, unfold=None, ctr=0, blen=64, flags=11, vals=None):
    """Returns (src, ops, by, per-step table, tracer). consts: 16 message constants for non-free words (default 0).
    unfold: set of (round,call,q) steps whose constant inputs are demoted to run-time variables (no build-time folding from there).
    vals: optional dict filled with (round,call,q) -> tuple of constant outputs (or None if variable)."""
    tr=Tr(pitch,lanes); unfold=unfold or set()
    free=set(free); consts=consts or [0]*16
    v=[("c",w) for w in IV]+[("c",w) for w in IV[:4]]+[("c",ctr&M32),("c",ctr>>32),("c",blen),("c",flags)]
    m=[("v","i%d"%i,M32) if i in free else ("c",consts[i]) for i in range(16)]
    rec={}; dem=[0]
    def demote(x):
        if x[0]=="c":
            dem[0]+=1; return ("v","k%d_%d"%(dem[0],x[1]),M32)
        return x
    for r in range(rounds):
        for j,(a,b,c,d) in enumerate(GC):
            x,y=m[2*j],m[2*j+1]
            def step(q,f,ins,outs):
                key=(r,NAMES[j],q)
                if key in unfold:
                    for i in ins: v[i]=demote(v[i])
                o0,b0=tr.ops,dict(tr.by); f()
                rec[key]=(tr.ops-o0,{k:tr.by[k]-b0.get(k,0) for k in tr.by if tr.by[k]-b0.get(k,0)})
                if vals is not None:
                    vals[key]=tuple(v[i][1] if v[i][0]=="c" else None for i in outs)
            def q1(): v[a]=tr.add(v[a],v[b],x); v[d]=tr.ror(tr.xor(v[d],v[a]),16)
            def q2(): v[c]=tr.add(v[c],v[d]); v[b]=tr.ror(tr.xor(v[b],v[c]),12)
            def q3(): v[a]=tr.add(v[a],v[b],y); v[d]=tr.ror(tr.xor(v[d],v[a]),8)
            def q4(): v[c]=tr.add(v[c],v[d]); v[b]=tr.ror(tr.xor(v[b],v[c]),7)
            step(1,q1,(a,b,d),(a,d)); step(2,q2,(c,d,b),(c,b)); step(3,q3,(a,b,d),(a,d)); step(4,q4,(c,d,b),(c,b))
        m=[m[i] for i in PERM]
    out=[]; o0=tr.ops
    for i in range(8):
        z=tr.xor(v[i],v[i+8])
        if z[2]>M32: z=tr.mask(z)
        out.append(z[1])
    rec["final"]=(tr.ops-o0,{})
    src="def batch(%s):\n"%",".join("i%d"%i for i in sorted(free))+"".join("    %s\n"%ln for ln in tr.lines)+"    return (%s,)\n"%",".join(out)
    return src,tr.ops,dict(tr.by),rec,tr

def make_batch(src):
    ns={}; exec(src,{},ns); return ns["batch"]

def check(src, rounds, pitch, lanes, free, consts=None, n=6, seed=5, verifier=None):
    """packed circuit vs scalar digest (and vs organizer verifier when given); random inputs on all free words."""
    rng=random.Random(seed); bt=make_batch(src); consts=consts or [0]*16; free=sorted(free)
    for _ in range(n):
        lm=[[rng.getrandbits(32) for _ in free] for _ in range(lanes)]
        args=[sum(lm[l][i]<<(pitch*l) for l in range(lanes)) for i in range(len(free))]
        outw=bt(*args)
        for l in range(lanes):
            msg=list(consts)
            for i,w in enumerate(free): msg[w]=lm[l][i]
            ref=digest_words(msg,rounds)
            got=[(outw[i]>>(pitch*l))&M32 for i in range(8)]
            if ref!=got: return False
            if verifier is not None:
                data=b"".join(w.to_bytes(4,"little") for w in msg)
                if verifier(data,rounds)!=b"".join(w.to_bytes(4,"little") for w in ref): return False
    return True
