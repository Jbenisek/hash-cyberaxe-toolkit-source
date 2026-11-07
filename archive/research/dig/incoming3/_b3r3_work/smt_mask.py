import sys,json,time,ctypes; sys.path.insert(0,'.')
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)  # BELOW_NORMAL
import b3core as B
from z3 import *
prog,out=B.build(3)
def model(k, tlimit_ms):
    xs=[BitVec('i%d'%(8+i),32) for i in range(8)]
    env={'i%d'%(8+i):ZeroExt(32,xs[i]) for i in range(8)}
    L36=(1<<36)-1
    over=[]
    for n,op in enumerate(prog):
        a=[env[x] for x in op['args']]; kd=op['kind']; im=op['imm']
        imm=(im&L36) if im is not None else None
        if kd=='and':
            r=a[0]&BitVecVal(imm,64)
            if n==k: r=a[0]
        elif kd=='add':
            r=a[0]+(a[1] if len(a)>1 else BitVecVal(imm,64))
            if n>k: over.append(UGE(r,BitVecVal(1<<36,64)))
        elif kd=='xor': r=a[0]^(a[1] if len(a)>1 else BitVecVal(imm,64))
        elif kd=='or': r=a[0]|a[1]
        elif kd=='shr': r=LShR(a[0],im)
        elif kd=='shl': r=a[0]<<im
        env[op['r']]=r
    s=Solver(); s.set('timeout',tlimit_ms); s.add(Or(over)); 
    t0=time.time(); res=s.check()
    ans=str(res); 
    wit=None
    if res==sat:
        m=s.model(); wit=[m.eval(x).as_long() for x in xs]
    return ans,time.time()-t0,wit
ks=[int(a) for a in sys.argv[2:]]; tl=int(sys.argv[1])
for k in ks:
    r=model(k,tl); print(k,prog[k]['tag'],r,flush=True)
    json.dump(dict(k=k,tag=list(prog[k]['tag']),result=r[0],secs=r[1],witness=r[2]),open('smt_mask_%d.json'%k,'w'))
