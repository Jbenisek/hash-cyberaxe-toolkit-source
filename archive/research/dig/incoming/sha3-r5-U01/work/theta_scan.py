
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

import types,sys
sys.modules.setdefault("numpy",types.SimpleNamespace(array=lambda *a,**k:None,uint64=int,int64=int,zeros=lambda *a,**k:None))
"""Q4 theta scan, r5 rounds 0,1,2,4. Own Keccak (tools/traillab/sha3_atlas/kk.py), real collision pairs from the pkgR5L certificates."""
import json, glob, os, collections
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/tools/traillab/sha3_atlas'))
from kk import *
RC=[0x1,0x8082,0x800000000000808A,0x8000000080008000,0x808B]
CERT=_hca_public_path_text('__HCA_WORKSPACE__/research/tools/build_pkg/scratch/pkgR5L/pkg/sha3-256-r5/certificates/')
def init(msg):
    b=bytearray(200); b[:len(msg)]=msg; b[len(msg)]^=0x06; b[135]^=0x80
    return [int.from_bytes(b[8*i:8*i+8],"little") for i in range(25)]
def rnd(A,r):
    B=L(A); o=[0]*25
    for y in range(5):
        for z in range(64):
            pass
    # chi per row
    for y in range(5):
        for x in range(5):
            o[x+5*y]=B[x+5*y]^((~B[(x+1)%5+5*y])&M&B[(x+2)%5+5*y])
    o[0]^=RC[r]; return o
def states(msg):
    A=init(msg); S=[A]
    for r in range(5): A=rnd(A,r); S.append(A)
    return S   # S[r] = input to round r ; S[5] = output
def xor(a,b): return [p^q for p,q in zip(a,b)]
def par_cols(A):
    # C[x] lane parity; nonzero columns = bits of C
    C=[A[x]^A[x+5]^A[x+10]^A[x+15]^A[x+20] for x in range(5)]
    return sum(bin(c).count("1") for c in C)
