"""Hill climb: can the true lane value before an internal mask reach the overflow threshold? numpy single-lane model of the shipped circuit.
Success (S >= 2^36) would prove the mask necessary (own witness, checked against the packed circuit). Failure = a lower bound on the maximum only."""
import sys,time,json,ctypes; sys.path.insert(0,'.')
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
import numpy as np, b3core as B
prog,out=B.build(3)
L36=(1<<36)-1
def evalv(X,upto):
    env={'i%d'%(8+i):X[i].astype(np.uint64) for i in range(8)}
    for o in prog[:upto+1]:
        a=[env[x] for x in o['args']]; kd=o['kind']; im=o['imm']; il=np.uint64(im&L36) if im is not None else None
        if kd=='and': r=a[0]&il
        elif kd=='add': r=a[0]+(a[1] if len(a)>1 else il)
        elif kd=='xor': r=a[0]^(a[1] if len(a)>1 else il)
        elif kd=='or': r=a[0]|a[1]
        elif kd=='shr': r=a[0]>>np.uint64(im)
        elif kd=='shl': r=a[0]<<np.uint64(im)
        env[o['r']]=r
    return env
def run(k,secs,seed):
    rng=np.random.default_rng(seed)
    a_name=prog[k]['args'][0]; add=prog[k+1]; other=[x for x in add['args'] if x!=prog[k]['r']][0]
    P=1<<15
    X=rng.integers(0,1<<32,size=(8,P),dtype=np.uint64)
    t0=time.time(); best=0; gen=0; hist=[]
    while time.time()-t0<secs:
        env=evalv(X,k)
        S=env[a_name].astype(np.float64)+env[other].astype(np.float64)
        idx=np.argsort(-S)[:P//16]
        if S[idx[0]]>best: best=S[idx[0]]; hist.append((gen,best/2**32))
        if best>=2**36: break
        top=X[:,idx]
        # children: copy elites, flip 1-3 random bits in random words, sometimes replace a word
        rep=np.repeat(top,16,axis=1)[:, :P].copy()
        for _ in range(rng.integers(1,4)):
            w=rng.integers(0,8,size=P); b=rng.integers(0,32,size=P)
            rep[w,np.arange(P)]^=(np.uint64(1)<<b.astype(np.uint64))
        m=rng.random(P)<0.02
        rep[rng.integers(0,8),np.where(m)[0]]=rng.integers(0,1<<32,size=m.sum(),dtype=np.uint64)
        rep[:,:P//16]=top   # keep elites
        X=rep; gen+=1
    i=np.argmax(S)
    return dict(k=k,tag=list(prog[k]['tag']),best_sum_units=best/2**32,threshold_units=16.0,gens=gen,reached=bool(best>=2**36),witness=[int(X[w,i]) for w in range(8)],trace=hist[-5:])
if __name__=='__main__':
    secs=int(sys.argv[1]); res=[]
    for k in map(int,sys.argv[2:]):
        r=run(k,secs,k); print(r,flush=True); res.append(r)
        json.dump(r,open('hc_%d.json'%k,'w'))
