
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

import sys,json
sys.path.insert(0,_hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/orchard/impl'))
import poseidon_ref as pr
P=pr.P
def bits(v,n): return [(v>>(n-1-i))&1 for i in range(n)]
def mk(sbox=0,field=1,nb=255,t=3,rf=8,rp=56):
    st=bits(field,2)+bits(sbox,4)+bits(nb,12)+bits(t,12)+bits(rf,10)+bits(rp,10)+[1]*30
    assert len(st)==80
    return st
class G:
    def __init__(s,st,discard=160):
        s.s=list(st)
        for _ in range(discard): s.step()
    def step(s):
        S=s.s
        nb=S[62]^S[51]^S[38]^S[23]^S[13]^S[0]
        s.s=S[1:]+[nb]; return nb
    def bit(s):
        while True:
            a=s.step(); b=s.step()
            if a: return b
    def fe(s,nb=255,order='be'):
        rej=0
        while True:
            bs=[s.bit() for _ in range(nb)]
            if order=='le': bs=bs[::-1]
            v=int(''.join(map(str,bs)),2)
            if v<P: return v,rej
            rej+=1
def gen(order='be',discard=160):
    g=G(mk(),discard); rc=[];rej=0
    for r in range(64):
        row=[]
        for l in range(3):
            v,x=g.fe(order=order); row.append(v); rej+=x
        rc.append(row)
    xs=[];ys=[]
    for _ in range(3): xs.append(g.fe(order=order)[0])
    for _ in range(3): ys.append(g.fe(order=order)[0])
    return rc,xs,ys,rej
if __name__=='__main__':
    for order in ('be','le'):
        rc,xs,ys,rej=gen(order)
        m=sum(rc[r][l]==pr.RC[r][l] for r in range(64) for l in range(3))
        print(order,'RC matches',m,'/192 rejections',rej)
        M=[[pow((xs[i]+ys[j])%P,P-2,P) for j in range(3)] for i in range(3)]
        print(' MDS match', sum(M[i][j]==pr.MDS[i][j] for i in range(3) for j in range(3)),'/9')
        print(' first rc', hex(rc[0][0]))
