import random,sys
from b3lib import *
rng=random.Random(20261012)
N=3000
ok=dict(consts=0,y=0,Sequal=0,Xequal=0,lemmaH=0,notall=0,w01eq=0,diffonly45=0,sA=0)
for _ in range(N):
    a=[rnd(rng) for _ in range(8)]
    d=build(*a)
    A,B=d['A'],d['B']
    sa,oa=compress_full(A,55); sb,ob=compress_full(B,63)
    X=sa['X']
    if (X[3],X[7],X[11],X[15])==(X3,X7,X11,X15): ok['consts']+=1
    if sa['Y'][4]==a[7]: ok['y']+=1
    if sa['Y'][3]==None: pass
    if sa['S']==sb['S']: ok['Sequal']+=1
    if sa['X']==sb['X']: ok['Xequal']+=1
    if all(oa[i]==ob[i] for i in (0,2,5,7)): ok['lemmaH']+=1
    if not all(oa[i]==ob[i] for i in range(8)): ok['notall']+=1
    if A[0]==B[0] and A[1]==B[1]: ok['w01eq']+=1
    if all(A[i]==B[i] for i in range(16) if i not in (4,5)): ok['diffonly45']+=1
    # K0 forward gives S4,S8 (word names)
    if (sa['S'][4],sa['S'][8],sa['S'][0],sa['S'][12])==(d['S4'],d['S8'],d['S0'],d['S12']): ok['sA']+=1
print(N,ok)
assert all(v==N for v in ok.values())
print("VALIDATED: construction reproduces X3/X7/X11/X15, Y4=y, S and X equal, digest words 0,2,5,7 equal on",N,"random 8-word inputs")
