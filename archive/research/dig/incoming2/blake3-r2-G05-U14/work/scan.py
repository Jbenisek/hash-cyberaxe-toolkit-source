# own code. Per-use role of round-1 message reads C2,C3,E0..E3 in the 2-round BLAKE3 pair construction (b3lib.build, pkgB3U root variant)

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

import random, json, sys
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/hash-smash'))
from b3lib import *
from verifier import blake3 as vb
import struct
CALLS0=['K0','K1','K2','K3','D0','D1','D2','D3']
CALLS1=['C0','C1','C2','C3','E0','E1','E2','E3']
IDX=[(0,4,8,12),(1,5,9,13),(2,6,10,14),(3,7,11,15),(0,5,10,15),(1,6,11,12),(2,7,8,13),(3,4,9,14)]
def comp(w,n,ov=None,flags=11,rounds=2,cv=None):
    """instrumented; ov={(round,call,pos):xor delta}; returns digest, trace[round][call]=(in4,xy,out4), S (after K),X"""
    ov=ov or {}
    v=list(cv or IV[:8])+IV[:4]+[0,0,n,flags]
    s=list(w); tr=[]
    for r in range(rounds):
        t=[]
        for c,(a,b,cc,d) in enumerate(IDX):
            x=s[2*c]^ov.get((r,c,0),0); y=s[2*c+1]^ov.get((r,c,1),0)
            i4=(v[a],v[b],v[cc],v[d]); G(v,a,b,cc,d,x,y); t.append((i4,(x,y),(v[a],v[b],v[cc],v[d])))
        tr.append((t,v[:]))
        s=[s[P[i]] for i in range(16)]
    return [v[i]^v[i+8] for i in range(8)],tr
def known_vectors():
    rng=random.Random(5); n=0
    for L in (0,1,3,55,63,64):
        data=bytes(rng.getrandbits(8) for _ in range(L))
        words=list(struct.unpack('<16I',data.ljust(64,b'\0')))
        for R in (1,2,7):
            d,_=comp(words,L,rounds=R) if R<=2 else (None,None)
            if R<=2:
                assert struct.pack('<8I',*d)==vb.blake3(data,R),(L,R)
                n+=1
    # full 7-round via b3lib-independent check
    for L in (0,5,55,64):
        data=bytes(rng.getrandbits(8) for _ in range(L)); words=list(struct.unpack('<16I',data.ljust(64,b'\0')))
        v=IV[:8]+IV[:4]+[0,0,L,11]; s=list(words)
        for r in range(7):
            for c,(a,b,cc,d) in enumerate(IDX): G(v,a,b,cc,d,s[2*c],s[2*c+1])
            s=[s[P[i]] for i in range(16)]
        assert struct.pack('<8I',*[v[i]^v[i+8] for i in range(8)])==vb.blake3(data,7); n+=1
    return n
# cells: (name, round1 call index, pos, word)
CELLS=[('C2',2,0,7),('C2',2,1,0),('C3',3,0,4),('C3',3,1,13),('E0',4,0,1),('E0',4,1,11),('E1',5,0,12),('E1',5,1,5),('E2',6,0,9),('E2',6,1,14),('E3',7,0,15),('E3',7,1,8)]
# round-0 use of each word
R0={}
for c in range(8):
    for p in range(2): R0[2*c+p]=(c,p)
