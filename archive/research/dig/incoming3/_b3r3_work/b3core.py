"""Own BLAKE3 core for the blake3-r3 dig scout (2026-10-12): scalar reference, 7-lane packed tracer with per-op tags, interpreter with mutation hook.
Written from the printed definitions of the circuit (36-bit pitch, 7 lanes); no code of other participants is run."""
import sys, os, random
M32=0xFFFFFFFF
IV=(0x6A09E667,0xBB67AE85,0x3C6EF372,0xA54FF53A,0x510E527F,0x9B05688C,0x1F83D9AB,0x5BE0CD19)
PERM=(2,6,3,10,7,0,4,13,1,11,12,5,9,14,15,8)
GC=((0,4,8,12),(1,5,9,13),(2,6,10,14),(3,7,11,15),(0,5,10,15),(1,6,11,12),(2,7,8,13),(3,4,9,14))
PITCH,LANES=36,7
REP=sum(1<<(PITCH*i) for i in range(LANES)); LIM=1<<PITCH
def ror(v,k): return ((v>>k)|(v<<(32-k)))&M32
def digest_words(m,rounds=3,flags=11,blen=64,counter=0,cv=IV):
    v=list(cv)+list(IV[:4])+[counter&M32,counter>>32,blen,flags]; m=list(m)
    for _ in range(rounds):
        for j,(a,b,c,d) in enumerate(GC):
            x,y=m[2*j],m[2*j+1]
            v[a]=(v[a]+v[b]+x)&M32; v[d]=ror(v[d]^v[a],16); v[c]=(v[c]+v[d])&M32; v[b]=ror(v[b]^v[c],12)
            v[a]=(v[a]+v[b]+y)&M32; v[d]=ror(v[d]^v[a],8); v[c]=(v[c]+v[d])&M32; v[b]=ror(v[b]^v[c],7)
        m=[m[i] for i in PERM]
    return [v[i]^v[i+8] for i in range(8)]
def digest_bytes(data,rounds):
    assert len(data)==64
    m=[int.from_bytes(data[4*i:4*i+4],'little') for i in range(16)]
    return b''.join(w.to_bytes(4,'little') for w in digest_words(m,rounds))
def f_scalar(x,rounds=3):
    return digest_words([0]*8+[(x>>(32*i))&M32 for i in range(8)],rounds)

# ---------- tracer: values ('c',k) | ('v',reg,bound)
class Tr:
    def __init__(s): s.prog=[]; s.tag=None; s.nreg=0
    def emit(s,kind,args,imm=None):
        r='t%d'%len(s.prog); s.prog.append(dict(r=r,kind=kind,args=args,imm=imm,tag=s.tag)); return r
    def mask(s,a): return ('v',s.emit('and',[a[1]],REP*M32),M32)
    def add(s,*xs):
        c=sum(x[1] for x in xs if x[0]=='c')&M32; vs=[x for x in xs if x[0]=='v']
        if not vs: return ('c',c)
        acc=vs[0]
        for v in vs[1:]:
            while acc[2]+v[2]>=LIM:
                if acc[2]>=v[2]: acc=s.mask(acc)
                else: v=s.mask(v)
            acc=('v',s.emit('add',[acc[1],v[1]]),acc[2]+v[2])
        if c:
            if acc[2]+c>=LIM: acc=s.mask(acc)
            acc=('v',s.emit('add',[acc[1]],REP*c),acc[2]+c)
        return acc
    def xor(s,a,b):
        if a[0]=='c' and b[0]=='c': return ('c',a[1]^b[1])
        if a[0]=='c': a,b=b,a
        if b[0]=='c':
            if b[1]==0: return a
            return ('v',s.emit('xor',[a[1]],REP*b[1]),(1<<max(a[2].bit_length(),b[1].bit_length()))-1)
        return ('v',s.emit('xor',[a[1],b[1]]),(1<<max(a[2].bit_length(),b[2].bit_length()))-1)
    def ror(s,a,r):
        if a[0]=='c': return ('c',ror(a[1],r))
        s1=s.emit('shr',[a[1]],r); h=s.emit('and',[s1],REP*((1<<(32-r))-1))
        s2=s.emit('shl',[a[1]],32-r); lw=s.emit('and',[s2],REP*(((1<<r)-1)<<(32-r)))
        return ('v',s.emit('or',[h,lw]),M32)
def build(rounds=3):
    tr=Tr()
    v=[('c',w) for w in IV]+[('c',w) for w in IV[:4]]+[('c',0),('c',0),('c',64),('c',11)]
    m=[('c',0)]*8+[('v','i%d'%i,M32) for i in range(8,16)]
    qs=((16,'d','a'),(12,'b','c'))
    for rd in range(rounds):
        for j,(a,b,c,d) in enumerate(GC):
            x,y=m[2*j],m[2*j+1]
            tr.tag=(rd,j,1); v[a]=tr.add(v[a],v[b],x); v[d]=tr.ror(tr.xor(v[d],v[a]),16)
            tr.tag=(rd,j,2); v[c]=tr.add(v[c],v[d]); v[b]=tr.ror(tr.xor(v[b],v[c]),12)
            tr.tag=(rd,j,3); v[a]=tr.add(v[a],v[b],y); v[d]=tr.ror(tr.xor(v[d],v[a]),8)
            tr.tag=(rd,j,4); v[c]=tr.add(v[c],v[d]); v[b]=tr.ror(tr.xor(v[b],v[c]),7)
        m=[m[i] for i in PERM]
    tr.tag=('final',)
    out=[]
    for i in range(8):
        z=tr.xor(v[i],v[i+8])
        if z[2]>M32: z=tr.mask(z)
        out.append(z[1])
    return tr.prog,out
def run(prog,out,ins,mut=None,trace=None):
    """ins: list of 8 packed words i8..i15.  mut=(index,variant): variant 'a0','a1','zero' replaces op result."""
    env={'i%d'%(8+i):ins[i] for i in range(8)}
    for n,op in enumerate(prog):
        a=[env[x] for x in op['args']]; k=op['kind']; im=op['imm']
        if k=='and': r=a[0]&im
        elif k=='add': r=a[0]+(a[1] if len(a)>1 else im)
        elif k=='xor': r=a[0]^(a[1] if len(a)>1 else im)
        elif k=='or': r=a[0]|a[1]
        elif k=='shr': r=a[0]>>im
        elif k=='shl': r=a[0]<<im
        if mut and mut[0]==n:
            v=mut[1]
            if v=='a0': r=a[0]
            elif v=='a1': r=a[1] if len(a)>1 else (a[0] if k in('and','shr','shl') else r)
            elif v=='zero': r=0
        if trace is not None: trace[op['r']]=r
        env[op['r']]=r
    return [env[o] for o in out]
def pack(vals): return sum(v<<(PITCH*l) for l,v in enumerate(vals))
def lane(w,l): return (w>>(PITCH*l))&M32
def pack_x(xs): return [pack([(x>>(32*i))&M32 for x in xs]) for i in range(8)]
def check(prog,out,xs,mut=None):
    o=run(prog,out,pack_x(xs),mut)
    for l,x in enumerate(xs):
        ref=f_scalar(x)
        if any(lane(o[i],l)!=ref[i] for i in range(8)): return False
    return True
