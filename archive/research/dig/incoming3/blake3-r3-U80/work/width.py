# MACHINE.WIDTH Q2/Q3/Q4: ops per chain step as a function of machine word width W and lane pitch p (guard bits p-32),
# using the filed tracer (greedy mask insertion), every variant checked against the scalar digest.
import random, math
from common import rho as R
random.seed(5)
class Tight(R.Tracer):
    # p=32: no guard bits. Lane-isolated add = ((a&H)+(b&H)) ^ ((a^b)&T), H=0x7FFFFFFF, T=0x80000000 per lane: 6 ops (5 with a constant operand)
    def add(self,*xs):
        c=sum(x[1] for x in xs if x[0]=="c")&R.M32
        vs=[x for x in xs if x[0]=="v"]
        if not vs: return ("c",c)
        acc=vs[0]
        H=R.REP*0x7FFFFFFF; T=R.REP*0x80000000
        for v in vs[1:]:
            t1=self.emit("and","%s&%d"%(acc[1],H)); t2=self.emit("and","%s&%d"%(v[1],H)); s=self.emit("add","%s+%s"%(t1,t2))
            x=self.emit("xor","%s^%s"%(acc[1],v[1])); x2=self.emit("and","%s&%d"%(x,T)); acc=("v",self.emit("xor","%s^%s"%(s,x2)),R.M32)
        if c:
            t1=self.emit("and","%s&%d"%(acc[1],H)); s=self.emit("add","%s+%d"%(t1,R.REP*(c&0x7FFFFFFF)))
            x=self.emit("xor","%s^%d"%(acc[1],R.REP*c)); x2=self.emit("and","%s&%d"%(x,T)); acc=("v",self.emit("xor","%s^%s"%(s,x2)),R.M32)
        return acc
class Native(R.Tracer):
    # W=32, one lane: native wrap-around add, 3-op rotation (shr, shl, or)
    def add(self,*xs):
        c=sum(x[1] for x in xs if x[0]=="c")&R.M32
        vs=[x for x in xs if x[0]=="v"]
        if not vs: return ("c",c)
        acc=vs[0]
        for v in vs[1:]: acc=("v",self.emit("add","(%s+%s)&%d"%(acc[1],v[1],R.M32)),R.M32)
        if c: acc=("v",self.emit("add","(%s+%d)&%d"%(acc[1],c,R.M32)),R.M32)
        return acc
    def ror(self,a,r):
        if a[0]=="c": return ("c",R._ror(a[1],r))
        s1=self.emit("shr","%s>>%d"%(a[1],r)); s2=self.emit("shl","(%s<<%d)&%d"%(a[1],32-r,R.M32))
        return ("v",self.emit("or","%s|%s"%(s1,s2)),R.M32)
def variant(W,p):
    lanes=W//p
    if lanes<1: return None
    if W==32:
        R.PITCH=32; R.LANES=1; R.LIM=1<<32; R.REP=1
        old=R.Tracer; R.Tracer=Native
        try: src,ops,by=R.build_hash()
        finally: R.Tracer=old
        return finish(src,ops,by,1,32)
    if p==32:
        R.PITCH=32; R.LANES=lanes; R.LIM=1<<32; R.REP=sum(1<<(32*i) for i in range(lanes))
        old=R.Tracer; R.Tracer=Tight
        try: src,ops,by=R.build_hash()
        finally: R.Tracer=old
        return finish(src,ops,by,lanes,p)
    R.PITCH=p; R.LANES=lanes; R.LIM=1<<p; R.REP=sum(1<<(p*i) for i in range(lanes))
    src,ops,by=R.build_hash()
    return finish(src,ops,by,lanes,p)
def finish(src,ops,by,lanes,p):
    ns={}; exec(src,{},ns); fn=ns['batch']
    bad=0
    for _ in range(40):
        xs=[random.getrandbits(256) for _ in range(lanes)]
        inp=[sum(((x>>(32*i))&0xFFFFFFFF)<<(p*l) for l,x in enumerate(xs)) for i in range(8)]
        out=fn(*inp)
        for l,x in enumerate(xs):
            got=sum(((out[i]>>(p*l))&0xFFFFFFFF)<<(32*i) for i in range(8))
            if got!=R.f_scalar(x,256): bad+=1
    return lanes,ops,by,bad
base=595/7
print('filed: W=256 p=36 lanes=7 ops=595 ops/step=%.3f'%base)
print("NOTE: W=32 uses native wrap-around add (1 lane); W=64 and p=32 rows use the 6-op lane-isolated add; W=32 ops count the native 3-op rotate")
for W in (32,64,128,256,512,1024):
    best=None
    for p in list(range(32,40))+[40,44,48]:
        r=variant(W,p)
        if r is None: continue
        lanes,ops,by,bad=r
        if bad: print('  W=%d p=%d INCORRECT (%d bad)'%(W,p,bad)); continue
        ps=ops/lanes
        if best is None or ps<best[0]: best=(ps,p,lanes,ops)
        if W==256: print('  W=256 p=%d lanes=%d ops/batch=%d ops/step=%.3f  and-count=%d  delta vs filed %+0.4f bit'%(p,lanes,ops,ps,by.get('and',0),math.log2(ps/base)))
    print('W=%4d best p=%d lanes=%d ops=%d ops/step=%.3f  delta vs filed (if every op still costs 1/638): %+0.4f bit'%((W,best[1],best[2],best[3],best[0],math.log2(best[0]/base))))
