
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

import sys,random,json,struct,itertools,time
sys.path.insert(0,_hca_public_path_text('__HCA_WORKSPACE__/hash-smash'))
from verifier import blake3 as vb
from b3lib import *
rng=random.Random(20261012)
def rnd(): return rng.getrandbits(32)
def mk(LA,LB,params=None):
    p=params or [rnd() for _ in range(8)]
    A,B,W4p=build(IV,*p,LA=LA,delta=LA^LB)
    sa,oa=compress(IV,A,LA,0,0,11,2); sb,ob=compress(IV,B,LB,0,0,11,2)
    return p,A,B,W4p,sa,sb,oa,ob
res={}
t0=time.time()
# ---- Q1 : control 55/63
N=3000; kset={}; xid=0; pins=0; oth=0; vcheck=0
for _ in range(N):
    p,A,B,W4p,sa,sb,oa,ob=mk(55,63)
    xid+= sa['X']==sb['X']; pins+= (sa['X'][3],sa['X'][7],sa['X'][11],sa['X'][15])==(X3,X7,X11,X15)
    eq=tuple(i for i in range(8) if oa[i]==ob[i]); kset[eq]=kset.get(eq,0)+1
    if _<300:
        ba=struct.pack('<16I',*A)[:55]; bb=struct.pack('<16I',*B)[:63]
        assert B[13]>>24==0 and A[13]>>24==0 and A[14]==A[15]==B[14]==B[15]==0
        ha,hb=vb.blake3(ba,2),vb.blake3(bb,2)
        assert ha==struct.pack('<8I',*oa) and hb==struct.pack('<8I',*ob)
        vcheck+=1
res['Q1']=dict(N=N,X_identical=xid,pins_hold=pins,equal_word_sets={str(k):v for k,v in kset.items()},verifier_byte_level=vcheck,K='%08x'%((IV[2]+IV[6])&M),
               W4p_minus_W4=(W4p-W4)&M)
# v14 reader check: perturb initial v14, which round-0 calls see a different input?
from tree_pairs import run
w=[rnd() for _ in range(16)]
v0,tr0=run(IV,w,0,55,11); v1,tr1=run(IV,w,0,55^1,11)
readers=[k for (a,b) in zip(tr0,tr1) if a[0]==0 for k in [a[1]] if a[2:]!=b[2:]]
res['Q1']['round0_calls_whose_input_changes_when_v14_changes']=readers
print('Q1',res['Q1'])
# ---- Q2 : all ordered pairs (LA holds W4)
rows={}
T=12
for LA in range(1,65):
    for LB in range(1,65):
        if LA==LB: continue
        ok_x=0; eqs={}
        for _ in range(T):
            p,A,B,W4p,sa,sb,oa,ob=mk(LA,LB)
            ok_x+= sa['X']==sb['X']
            eq=tuple(i for i in range(8) if oa[i]==ob[i]); eqs[eq]=eqs.get(eq,0)+1
        rows[(LA,LB)]=dict(X_identical=ok_x,Delta=(W4p-W4+2**31)%2**32-2**31,eq=eqs)
print('Q2 scan time',round(time.time()-t0,1))
full4=[k for k,v in rows.items() if v['eq'].get((0,2,5,7),0)==T]
anyeq=[k for k,v in rows.items() if any(e for e in v['eq'])]
legal=lambda k: min(k)>=55 and max(k)<=64
res['Q2']=dict(trials_per_pair=T,ordered_pairs=len(rows),X_identical_all=all(v['X_identical']==T for v in rows.values()),
    pairs_with_digest_words_0_2_5_7_equal=[list(k) for k in full4],pairs_with_any_digest_word_equal=[list(k) for k in anyeq],
    legal_with_pinned_W13_ordered=sum(1 for k in rows if legal(k)),legal_unordered=sum(1 for k in rows if legal(k))//2,
    legal_and_full4=[list(k) for k in full4 if legal(k)],
    Delta_by_pair_legal={('%d,%d'%k):v['Delta'] for k,v in rows.items() if legal(k)})
print('Q2',{k:v for k,v in res['Q2'].items() if k!='Delta_by_pair_legal'})
# bytes honesty check on the legal pairs that work
for (LA,LB) in full4:
    if legal((LA,LB)):
        p,A,B,W4p,sa,sb,oa,ob=mk(LA,LB)
        ba=struct.pack('<16I',*A)[:LA]; bb=struct.pack('<16I',*B)[:LB]
        # honest iff the words reproduce from bytes
        assert struct.unpack('<16I',ba.ljust(64,b'\0'))==tuple(A) and struct.unpack('<16I',bb.ljust(64,b'\0'))==tuple(B),(LA,LB)
        assert vb.blake3(ba,2)==struct.pack('<8I',*oa) and vb.blake3(bb,2)==struct.pack('<8I',*ob)
# ---- Q3 : injectivity / dimension of the builder
seen=set(); rec=0; N3=20000
for _ in range(N3):
    p,A,B,W4p,sa,sb,oa,ob=mk(55,63)
    seen.add(tuple(A))
    rec+= (A[5]==p[5]) and (sa['Y'][4]==p[7])
res['Q3']=dict(N=N3,distinct_A=len(seen),w5_and_Y4_recovered_from_A=rec)
print('Q3',res['Q3'])
# ---- Q4: k>=5 check over many 55/63 pairs, and equal-length necessity
mx=0
for _ in range(20000):
    p,A,B,W4p,sa,sb,oa,ob=mk(55,63); mx=max(mx,sum(oa[i]==ob[i] for i in range(8)))
res['Q4']=dict(N=20000,max_equal_digest_words=mx)
# toy: width 8 G, same state, (x,y)->4 outputs injective
def tg(a,b,c,d,x,y,n=8,r=(4,3,2,1)):
    m=(1<<n)-1; rr=lambda v,k:((v>>k)|(v<<(n-k)))&m
    a=(a+b+x)&m; d=rr(d^a,r[0]); c=(c+d)&m; b=rr(b^c,r[1]); a=(a+b+y)&m; d=rr(d^a,r[2]); c=(c+d)&m; b=rr(b^c,r[3]); return (a,b,c,d)
col=0
for _ in range(30):
    s=[rng.getrandbits(8) for _ in range(4)]
    outs=set(tg(*s,x,y) for x in range(256) for y in range(256)); col+= 65536-len(outs)
res['Q4']['toy8_same_state_xy_collisions']=col
print('Q4',res['Q4'])
json.dump(res,open('mode_len.out.json','w'),indent=1,default=str)
