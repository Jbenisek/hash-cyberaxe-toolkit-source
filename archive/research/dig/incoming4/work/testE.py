import random,json,ctypes
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
def toy(q,seed,r=2):
    rnd=random.Random(seed); xs=rnd.sample(range(q),6); X=xs[:3];Y=xs[3:]
    M=[[pow((X[i]+Y[j])%q,-1,q) for j in range(3)] for i in range(3)]
    R=4+r+4; RC=[[rnd.randrange(q) for _ in range(3)] for _ in range(R)]; cap=rnd.randrange(q)
    full=[True]*4+[False]*r+[True]*4
    def step(s,k):
        s=[(s[i]+RC[k][i])%q for i in range(3)]
        s=[pow(x,5,q) for x in s] if full[k] else [pow(s[0],5,q),s[1],s[2]]
        return tuple(sum(M[i][j]*s[j] for j in range(3))%q for i in range(3))
    return M,step,R,cap
res={}
q=103
for seed in range(1,6):
    M,step,R,cap=toy(q,seed)
    u=(0,M[0][2],(-M[0][1])%q)
    # check trail property
    Mu=[sum(M[i][j]*u[j] for j in range(3))%q for i in range(3)]
    img={}  # state after R3 -> digest
    for a in range(q):
        for b in range(q):
            s=(a,b,cap)
            for k in range(4): s=step(s,k)
            t=s
            for k in range(4,R): t=step(t,k)
            img[s]=t[0]
    def count(dirv):
        pairs=0;coll=0
        for s,d in img.items():
            for t in range(1,q):
                y=tuple((s[i]+t*dirv[i])%q for i in range(3))
                if y in img:
                    pairs+=1; coll+= (img[y]==d)
        return pairs//2,coll//2
    tp,tc=count(u)
    rnd=random.Random(99+seed); ctrl=[]
    for _ in range(3):
        v=(rnd.randrange(1,q),rnd.randrange(q),rnd.randrange(q)); ctrl.append(count(v))
    res[seed]=dict(Mu0=Mu[0],trail_pairs=tp,trail_collisions=tc,trail_rate=round(tc/max(tp,1),5),ctrl=ctrl,ctrl_rate=round(sum(c[1] for c in ctrl)/max(1,sum(c[0] for c in ctrl)),5),random_rate=round(1/q,5))
    print(seed,res[seed],flush=True)
json.dump(res,open('testE.json','w'),indent=1)