def wt(A): return sum(bin(a).count("1") for a in A)
def nrows(A): return len(rows(A))
def flip(A,bit): B=list(A); B[bit//64]^=1<<(bit%64); return B
def lane_bit(x,y,z): return (x+5*y)*64+z
def reach(Bd, Aout):
    """chi row-wise: input difference Bd, required output difference Aout (exact). True if every row has DDT>0"""
    rb=rows(Bd); ra=rows(Aout)
    for k in set(rb)|set(ra):
        if DDT[rb.get(k,0)][ra.get(k,0)]==0: return False
    return True
def digest_ok(B4):
    for (y,z),d in rows(B4).items():
        if y==0 and not (DDT[d][0] or DDT[d][16]): return False
    return True
res={"pairs":[],"scan":{}}
names=sorted(set(f.rsplit("-",1)[0] for f in glob.glob(CERT+"*-a.bin")))
D={}
for n in names:
    a=open(n+"-a.bin","rb").read(); b=open(n+"-b.bin","rb").read()
    Sa,Sb=states(a),states(b)
    dig=[Sa[5][i]==Sb[5][i] for i in range(4)]
    alpha=[xor(Sa[r],Sb[r]) for r in range(5)]
    D[os.path.basename(n)]=(alpha,all(dig),len(a),len(b))
    print(os.path.basename(n),"len",len(a),len(b),"digest lanes0-3 equal",all(dig),"digest hex",b"".join(x.to_bytes(8,"little") for x in Sa[5][:4]).hex()[:16])

BETA2=[0x1,0,0x4,0,0,0x4,0x4,0x4,0x20000,0,0x2000000000000000,0,0x200000,0,0,0x2000000000000000,0,0,0x20000,0,0x200001,0,0x200000,0,0x1]
al3=frombits([0,130,450,529,701,789,1021,1169,1280,1429])
out={"certs":len(D)}
chk=[]
for n,(al,ok,_,_) in D.items():
    chk.append((n,ok,L(al[2])==BETA2,al[3]==al3, theta(al[3])==al[3]))
print("validation (digest eq, beta2==trail, alpha3==trail, alpha3 in kernel):")
for c in chk: print(c)
out["validation"]=chk
def stats(A):
    B=L(A)
    return {"wt_alpha":wt(A),"rows_alpha":nrows(A),"colparity_cols":par_cols(A),"in_kernel":theta(A)==A,"wt_beta":wt(B),"rows_beta":nrows(B)}
for r in (0,1,2,4):
    print("== round",r,"theta")
    per=[]
    for n,(al,ok,_,_) in D.items():
        per.append(stats(al[r]))
    kern=sum(p["in_kernel"] for p in per)
    print(" certs",len(per)," in kernel:",kern," colparity cols range",min(p["colparity_cols"] for p in per),max(p["colparity_cols"] for p in per),
      " rows alpha",min(p["rows_alpha"] for p in per),max(p["rows_alpha"] for p in per)," rows beta",min(p["rows_beta"] for p in per),max(p["rows_beta"] for p in per))
    out["round%d"%r]={"per_cert":per,"in_kernel":kern}
# alternatives, on the first cert (r5-v6-000038) and a second one
def alts(r, A, label):
    base=stats(A); B0=L(A)
    # single-bit flips (non-kernel), restricted: round0 only rate bits (<1088) since capacity must stay 0
    lim=1088 if r==0 else 1600
    sf=[];kp=0
    for b in range(lim):
        A2=flip(A,b); B2=L(A2)
        sf.append(nrows(B2))
    # same-column pairs (kernel-preserving): flips of two bits in the same column (x,z)
    pf=[]; pairs=0
    for x in range(5):
        for z in range(64):
            for y1 in range(5):
                for y2 in range(y1+1,5):
                    b1,b2=lane_bit(x,y1,z),lane_bit(x,y2,z)
                    if r==0 and (b1>=1088 or b2>=1088): continue
                    A2=flip(flip(A,b1),b2); pairs+=1
                    pf.append(nrows(L(A2)))
    d={"label":label,"base":base,"single_flips":len(sf),"single_rows_beta_min":min(sf),"single_rows_beta_mean":sum(sf)/len(sf),"single_rows_beta_max":max(sf),
       "pair_flips_kernel_preserving":len(pf),"pair_rows_beta_min":min(pf),"pair_rows_beta_mean":sum(pf)/len(pf),"pair_rows_beta_max":max(pf)}
    # downstream reachability
    if r==1:
        tgt=D[label][0][2]   # alpha2 exact (chi output of round 1)
        d["single_reach_alpha2"]=sum(reach(L(flip(A,b)),tgt) for b in range(1600))
        d["pair_reach_alpha2"]=0; d["pair_reach_alpha2_of"]=pairs
        for x in range(5):
            for z in range(64):
                for y1 in range(5):
                    for y2 in range(y1+1,5):
                        A2=flip(flip(A,lane_bit(x,y1,z)),lane_bit(x,y2,z))
                        d["pair_reach_alpha2"]+=reach(L(A2),tgt)
        d["base_reach_alpha2"]=reach(B0,tgt)
    if r==2:
        tgt=al3
        d["base_reach_alpha3"]=reach(B0,tgt)
        d["single_reach_alpha3"]=sum(reach(L(flip(A,b)),tgt) for b in range(1600))
        c=0
        for x in range(5):
            for z in range(64):
                for y1 in range(5):
                    for y2 in range(y1+1,5):
                        A2=flip(flip(A,lane_bit(x,y1,z)),lane_bit(x,y2,z)); c+=reach(L(A2),tgt)
        d["pair_reach_alpha3"]=c; d["pair_reach_of"]=pairs
    if r==4:
        d["base_digest_ok"]=digest_ok(B0)
        d["single_digest_ok"]=sum(digest_ok(L(flip(A,b))) for b in range(1600))
        c=0
        for x in range(5):
            for z in range(64):
                for y1 in range(5):
                    for y2 in range(y1+1,5):
                        A2=flip(flip(A,lane_bit(x,y1,z)),lane_bit(x,y2,z)); c+=digest_ok(L(A2))
        d["pair_digest_ok"]=c; d["pair_of"]=pairs
    return d
out["alts"]={}
for n in list(D)[:3]:
    for r in (0,1,2,4):
        d=alts(r,D[n][0][r],n); out["alts"]["%s/r%d"%(n,r)]=d
        print(n,"r",r,json.dumps({k:v for k,v in d.items() if k!="base"}),"base",d["base"])
json.dump(out,open("theta_scan.json","w"),default=str,indent=1)
