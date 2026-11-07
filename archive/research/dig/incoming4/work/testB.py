
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

import sys,time,ctypes,json
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
sys.path.insert(0,_hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/orchard/math'))
from attack import *
res={}
def zs(r,j,logn,a=123456789123456789):
    L=Line(j); n=1<<logn
    g=pow(5,(p-1)//n,p)  # need element of exact order n: use generator-power
    # find primitive n-th root: 5 is a nonresidue? derive generically
    for base in range(2,50):
        h=pow(base,(p-1)//n,p)
        if pow(h,n//2,p)!=1: break
    s=0; w=a
    t=time.time()
    for i in range(n):
        s=(s+L.F(w,r))%p; w=w*h%p
    f0=L.F(0,r)
    return dict(r=r,j=j,logn=logn,sum_minus_n_F0_is_zero=(s-n*f0)%p==0,secs=round(time.time()-t,1))
res['r0_n2^14']=zs(0,0,14)   # deg 5^6=15625 < 16384
res['r0_n2^13_control']=zs(0,0,13)  # 8192 < 15625: should fail
print(res); 
if len(sys.argv)>1:
    res['r1_n2^17']=zs(1,0,17); print(res['r1_n2^17'])
json.dump(res,open('testB.json','w'),indent=1)
