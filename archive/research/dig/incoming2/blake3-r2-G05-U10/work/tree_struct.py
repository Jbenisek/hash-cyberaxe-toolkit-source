# word-level structural model of round 1 after every round-0 difference is cancelled (X identical).
# Rule per G call in round 1 (proved: y-only difference makes all 4 outputs differ; x-only can leave b,d equal under a pin):
#  no input difference -> clean; x-only difference -> outputs a,c differ, b,d may be pinned equal; anything else -> all 4 differ
import json,random
from b3lib import P,M,G,IV
from tree_pairs import CALLS,run,dig
COLS=CALLS[:4]; DIAG=CALLS[4:]
def model(msgdiff_words):
    # round-1 message words: m'[i]=m[P[i]]
    md=[False]*16
    for w in msgdiff_words: md[w]=True
    m1=[md[P[i]] for i in range(16)]
    zd=[False]*16   # output difference after round 1 columns (state words Y)
    for k,(a,b,c,d) in enumerate(COLS):
        x,y=m1[2*k],m1[2*k+1]
        if not x and not y: continue
        if x and not y: zd[a]=zd[c]=True       # b,d pinned equal
        else: zd[a]=zd[b]=zd[c]=zd[d]=True
    z2=[False]*16; E=[]
    for k,(a,b,c,d) in enumerate(DIAG):
        x,y=m1[8+2*k],m1[8+2*k+1]
        act = zd[a] or zd[b] or zd[c] or zd[d] or x or y
        E.append(act)
        if act:
            for s in (a,b,c,d): z2[s]=True
    dirty=[z2[i] or z2[i+8] for i in range(8)]
    return dict(colsActive=[k for k,(a,b,c,d) in enumerate(COLS) if m1[2*k] or m1[2*k+1]],diagActive=[k for k,e in enumerate(E) if e],
                cleanDigestWords=[i for i in range(8) if not dirty[i]])
out={}
# message words carrying the cancellation: K0:(w0,w1) K1:(w2,w3) K2:(w4,w5) K3:(w6,w7)
for name,cols in [('length only (K2): AA 55/63',[2]),('flags only (K3): 11 vs 12 or 11 vs 10',[3]),('length+flags (K2,K3): AC, A-B*',[2,3]),
                  ('counter t_lo only (K0)',[0]),('counter t_hi only (K1)',[1]),('K0+K1 (t_lo and t_hi)',[0,1]),('K0+K2',[0,2]),('K1+K2',[1,2]),('K0+K3',[0,3]),('K1+K3',[1,3])]:
    words=[w for c in cols for w in (2*c,2*c+1)]
    out[name]=model(words); print(name,out[name])
json.dump(out,open('tree_struct.out.json','w'),indent=1)
# unit check of the per-call rule on 1e6 random G calls (y-only diff: count equal outputs per slot; x-only: outputs a,c never equal)
import random
rng=random.Random(3); eq_y=[0]*4; eq_x=[0]*4; N=1000000
for _ in range(N):
    v=[rng.getrandbits(32) for _ in range(4)]; x=rng.getrandbits(32); y=rng.getrandbits(32); dd=rng.getrandbits(32) or 1
    def g(v0,x,y):
        u=list(v0)+[0]*12
        G(u,0,1,2,3,x,y); return u[:4]
    r0=g(v,x,y); ry=g(v,x,(y+dd)&M); rx=g(v,(x+dd)&M,y)
    for i in range(4):
        eq_y[i]+= r0[i]==ry[i]; eq_x[i]+= r0[i]==rx[i]
print('1e6 random G calls, y-only difference: equal outputs per slot (a,b,c,d) =',eq_y,'; x-only difference:',eq_x)
