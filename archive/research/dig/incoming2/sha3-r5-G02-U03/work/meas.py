
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

import sys, time, json, tracemalloc, gc
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/tools/build_pkg/scratch/pkgR5T/pkg/sha3-256-r5/experiments'))
import r5
from r5 import *
peak = {"ED":0,"EM":0,"sum":0}
live = []
class Ech2(r5.Ech):
    def __init__(s,budget=None):
        super().__init__(budget); live.append(s)
    def add(s,f):
        r = super().add(f)
        t = sum(e.rank() for e in live[-2:]) if len(live)>=2 else s.rank()
        if t>peak["sum"]: peak["sum"]=t
        return r
r5.Ech = Ech2
def rowbytes(E): # packed model: 1601-bit rows in 64-bit words (26 words = 208 B) + 2-byte pivot index
    return E.rank()*(26*8)
def pysize(E):
    return sys.getsizeof(E.piv)+sum(sys.getsizeof(v)+sys.getsizeof(k) for k,v in E.piv.items())+sys.getsizeof(E.log)
t0=time.time()
k = sorted(CHEAP)[0] if len(sys.argv)<2 else int(sys.argv[1])
lab = rlab(7,k)
base,OB = Base(), own_bits()
r = bprime(base,OB,lab)
print("bprime done",k,r[2:],"cost",WK.cost(),"t",round(time.time()-t0,1),flush=True)
st = Setup(base,r[0],r[1])
c = r[2]
out=[]; spaces=[]
tmax=float(sys.argv[2]) if len(sys.argv)>2 else 900
i=0
while len(spaces)<50 and time.time()-t0<tmax and i<1067:
    live.clear()
    co = Coins(run_seed(lab+b"conn"+(c+1).to_bytes(4,"little"), i))
    ta=time.time()
    status,info = attempt(st,co)
    rec={"i":i,"status":status,"xors":info["xors"],"draws":info["draws"],"sec":round(time.time()-ta,3)}
    if status=="ok":
        EM=info["EM"]
        rec.update(rank=EM.rank(),DF=info["DF"],em_packed=rowbytes(EM),em_py=pysize(EM),log=len(EM.log),peakranksum=peak["sum"])
        spaces.append(info)
    out.append(rec); i+=1
print("attempts",i,"accepted",len(spaces),"t",round(time.time()-t0,1),flush=True)
# held-50 python size
gc.collect()
tot_py=sum(pysize(s["EM"]) for s in spaces)
tot_pk=sum(rowbytes(s["EM"]) for s in spaces)
# tracemalloc on re-run of accepted + a cap attempt seeds
tm=[]
gc.collect()
for rec in [x for x in out if x["status"]=="ok"][:3]+[max(out,key=lambda x:x["xors"])]+[max([x for x in out if x["status"]!="ok"],key=lambda x:x["xors"])]:
    co = Coins(run_seed(lab+b"conn"+(c+1).to_bytes(4,"little"), rec["i"]))
    gc.collect(); tracemalloc.start(); tracemalloc.reset_peak()
    base0=tracemalloc.get_traced_memory()[0]
    live.clear(); peak["sum"]=0
    s2,i2=attempt(st,co)
    cur,pk=tracemalloc.get_traced_memory(); tracemalloc.stop()
    tm.append({"i":rec["i"],"status":s2,"xors":i2["xors"],"tm_peak_over_base":pk-base0,"tm_end_over_base":cur-base0,"peakranksum":peak["sum"]})
res={"label":lab.decode(),"k":k,"cand":r[2:],"bprime_cost_WK":WK.cost(),"attempts":out,"held_py_total":tot_py,"held_packed_total":tot_pk,"n_held":len(spaces),"tm":tm}
json.dump(res,open("meas_k%d.json"%k,"w"))
print("held50 py",tot_py,"packed",tot_pk)
print(json.dumps(tm,indent=0))
