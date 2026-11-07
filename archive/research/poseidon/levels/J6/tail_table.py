"""J6: tail (R60..R63) support-chain table. Exhaustive over ALL ordered pairs (x,y), x!=y, of R60 input states for toy q.
Toy: random Cauchy MDS + random RC (same recipe as atlas facts_toy). Records S-box-input difference support masks s0..s3 and lane-0 collision of output.
usage: python tail_table.py q seed"""
import sys, random, numpy as np, collections, json
q=int(sys.argv[1]); seed=int(sys.argv[2])
rnd=random.Random(seed*1000003+q)
while True:
    xs=rnd.sample(range(q),3); ys=rnd.sample(range(q),3)
    if all((x+y)%q for x in xs for y in ys): break
M=[[pow(x+y,-1,q) for y in ys] for x in xs]
RC=[[rnd.randrange(q) for _ in range(3)] for _ in range(4)]
def rnd_(a,k):
    a=[(a[i]+RC[k][i])%q for i in range(3)]
    a=[pow_(v) for v in a]
    return [(M[i][0]*a[0]+M[i][1]*a[1]+M[i][2]*a[2])%q for i in range(3)]
def pow_(v):
    v2=v*v%q; v4=v2*v2%q; return v4*v%q
N=q**3
allst=np.arange(N,dtype=np.int64)
Y=[allst//(q*q), (allst//q)%q, allst%q]
hist=np.zeros(4096,dtype=np.int64); col=np.zeros(4096,dtype=np.int64)
CH=max(1,2000000//N)
for st in range(0,N,CH):
    xs_=np.arange(st,min(N,st+CH),dtype=np.int64)
    X=[np.repeat(xs_//(q*q),N),np.repeat((xs_//q)%q,N),np.repeat(xs_%q,N)]
    YY=[np.tile(Y[i],len(xs_)) for i in range(3)]
    code=np.zeros(len(X[0]),dtype=np.int64)
    a=X;b=YY
    for k in range(4):
        d=[(a[i]-b[i])%q for i in range(3)]
        mask=(d[0]!=0)*1+(d[1]!=0)*2+(d[2]!=0)*4
        code=code*8+mask
        a=[(a[i]+RC[k][i])%q for i in range(3)]; b=[(b[i]+RC[k][i])%q for i in range(3)]
        a=[(v*v%q)*(v*v%q)%q*v%q for v in a]; b=[(v*v%q)*(v*v%q)%q*v%q for v in b]
        a=[(M[i][0]*a[0]+M[i][1]*a[1]+M[i][2]*a[2])%q for i in range(3)]
        b=[(M[i][0]*b[0]+M[i][1]*b[1]+M[i][2]*b[2])%q for i in range(3)]
    c=((a[0]==b[0]))
    ne=(code//512)%8 != 0  # s0 != 0 (x!=y); code digits: s0 is top (shift 3*3)
    # first digit s0 is bits 9..11
    s0=(code>>9)&7
    ok=s0!=0
    hist+=np.bincount(code[ok],minlength=4096)
    col+=np.bincount(code[ok&c],minlength=4096)
out={'q':q,'seed':seed,'M':M,'hist':{int(i):int(h) for i,h in enumerate(hist) if h},'col':{int(i):int(h) for i,h in enumerate(col) if h}}
json.dump(out,open(f'tail_q{q}_s{seed}.json','w'))
print('done',q,sum(hist),sum(col))
