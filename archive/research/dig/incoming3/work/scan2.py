"""extra numbers: where the nonzero-prefix cost sits, injectivity of the D0 q1/q2 maps in m8, fewer free words."""
import sys, os, json, random
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
import b3steps as B
from b3steps import *
res={}
# per-round op totals with zero prefix vs random nonzero prefix
def per_round(consts):
    src,ops,by,rec,tr=build(consts=consts)
    out={}
    for k,v in rec.items():
        if k=="final": out["final"]=v[0]; continue
        out[k[0]]=out.get(k[0],0)+v[0]
    return ops,out
rng=random.Random(5)
z=per_round(None); res["zero_prefix"]=z
res["rand_prefix"]=[per_round([rng.getrandbits(32) for _ in range(8)]+[0]*8) for _ in range(3)]
# a single nonzero prefix word: cost per word (m_i used in rounds r via PERM)
single={}
for i in range(8):
    cs=[0]*16; cs[i]=0x12345678
    single[i]=build(consts=cs)[1]
res["single_nonzero_word_total"]=single
# fewer free words
res["fewer_free"]={n:build(free=range(16-n,16))[1] for n in (8,7,6)}
# injectivity of D0 q1 (a1,d1) and q2 (c1,b1) in m8 on 2^20 values (structural: add/xor/rotate by constants are bijections)
msgz=[0]*8
def d0(m8):
    v=list(IV)+list(IV[:4])+[0,0,64,11]
    for j,(a,b,c,d) in enumerate(GC[:4]):
        x,y=msgz[2*j],msgz[2*j+1]
        v[a]=(v[a]+v[b]+x)&M32; v[d]=B._ror(v[d]^v[a],16); v[c]=(v[c]+v[d])&M32; v[b]=B._ror(v[b]^v[c],12)
        v[a]=(v[a]+v[b]+y)&M32; v[d]=B._ror(v[d]^v[a],8); v[c]=(v[c]+v[d])&M32; v[b]=B._ror(v[b]^v[c],7)
    a,b,c,d=GC[4]
    v[a]=(v[a]+v[b]+m8)&M32; v[d]=B._ror(v[d]^v[a],16); q1=(v[a],v[d])
    v[c]=(v[c]+v[d])&M32; v[b]=B._ror(v[b]^v[c],12); q2=(v[c],v[b])
    return q1,q2
s1=set(); s2=set(); N=1<<20
for i in range(N):
    m8=(i*2654435761)&M32
    q1,q2=d0(m8); s1.add(q1); s2.add(q2)
res["inject_sample"]={"N":N,"distinct_q1":len(s1),"distinct_q2":len(s2)}
json.dump(res,open(os.path.join(HERE,"scan2_out.json"),"w"),indent=1)
print(json.dumps(res,indent=1))
