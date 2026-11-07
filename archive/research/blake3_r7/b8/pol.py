import sys
sys.path.insert(0,'.')
import bsrho_b7 as B
for K in (1,2,3):
    g=B.Gen(256)
    zero=B._constw(0)
    m=[zero]*8+[[g.inputs[32*i+b] for b in range(32)] for i in range(8)]
    v=[B._constw(w) for w in B.IV]+[B._constw(w) for w in B.IV[:4]]+[zero,zero,B._constw(64),B._constw(B.FLAGS)]
    for r in range(K):
        for j,(a,b,c,d) in enumerate(B.GCALLS):
            x,y=m[2*j],m[2*j+1]
            v[a]=g.add(g.add(v[a],v[b]),x)
            v[d]=B._ror_planes(g.xorw(v[d],v[a]),16)
            v[c]=g.add(v[c],v[d])
            v[b]=B._ror_planes(g.xorw(v[b],v[c]),12)
            v[a]=g.add(g.add(v[a],v[b]),y)
            v[d]=B._ror_planes(g.xorw(v[d],v[a]),8)
            v[c]=g.add(v[c],v[d])
            v[b]=B._ror_planes(g.xorw(v[b],v[c]),7)
        m=[m[i] for i in B.PERM]
    print(K,"neg planes",sum(s[1] for w in v for s in w),"const",sum(1 for w in v for s in w if s[0]==0), "negs by word",[sum(s[1] for s in w) for w in v])
