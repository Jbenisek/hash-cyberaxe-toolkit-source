import random, json
from opcount import *
M=0xFFFFFFFF
def rol(x,n): return ((x<<n)|(x>>(32-n)))&M
def ror(x,n): return ((x>>n)|(x<<(32-n)))&M
FL=10  # CHUNK_END|ROOT, last block of a 2-block chunk
def col_g(i,a,b,c,d,x=0,y=0):
    a1=(a+b+x)&M; d1=ror(d^a1,16); c1=(c+d1)&M; b1=ror(b^c1,12)
    a2=(a1+b1+y)&M; d2=ror(d1^a2,8); c2=(c1+d2)&M; b2=ror(b1^c2,7)
    return a2,b2,c2,d2
def solve_D(i,t,d,c):
    """cv pair (a,b) for column i such that post-column d2==0 (x=y=0): a1=t free"""
    d1=ror(d^t,16); c1=(c+d1)&M; b1=(d1-t)&M; b=rol(b1,12)^c1; a=(t-b)&M
    return a,b
def solve_DC(i,d,c):
    d1=(-c)&M; t=rol(d1,16)^d; return solve_D(i,t,d,c)
random.seed(11)
dvec=[0,0,64,FL]
res={}
for trial in range(5):
    cv=[random.getrandbits(32) for _ in range(8)]
    for j in range(0,5):
        cc=list(cv)
        for i in range(j):
            a,b=solve_D(i,random.getrandbits(32),dvec[i],IV[i]); cc[i]=a; cc[i+4]=b
            assert col_g(i,a,b,IV[i],dvec[i])[3]==0
        res.setdefault(("D",j),[]).append(trace(cv=tuple(cc),flags=FL)[0])
    cc=list(cv); a,b=solve_DC(0,dvec[0],IV[0]); cc[0]=a; cc[4]=b
    r=col_g(0,a,b,IV[0],dvec[0]); assert r[2]==0 and r[3]==0
    res.setdefault(("DC",1),[]).append(trace(cv=tuple(cc),flags=FL)[0])
    cc=list(cv)
    for i in range(4):
        a,b=solve_DC(i,dvec[i],IV[i]); cc[i]=a; cc[i+4]=b
    res.setdefault(("DC",4),[]).append(trace(cv=tuple(cc),flags=FL)[0])
for k,v in sorted(res.items()): print(k,"ops",sorted(set(v)))
json.dump({str(k):sorted(set(v)) for k,v in res.items()},open("exp_multi.json","w"))
# real-search sanity on a reduced word: how often does a random cv pair satisfy D=0 for column 0 at width 32? cost 2^32 -> report expected only
