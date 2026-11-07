# Memory-free alternatives (Floyd, Brent) on a random mapping: evaluations to FIND A COLLISION PAIR (x != y, f(x)=f(y)),
# in units of sqrt(N); success within a budget E is P(total <= E). Compared with the filed program: Q = 0.99885 sqrt(N) evaluations for success 0.39.
import numpy as np, sys
rng=np.random.default_rng(20261012)
def run(logN,T):
    N=1<<logN; f=rng.integers(0,N,N,dtype=np.int64).tolist()
    fl=[];br=[]
    for _ in range(T):
        x0=int(rng.integers(0,N))
        # Floyd
        t=f[x0]; h=f[f[x0]]; ev=3; i=1
        while t!=h:
            t=f[t]; h=f[f[h]]; ev+=3; i+=1
        # phase 2: find mu and the colliding pair
        t=x0; mu=0; pair=None
        while t!=h:
            pt,ph=t,h; t=f[t]; h=f[h]; ev+=2; mu+=1
        if mu>0: fl.append(ev)   # pair (pt,ph) exists when mu>0
        # Brent
        power=lam=1; t=x0; h=f[x0]; ev=1
        while t!=h:
            if power==lam: t=h; power*=2; lam=0
            h=f[h]; lam+=1; ev+=1
        # find mu: hare is lam ahead of tortoise from x0
        t=x0; h=x0
        for _ in range(lam): h=f[h]; ev+=1
        mu=0
        while t!=h:
            pt,ph=t,h; t=f[t]; h=f[h]; ev+=2; mu+=1
        if mu>0: br.append(ev)
    s=N**0.5
    for nm,a in (('Floyd',fl),('Brent',br)):
        a=np.array(a)/s
        print('N=2^%d %s: trials %d (with a tail, mu>0: %d) mean %.3f sqrtN, quantiles 0.39: %.3f  0.50: %.3f  0.90: %.3f ; filed program: 0.99885 sqrtN at success 0.39'%(logN,nm,T,len(a),a.mean(),np.quantile(a,0.39),np.quantile(a,0.5),np.quantile(a,0.9)))
        print('   bits above filed at equal success 0.39: %.3f ; at success 0.90 (filed would need Q for lambda 2.30: %.3f sqrtN): %.3f'%(np.log2(np.quantile(a,0.39)/0.99885),np.sqrt(2*2.3026),np.log2(np.quantile(a,0.9)/np.sqrt(2*2.3026))))
run(20,6000); run(22,3000)
