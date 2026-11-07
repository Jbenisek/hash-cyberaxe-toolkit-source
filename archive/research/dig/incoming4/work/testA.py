
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

import sys,itertools,json
sys.path.insert(0,_hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/orchard/math'))
from pos import *
import math
out={}
# 0 validation
v=json.load(open(ROOT+r'/tests/orchard-upstream-vectors.json'))
ok=0
for row in v['permute']:
    x=[int.from_bytes(bytes.fromhex(h),'little') for h in row]; ok+= full_perm(x[:3])==x[3:]
out['permute_vectors_ok']=f'{ok}/{len(v["permute"])}'
# MDS minors
def det2(a,b,c,d): return (a*d-b*c)%p
z1=sum(1 for i in range(3) for j in range(3) if MDS[i][j]%p==0)
z2=0
for r in itertools.combinations(range(3),2):
    for c in itertools.combinations(range(3),2):
        if det2(MDS[r[0]][c[0]],MDS[r[0]][c[1]],MDS[r[1]][c[0]],MDS[r[1]][c[1]])==0: z2+=1
M=MDS
d3=(M[0][0]*det2(M[1][1],M[1][2],M[2][1],M[2][2])-M[0][1]*det2(M[1][0],M[1][2],M[2][0],M[2][2])+M[0][2]*det2(M[1][0],M[1][1],M[2][0],M[2][1]))%p
out['mds_zero_minors']=dict(order1=z1,order2=z2,order3=int(d3==0))
# chains
subs=[s for k in (1,2,3) for s in itertools.combinations(range(3),k)]
ok_ab=lambda A,B: len(A)+len(B)>=4
chains=[(a,b,c,d) for a in subs for b in subs for c in subs for d in subs if ok_ab(a,b) and ok_ab(b,c) and ok_ab(c,d)]
# last M: output supp t subset {1,2} nonempty, |d|+|t|>=4 -> |d|>=2
fin=[ch for ch in chains if len(ch[3])>=2]
from collections import Counter
wp=Counter(tuple(len(s) for s in ch) for ch in fin)
out['tail']=dict(total_chain_space=7**4,mds_ok=len(chains),with_lane0_zero_output=len(fin),weight_patterns=len(wp),min_total_active=min(sum(w) for w in wp))
# symmetry
sched=list(range(0,4))+[4,5]+list(range(60,64))
out['zero_rc_entries_in_r2_schedule']=sum(1 for k in sched for i in range(3) if RC[k][i]==0)
out['p_mod_4']=p%4
out['i_exists']=True
# inverse exponent
e=E5INV; out['e5inv_over_pm1']=e/(p-1); out['e5inv_form']=(4*(p-1)+1)==5*e
# degree tracker: plane (nk,rho) lane degrees
deg=[1,1,0]
trace=[]
for k,f in [(k,True) for k in range(4)]+[(4,False),(5,False)]+[(k,True) for k in range(60,64)]:
    if f: deg=[5*x for x in deg]
    else: deg[0]*=5
    m=max(deg); deg=[m]*3   # after MDS dense (generic)
    trace.append((k,m))
out['plane_degree_trace_r2']=trace
out['plane_total_degree_r2_log5']=round(math.log(trace[-1][1],5),6)
json.dump(out,open('testA.json','w'),indent=1)
print(json.dumps(out,indent=1))
