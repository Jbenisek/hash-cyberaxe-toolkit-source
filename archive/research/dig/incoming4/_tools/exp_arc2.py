import json, random
from eng import *
random.seed(56)
sched=schedule(1)
def run(nk,rho,rcs):
    s=[nk,rho,CAPACITY]
    for idx in sched:
        full=(idx<4 or idx>=60)
        s=[(s[i]+rcs[idx][i])%P for i in range(3)]
        s=[pow(s[i],5,P) if (full or i==0) else s[i] for i in range(3)]
        s=[sum(MDS[i][k]*s[k] for k in range(3))%P for i in range(3)]
    return s[0]
base={i:tuple(RC[i]) for i in range(64)}
res={}
N=6
for pos,idx in enumerate(sched):
    for L in range(3):
        ok=0
        for _ in range(N):
            nk,rho=random.randrange(P),random.randrange(P)
            r2=dict(base); c=list(r2[idx]); cL=c[L]; c[L]=0; r2[idx]=tuple(c)
            if idx==0 and L<2:
                a=[nk,rho]; a[L]=(a[L]+cL)%P; ok+= run(a[0],a[1],r2)==run(nk,rho,base); continue
            if pos+1<len(sched):
                nidx=sched[pos+1]; nxt=list(r2[nidx])
                for i in range(3): nxt[i]=(nxt[i]+MDS[i][L]*cL)%P
                r2[nidx]=tuple(nxt)
            ok+= run(nk,rho,r2)==run(nk,rho,base)
        res['%d.L%d'%(idx,L)]=(ok,N)
print(res); json.dump(res,open('arc2.json','w'))
