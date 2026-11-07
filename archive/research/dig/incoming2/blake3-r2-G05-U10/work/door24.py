# Door 24 RELABEL test: own bijection check on E1/E3 inputs over sampled outer steps (our builder, 55/63 pins)
import random,json,itertools
from b3lib import *
rng=random.Random(24)
names=['C0c1','C0d1','D3d1','S15','S9','w5','X2','y']
def tup(p):
    A,B,W4p=build(IV,*p)
    sa,oa=compress(IV,A,55,0,0,11,2); sb,ob=compress(IV,B,63,0,0,11,2)
    assert all(oa[i]==ob[i] for i in (0,2,5,7))
    e1=tuple(s['Y'][i] for s in (sa,sb) for i in (1,6,11,12))+(A[12],A[5],B[12],B[5])   # E1 inputs: Y1,Y6,Y11,Y12, m'10=w12, m'11=w5 (both messages)
    e3=tuple(s['Y'][i] for s in (sa,sb) for i in (3,4,9,14))+(A[15],A[8],B[15],B[8])   # E3 inputs: Y3,Y4,Y9,Y14, m'14=w15, m'15=w8
    return e1,e3
# (1) random sample: are E1 inputs and E3 inputs each injective in the params, and is the joint count = either count?
N=20000; S1=set(); S3=set(); SJ=set()
for _ in range(N):
    e1,e3=tup([rng.getrandbits(32) for _ in range(8)]); S1.add(e1); S3.add(e3); SJ.add((e1,e3))
print('random sample N=',N,'distinct E1 tuples',len(S1),'distinct E3 tuples',len(S3),'distinct joint',len(SJ))
out=dict(random_sample=dict(N=N,E1=len(S1),E3=len(S3),joint=len(SJ)))
# (2) pairwise grids: vary two of the 8 params over n values each, others fixed; Cartesian iff joint = |E1|*|E3| (both >1)
n=12; grids=[]
for i,j in itertools.combinations(range(8),2):
    base=[rng.getrandbits(32) for _ in range(8)]
    vi=[rng.getrandbits(32) for _ in range(n)]; vj=[rng.getrandbits(32) for _ in range(n)]
    s1=set(); s3=set(); sj=set()
    for a in vi:
        for b in vj:
            p=base[:]; p[i]=a; p[j]=b; e1,e3=tup(p); s1.add(e1); s3.add(e3); sj.add((e1,e3))
    grids.append(dict(params=(names[i],names[j]),E1=len(s1),E3=len(s3),joint=len(sj),cartesian=(len(sj)==len(s1)*len(s3) and len(s1)>1 and len(s3)>1)))
    print(grids[-1])
out['grids']=grids
# (3) single-param dependence: which E1 / E3 input coordinates change when one param changes
dep={}
for i in range(8):
    base=[rng.getrandbits(32) for _ in range(8)]; e1,e3=tup(base); c1=set(); c3=set()
    for _ in range(20):
        p=base[:]; p[i]=rng.getrandbits(32); f1,f3=tup(p)
        c1|={k for k in range(len(e1)) if e1[k]!=f1[k]}; c3|={k for k in range(len(e3)) if e3[k]!=f3[k]}
    dep[names[i]]=dict(E1_coords_changed=sorted(c1),E3_coords_changed=sorted(c3))
    print(names[i],dep[names[i]])
out['dependence']=dep
json.dump(out,open('door24.out.json','w'),indent=1)
