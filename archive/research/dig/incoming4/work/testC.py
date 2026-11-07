import random,json,math
from collections import Counter
def run(q,seed,r=2):
    rnd=random.Random(seed)
    xs=rnd.sample(range(q),6); 
    # Cauchy matrix 1/(x_i+y_j)
    X=xs[:3];Y=xs[3:]
    M=[[pow((X[i]+Y[j])%q,-1,q) for j in range(3)] for i in range(3)]
    rounds=4+r+4
    RC=[[rnd.randrange(q) for _ in range(3)] for _ in range(rounds)]
    cap=rnd.randrange(q)
    full=[True]*4+[False]*r+[True]*4
    def step(s,k):
        s=[(s[i]+RC[k][i])%q for i in range(3)]
        if full[k]: s=[pow(x,5,q) for x in s]
        else: s[0]=pow(s[0],5,q)
        return [sum(M[i][j]*s[j] for j in range(3))%q for i in range(3)]
    hist=[]  # per input: lane0 after R3 (k=3), after each partial, final
    data=[]
    for a in range(q):
        for b in range(q):
            s=[a,b,cap]; lane=[]
            for k in range(rounds):
                s=step(s,k); lane.append(s[0])
            data.append(lane)
    return data,rounds
q=103
res={}
for seed in (1,2,3):
    data,R=run(q,seed)
    # lane0 after R3 = index 3; after R4 = idx4 ; after R5 = idx5; final idx R-1
    out={}
    for name,idx in (('R4',4),('R5',5),('final',R-1)):
        # global balance: histogram over all q^2 inputs
        h=Counter(d[idx] for d in data); mx=max(h.values()); mn=min(h.get(v,0) for v in range(q))
        # surface restricted: group by lane0 after R3; avg distinct values after idx
        groups={}
        for d in data: groups.setdefault(d[3],[]).append(d[idx])
        avg_d=sum(len(set(g)) for g in groups.values())/len(groups)
        avg_sz=sum(len(g) for g in groups.values())/len(groups)
        # random expectation for g balls in q bins
        exp=q*(1-(1-1/q)**avg_sz)
        out[name]=dict(global_min=mn,global_max=mx,global_mean=q,surf_groups=len(groups),surf_avg_size=round(avg_sz,2),surf_avg_distinct=round(avg_d,2),random_expect_distinct=round(exp,2))
    res[seed]=out
    print(seed,json.dumps(out),flush=True)
json.dump(res,open('testC.json','w'),indent=1)
