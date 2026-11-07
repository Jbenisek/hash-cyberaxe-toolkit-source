import sys, time, json, hashlib
sys.path.insert(0,'.')
import rho_r56 as R
out={}
for w,steps,mcap,gmax,T in ((20,16384,1024,600,16),(24,131072,8192,2500,6)):
    R.NB=w; R._cache.clear()
    # density 1/16 as in rho.py
    t0=time.time(); pairs=[]; evs=[]; fail=0
    for t in range(T):
        x0=int(hashlib.sha256(b"h1ev%d-%d"%(w,t)).hexdigest(),16)%(1<<w)
        pair,st,ev,ops=R.search(R.F_n,R.is_dp_n,x0,steps,mcap,gmax)
        evs.append(ev)
        if pair is None: fail+=1
        else:
            a,b=pair; assert a!=b and R.F_n(a)==R.F_n(b)
            pairs.append((R.enc(a)+bytes(32),R.enc(b)+bytes(32)))
    dt=time.time()-t0
    print(w,"trials",T,"pairs",len(pairs),"fail",fail,"mean evals",sum(evs)/len(evs),"sqrtN",2**(w/2),"secs",round(dt,1),flush=True)
    out[w]=[(a.hex(),b.hex()) for a,b in pairs]
json.dump(out,open('pairs.json','w'))
