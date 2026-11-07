"""Pure arithmetic table: chains (s0,s1,s2,s3) of S-box-input difference supports through R60..R63, with final lane-0 collision.
Feasibility = branch number (|s_k|+|s_{k+1}|>=4 across each M), |s3|>=2 (M row 0 all nonzero). Predicted pair count ~ q^(3+|s0|) * prod(zero conds) / q (collision) ,
approx exact: ordered pairs ~ N_s0 * q^3 * (q-1)^|s0| / q^(zeros) / q.
Also checks real MDS minors."""

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

import itertools, json, sys
pc=lambda m: bin(m).count('1')
chains=[]
for c in itertools.product(range(1,8),repeat=4):
    if all(pc(c[k])+pc(c[k+1])>=4 for k in range(3)) and pc(c[3])>=2: chains.append(c)
print(len(chains),'feasible support chains (of',7**4,')')
def dim(c):
    zeros=sum(3-pc(m) for m in c[1:])
    return 3+pc(c[0])-zeros-1
import collections
bydim=collections.Counter(); 
for c in chains: bydim[(sum(pc(m) for m in c),dim(c))]+=1
print('(total active, pair-dim) -> number of chains')
for k in sorted(bydim): print(k,bydim[k])
mx=max(dim(c) for c in chains)
# weight-pattern summary (by weights only)
w=collections.Counter(tuple(pc(m) for m in c) for c in chains)
print('weight patterns feasible:',len(w))
for k in sorted(w,key=lambda t:(sum(t),t)): 
    d=3+k[0]-sum(3-x for x in k[1:])-1
    print(k,'active',sum(k),'support-chains',w[k],'pair dim',d)
# real MDS
sys.path.insert(0,_hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/orchard/impl'))
try:
    import poseidon_ref as R
    Mr=R.MDS;p=R.P
    ent=all(Mr[i][j]%p for i in range(3) for j in range(3))
    mins=all((Mr[a][c]*Mr[b][d]-Mr[a][d]*Mr[b][c])%p for a in range(3) for b in range(a+1,3) for c in range(3) for d in range(c+1,3))
    det=(Mr[0][0]*(Mr[1][1]*Mr[2][2]-Mr[1][2]*Mr[2][1])-Mr[0][1]*(Mr[1][0]*Mr[2][2]-Mr[1][2]*Mr[2][0])+Mr[0][2]*(Mr[1][0]*Mr[2][1]-Mr[1][1]*Mr[2][0]))%p
    print('real MDS entries nonzero',ent,'2x2 minors nonzero',mins,'det nonzero',det!=0)
except Exception as e: print('real MDS check failed',e)