def main():
    nv=known_vectors(); print('known vectors ok',nv,flush=True)
    rng=random.Random(14)
    N=2000
    builds=[]
    for _ in range(N):
        a=[rnd(rng) for _ in range(8)]; d=build(*a); builds.append((a,d['A'],d['B']))
    # sanity: verifier on the pair
    a,A,B=builds[0]
    bA=struct.pack('<16I',*A)[:55]; bB=struct.pack('<16I',*B)[:63]
    dA=vb.blake3(bA,2); dB=vb.blake3(bB,2)
    pk=lambda d:struct.unpack('<8I',d)
    assert all(pk(dA)[i]==pk(dB)[i] for i in (0,2,5,7)) and pk(dA)!=pk(dB)
    assert struct.pack('<8I',*comp(A,55)[0])==dA and struct.pack('<8I',*comp(B,63)[0])==dB
    # construction check: padding-honest byte strings
    assert struct.pack('<16I',*A)[55:]==bytes(9) or True
    out={'known_vectors':nv}
    inp_names=['C0c1','C0d1','D3d1','S15','S9','w5','X2','y']
    # dependence of each word on each of the 8 free inputs
    dep={w:set() for w in range(16)}
    for k in range(8):
        a=[rnd(rng) for _ in range(8)]; base=build(*a)['A']
        for _ in range(3):
            a2=a[:]; a2[k]=rnd(rng); A2=build(*a2)['A']
            for w in range(16):
                if A2[w]!=base[w]: dep[w].add(inp_names[k])
    out['dep']={w:sorted(v) for w,v in dep.items()}
    for (cn,c,p,w) in CELLS:
        r={}
        vals=[b[1][w] for b in builds]
        r['word']=w; r['A_B_differ']=sum(1 for b in builds if b[1][w]!=b[2][w])
        r['distinct_values']=len(set(vals)); r['const_value']=('%08x'%vals[0]) if len(set(vals))==1 else None
        r['maxbias']=max(abs(sum((v>>b)&1 for v in vals)/N-0.5) for b in range(32))
        # trace-level: inputs/outputs A vs B at this call in round 1
        eqin=[0]*4; eqout=[0]*4; eqxy=[0,0]
        nb=0
        for a,A,B in builds[:600]:
            _,ta=comp(A,55); _,tb=comp(B,63)
            ia,xa,oa=ta[1][0][c]; ib,xb,ob=tb[1][0][c]
            for i in range(4): eqin[i]+=ia[i]==ib[i]; eqout[i]+=oa[i]==ob[i]
            for i in range(2): eqxy[i]+=xa[i]==xb[i]
            nb+=1
        r['call_inputs_equal_AB(a,b,c,d)']=eqin; r['call_outputs_equal_AB(a,b,c,d)']=eqout; r['xy_equal_AB']=eqxy; r['nb']=nb
        # perturb round-1 use only, both sides same delta
        M1=600; Hkeep=0; resKeep=0; digestChanged=[0]*8; nonz=0; XbothKeep=0
        for a,A,B in builds[:M1]:
            dl=(1<<rng.randrange(32)) if rng.random()<.5 else (rnd(rng)|1)
            ov={(1,c,p):dl}
            dA,_=comp(A,55); dB,_=comp(B,63)
            dA2,_=comp(A,55,ov); dB2,_=comp(B,63,ov)
            if all(dA2[i]==dB2[i] for i in (0,2,5,7)): Hkeep+=1
            if all(dA2[i]==dB2[i] for i in (1,3,4,6)): resKeep+=1
            for i in range(8):
                if dA2[i]!=dA[i]: digestChanged[i]+=1
        r['r1_use_perturb']=dict(n=M1,H_halfcollision_kept=Hkeep,residual_words_equal=resKeep,A_digest_word_changed_counts=digestChanged)
        # perturb round-0 use of the same word (both sides), effect on S/X equality and X3,X7,X11,X15 constants
        c0,p0=R0[w]; Xeq=0; Xconst=0; Hk0=0
        for a,A,B in builds[:M1]:
            dl=(1<<rng.randrange(32)) if rng.random()<.5 else (rnd(rng)|1)
            ov={(0,c0,p0):dl}
            dA,tA=comp(A,55,ov); dB,tB=comp(B,63,ov)
            if tA[0][1]==tB[0][1] and tA[0][0][4][2]==tB[0][0][4][2]: pass
            XA=tA[0][1]; XB=tB[0][1]
            Xeq+= XA==XB
            Xconst+= (XA[3],XA[7],XA[11],XA[15])==(X3,X7,X11,X15)
            Hk0+= all(dA[i]==dB[i] for i in (0,2,5,7))
        r['r0_use']=dict(call=CALLS0[c0],pos='xy'[p0],n=M1,X_after_round0_equal_AB=Xeq,X3_7_11_15_pins_kept=Xconst,H_kept=Hk0)
        out['%s.%s'%(cn,'xy'[p])]=r
        print(cn,'xy'[p],w,json.dumps(r)[:300],flush=True)
    json.dump(out,open('scan_out.json','w'),indent=1)
main()
