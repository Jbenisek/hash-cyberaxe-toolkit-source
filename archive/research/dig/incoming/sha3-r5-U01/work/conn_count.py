"""Count connector conditions as the pkgR5L constructor uses them (r5.py _attempt, instrumented copy).
usage: conn_count.py k [nattempts]  -> label 'hashsmash sha3-256-r5 R7 run k'; bprime gives advice, then attempts with run_seed(label+'conn'+(c+1))
Counts: rank of ED/EM after each stage. Does not change the algorithm."""

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

import sys, json, time, importlib.util
SRC=_hca_public_path_text('__HCA_WORKSPACE__/research/tools/build_pkg/scratch/pkgR5L/pkg/sha3-256-r5/experiments/r5.py')
spec=importlib.util.spec_from_file_location("r5",SRC); r5=importlib.util.module_from_spec(spec); sys.modules["r5"]=r5; spec.loader.exec_module(r5)
from r5 import *
def rk(E): return len(E.piv)
def inst_attempt(st, coins, dmin=33, xor_cap=X_MAX):
    budget=[0,xor_cap]; out={}
    try: status,info=_inst(st,coins,dmin,budget,out)
    except CapExceeded: status,info="cap",None
    out["status"]=status
    if info: out["DF"]=info["DF"]
    return status,info,out
def _inst(st,coins,dmin,budget,out):
    rows_a1=st.a1rows; ref=st.ref; Linv=st.Linv
    ED=Ech(budget)
    for j in st.FIX:
        if ED.add(Linv[j])<0: return "dinc",None
    out["ED_F"]=rk(ED); out["nFIX"]=len(st.FIX)
    nz=0
    for (y,z) in ROWS:
        if rows_a1[(y,z)]==0:
            nz+=1
            for b in rowbits(y,z):
                if ED.add(1<<b)<0: return "dinc",None
    out["inactive_rows"]=nz; out["active_rows_alpha1"]=len(st.act); out["ED_after_zero"]=rk(ED)
    order=list(st.act); coins.perm(order); A2sel={}
    for (y,z) in order:
        o=rows_a1[(y,z)]; rb=rowbits(y,z); rv=getrow(ref,y,z); sel=None
        for k in (2,1,0):
            cands=list(AFFIN[o][k]); coins.perm(cands); cands=[W for W in cands if rv in W]
            for W in cands:
                mk=ED.mark(); good=True
                for f in row_forms(W,rb):
                    if ED.add(f)<0: good=False;break
                if good: sel=W;break
                ED.undo(mk)
            if sel is not None:break
        if sel is None: return "dinc",None
        A2sel[(y,z)]=sel
    out["ED_after_D2"]=rk(ED)
    EM=Ech(budget)
    for j in st.FIX:
        if EM.add(Linv[j]|(st.fixval[j]<<N))<0: return "minc",None
    out["EM_M1"]=rk(EM)
    beta0=0; Srow={}
    for (y,z) in order:
        o=rows_a1[(y,z)]; rb=rowbits(y,z); rv=getrow(ref,y,z)
        cands=list(A2sel[(y,z)]); coins.perm(cands)
        cands.sort(key=lambda d:-DDT[d][o]); cands.sort(key=lambda d:d!=rv)
        ok=False
        for d in cands:
            md,mm=ED.mark(),EM.mark(); good=True
            for x in range(5):
                if ED.add(1<<rb[x]|(((d>>x)&1)<<N))<0: good=False;break
            if good:
                for f in row_forms(VSET[(d,o)],rb):
                    if EM.add(f)<0: good=False;break
            if good:
                ok=True; Srow[(y,z)]=VSET[(d,o)]
                for x in range(5):
                    if (d>>x)&1: beta0|=1<<rb[x]
                break
            ED.undo(md);EM.undo(mm)
        if not ok: return "tda",None
    out["EM_M2"]=rk(EM); out["ED_final"]=rk(ED)
    aff={}; full=frozenset(range(32))
    for r in st.lin_rows:
        y,z=r; rb=rowbits(y,z); masks=tuple(sorted(st.rowmasks[r]))
        W,best=st.lin[(r,Srow.get(r,full))]
        if W is None:
            best=list(best); coins.perm(best)
            forms={Wo:row_forms(Wo,rb) for Wo in best}
            implied=[Wo for Wo in best if all(EM.reduce(f)==0 for f in forms[Wo])]
            if implied: W=implied[0]
            else:
                for Wo in best:
                    mk=EM.mark(); good=True
                    for f in forms[Wo]:
                        if EM.add(f)<0: good=False;break
                    if good: W=Wo;break
                    EM.undo(mk)
                if W is None: return "lin",None
        Ws=sorted(W); b=Ws[0]; ech=[]
        for w in Ws:
            v=w^b
            for (pp,ee) in ech:
                if (v>>pp)&1: v^=ee
            if v:
                pp=v.bit_length()-1
                ech=[(q,e^v if (e>>pp)&1 else e) for (q,e) in ech]; ech.append((pp,v))
        for m in masks:
            f=par(m&CHI5[b])<<N
            for (pp,e) in ech:
                if par(m&(CHI5[b^e]^CHI5[b])): f^=(1<<rb[pp])^(((b>>pp)&1)<<N)
            aff[(r,m)]=f
    out["EM_M3"]=rk(EM); out["lin_rows"]=len(st.lin_rows); out["n_row_masks"]=sum(len(st.rowmasks[r]) for r in st.lin_rows)
    for (parts,c) in st.condparts:
        f=c<<N
        for r,m in parts.items(): f^=aff[(r,m)]
        if EM.add(f)<0: return "cond",None
    out["n_conditions_M4"]=len(st.condparts); out["EM_M4"]=rk(EM)
    DF=N-EM.rank(); out["DF"]=DF
    if DF<dmin: return "lowdf",{"DF":DF}
    return "ok",{"EM":EM,"beta0":beta0,"DF":DF}
if __name__=="__main__":
    k=int(sys.argv[1]); na=int(sys.argv[2]) if len(sys.argv)>2 else 12
    label=("hashsmash sha3-256-r5 R7 run %d"%k).encode()
    t0=time.time()
    base,OB=Base(),own_bits(); print("base",time.time()-t0,flush=True)
    r=bprime(base,OB,label,B_BUDGET,None,0,CCAP,B_TRUE)
    print("bprime",time.time()-t0,None if r is None else r[2:],flush=True)
    beta1,b0,c,j,DF=r
    st=Setup(base,beta1,b0)
    recs=[]
    for i in range(na):
        status,info,out=inst_attempt(st,Coins(run_seed(label+b"conn"+(c+1).to_bytes(4,"little"),i)))
        out["attempt"]=i; recs.append(out); print(json.dumps(out),flush=True)
    json.dump({"k":k,"c":c,"j":j,"advice_DF":DF,"attempts":recs,"n_rows_alpha2":len(base.a2rows),"beta1":hex(beta1),"beta0_advice":hex(b0)},open("conn_k%d.json"%k,"w"))
    print("done",time.time()-t0)
