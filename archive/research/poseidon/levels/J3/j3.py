"""J3: agreement lattice. Levels (post-MDS state after round): R0..R5 (r=2), R60..R63. For lane i and subset S of levels,
count unordered input pairs with equal lane i at every level in S; compare with N2*prod(p_L) (p_L = single-level equal-pair prob).
usage: python j3.py q seed"""
import sys, random, math, json, itertools
import numpy as np
q=int(sys.argv[1]); seed=int(sys.argv[2]); r=2
assert math.gcd(5,q-1)==1
rnd=random.Random(seed*1000003+q); cap=pow(2,65,q)
while True:
    xs=rnd.sample(range(q),3); ys=rnd.sample(range(q),3)
    if all((x+y)%q for x in xs for y in ys): break
M=[[pow(x+y,-1,q) for y in ys] for x in xs]
RC=[[rnd.randrange(q) for _ in range(3)] for _ in range(64)]
sched=[(i,True) for i in range(4)]+[(i,False) for i in range(4,4+r)]+[(i,True) for i in range(60,64)]
names=['R0','R1','R2','R3','R4','R5','R60','R61','R62','R63']
def det3(m): 
    return (m[0][0]*(m[1][1]*m[2][2]-m[1][2]*m[2][1])-m[0][1]*(m[1][0]*m[2][2]-m[1][2]*m[2][0])+m[0][2]*(m[1][0]*m[2][1]-m[1][1]*m[2][0]))%q
e=[M[0][j] for j in range(3)] # not used
NK=np.repeat(np.arange(q,dtype=np.int64),q); RHO=np.tile(np.arange(q,dtype=np.int64),q)
s=[NK,RHO,np.full_like(NK,cap)]
lev=[]
for idx,full in sched:
    s=[(s[i]+RC[idx][i])%q for i in range(3)]
    for i in (range(3) if full else range(1)):
        x2=s[i]*s[i]%q; x4=x2*x2%q; s[i]=x4*s[i]%q
    s=[(M[i][0]*s[0]+M[i][1]*s[1]+M[i][2]*s[2])%q for i in range(3)]
    lev.append([a.copy() for a in s])
N=q*q; N2=N*(N-1)//2
def pairs(key):
    c=np.bincount(np.unique(key,return_inverse=True)[1].ravel())
    return int((c*(c-1)//2).sum())
L=len(names)
out={'q':q,'seed':seed,'names':names,'cells':{}}
for lane in range(3):
    v=[lev[l][lane] for l in range(L)]
    p=[pairs(v[l])/N2 for l in range(L)]
    out['p%d'%lane]=p
    # DFS refine
    def rec(start,key,sub,prod):
        for l in range(start,L):
            k=np.unique(key*q+v[l],return_inverse=True)[1].ravel().astype(np.int64) if key is not None else v[l]
            c=np.bincount(k); cnt=int((c*(c-1)//2).sum())
            pr=prod*p[l]; sb=sub+[l]
            out['cells']['%d|%s'%(lane,','.join(names[x] for x in sb))]=(cnt,N2*pr)
            if cnt>0: rec(l+1,k,sb,pr)
            else:
                # all supersets are 0 too
                def zero(st,sub2,pr2):
                    for m in range(st,L):
                        out['cells']['%d|%s'%(lane,','.join(names[x] for x in sub2+[m]))]=(0,N2*pr2*p[m]); zero(m+1,sub2+[m],pr2*p[m])
                zero(l+1,sb,pr)
    rec(0,None,[],1.0)
json.dump(out,open('out_q%d_s%d.json'%(q,seed),'w'))
print('q',q,'seed',seed,'det[e0;e0M;e0M^2]-type det',None,'cells',len(out['cells']))
