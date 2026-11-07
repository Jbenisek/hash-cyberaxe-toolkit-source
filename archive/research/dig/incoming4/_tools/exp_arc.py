import json, random
from eng import *
random.seed(55)
def run(nk,rho,rcs,sbs,sched=None):
    s=[nk,rho,CAPACITY]
    for idx in schedule(1):
        rc=rcs[idx]; sb=sbs[idx]
        s=[(s[i]+rc[i])%P for i in range(3)]
        s=[pow(s[i],5,P) if sb[i] else s[i] for i in range(3)]
        s=[sum(MDS[i][k]*s[k] for k in range(3))%P for i in range(3)]
    return s[0]
rcs0={i:tuple(RC[i]) for i in range(64)}
sbs={i:((1,1,1) if (i<4 or i>=60) else (1,0,0)) for i in range(64)}
res={}
N=6
# R0 lane L in {0,1}: drop constant, shift input
for L in (0,1):
    ok=0
    for _ in range(N):
        nk,rho=random.randrange(P),random.randrange(P)
        r2=dict(rcs0); c=list(r2[0]); cL=c[L]; c[L]=0; r2[0]=tuple(c)
        a=[nk,rho]; a[L]=(a[L]-cL)%P   # var(input a)= S(a_L + 0 ...) ; ref input = nk means (nk + c); var input must be nk + c
        a=[nk,rho]; a[L]=(a[L]+cL)%P
        ok+= run(a[0],a[1],r2,sbs)==run(nk,rho,rcs0,sbs)
    res['R0.L%d.ARC_relabel'%L]=(ok,N)
# partial round P1 (idx 4) lanes 1,2: absorb into R60 constants by M*(c e_L)
for L in (1,2):
    ok=0
    for _ in range(N):
        nk,rho=random.randrange(P),random.randrange(P)
        r2=dict(rcs0); c=list(r2[4]); cL=c[L]; c[L]=0; r2[4]=tuple(c)
        nxt=list(r2[60]); 
        for i in range(3): nxt[i]=(nxt[i]+MDS[i][L]*cL)%P
        r2[60]=tuple(nxt)
        ok+= run(nk,rho,r2,sbs)==run(nk,rho,rcs0,sbs)
    res['P1.L%d.ARC_absorb_into_R60'%L]=(ok,N)
# negative control: P1 lane 0 (S-boxed) absorb attempt
ok=0
for _ in range(N):
    nk,rho=random.randrange(P),random.randrange(P)
    r2=dict(rcs0); c=list(r2[4]); cL=c[0]; c[0]=0; r2[4]=tuple(c)
    nxt=list(r2[60])
    for i in range(3): nxt[i]=(nxt[i]+MDS[i][0]*cL)%P
    r2[60]=tuple(nxt)
    ok+= run(nk,rho,r2,sbs)==run(nk,rho,rcs0,sbs)
res['P1.L0.ARC_absorb_attempt(negative control)']=(ok,N)
# R2/R3/R60.. S-boxed lane control
for idx in (2,60,63):
  for L in range(3):
    ok=0
    for _ in range(N):
        nk,rho=random.randrange(P),random.randrange(P)
        r2=dict(rcs0); c=list(r2[idx]); cL=c[L]; c[L]=0; r2[idx]=tuple(c)
        if idx<63:
            nidx={2:3,60:61}[idx]; nxt=list(r2[nidx])
            for i in range(3): nxt[i]=(nxt[i]+MDS[i][L]*cL)%P
            r2[nidx]=tuple(nxt)
        ok+= run(nk,rho,r2,sbs)==run(nk,rho,rcs0,sbs)
    res['R%d.L%d.ARC_absorb_attempt(negative control)'%(idx,L)]=(ok,N)
print(json.dumps(res,indent=0)); json.dump(res,open('arc.json','w'))
