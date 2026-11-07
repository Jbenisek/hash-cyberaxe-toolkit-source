"""U10: X6 trail check, done correctly. Two states at R4 entry differing by d=(0,M02,-M01) (r=2): R4 S-box sees equal lane 0,
output diff = M(0,d1,d2) has lane 0 = M01*M02-M02*M01 = 0, so R5's S-box also sees equal lane 0.
Checks: (1) lane 0 equal after R4.M, (2) lane 0 equal at R5.S input, (3) output diff after R5.M == M*(0,d1',d2') (linear), and
what happens for a random d with d0=0 (X6 says only 1 free dim survives two partial rounds). Real p and toys (Cauchy / non-Cauchy)."""

# Publication path adapter: resolve data paths from the extracted source tree.
def _hca_public_path_text(value):
    if "__HCA_WORKSPACE__/" not in value:
        return value
    import os as _hca_os
    from pathlib import Path as _hca_Path
    root = _hca_os.environ.get("HASHCYBERAXE_WORKSPACE")
    if root is None:
        here = _hca_Path(__file__).resolve().parent
        root = next((str(p) for p in (here, *here.parents) if (p / "research").is_dir()), None)
    if root is None:
        raise FileNotFoundError("Extract the research source tree, or set HASHCYBERAXE_WORKSPACE to its archive directory.")
    return value.replace("__HCA_WORKSPACE__/", str(_hca_Path(root).resolve()).replace("\\", "/") + "/")

import sys, random
sys.path.insert(0,_hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/orchard/impl'))
import poseidon_ref as P
sys.path.insert(0,_hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/levels/U10'))
from toylib import *
rnd=random.Random(9)
def trial(q,MD,RC,label,n=500):
    def pr(s,idx):
        s=[(s[i]+RC[idx][i])%q for i in range(3)]; s[0]=pow(s[0],5,q)
        return [sum(MD[i][j]*s[j] for j in range(3))%q for i in range(3)]
    def mv(v): return [sum(MD[i][j]*v[j] for j in range(3))%q for i in range(3)]
    d=[0,MD[0][2],(-MD[0][1])%q]
    c1=c3=0; rnd_equal=0
    for _ in range(n):
        s=[rnd.randrange(q) for _ in range(3)]; s2=[(s[i]+d[i])%q for i in range(3)]
        a=pr(s,4);b=pr(s2,4)
        c1+= a[0]==b[0]
        a2=pr(a,5);b2=pr(b,5)
        dd=[(b[i]-a[i])%q for i in range(3)]
        c3+= [(b2[i]-a2[i])%q for i in range(3)]==mv([0,dd[1],dd[2]])
        # random d with d0=0
        e=[0,rnd.randrange(1,q),rnd.randrange(1,q)]; s3=[(s[i]+e[i])%q for i in range(3)]
        x=pr(pr(s,4),5); y=pr(pr(s3,4),5)
        rnd_equal+= x[0]==y[0]
    print(f"{label}: lane0 equal after R4.M {c1}/{n}; R5 output diff == M(0,d1',d2') {c3}/{n}; random d (d0=0, generic) lane0 equal after R4,R5: {rnd_equal}/{n}")
trial(P.P,P.MDS,P.RC,"REAL p, real Cauchy M")
for q,cau in ((257,True),(257,False),(1000003,True),(1000003,False)):
    t=Toy(q,5,cauchy=cau); trial(q,t.M,t.RC,f"toy q={q} cauchy={cau}")
# generic: how many (d1:d2) directions at q=257 keep lane 0 equal after R4,R5 ? count by brute force over all d1,d2 (and 1 random state)
q=257; t=Toy(q,5); MD=t.M
def pr(s,idx):
    s=[(s[i]+t.RC[idx][i])%q for i in range(3)]; s[0]=pow(s[0],5,q)
    return [sum(MD[i][j]*s[j] for j in range(3))%q for i in range(3)]
good=[]
for trials in range(3):
    s=[rnd.randrange(q) for _ in range(3)]; x=pr(s,4); gs=[]
    for d1 in range(q):
        for d2 in range(q):
            s2=[s[0],(s[1]+d1)%q,(s[2]+d2)%q]
            y=pr(s2,4)
            if y[0]==x[0] and (d1,d2)!=(0,0): gs.append((d1,d2))
    line={(c*MD[0][2]%q,(-c*MD[0][1])%q) for c in range(1,q)}
    inl=len(line&set(gs))
    print(f"toy q=257 fixed state {s}: nonzero (d1,d2) with d0=0 and equal lane 0 after R4.M (= R5 S-box sees no difference): {len(gs)} total (linear condition, exactly q-1=256 expected); of the 256 nonzero points on the predicted line c*(M02,-M01): {inl} found")
