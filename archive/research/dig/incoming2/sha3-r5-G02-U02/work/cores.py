
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

import sys, time, math, json, importlib.util
SRC=_hca_public_path_text('__HCA_WORKSPACE__/research/tools/build_pkg/scratch/pkgR5M/pkg/sha3-256-r5/experiments/r5.py')
spec=importlib.util.spec_from_file_location("r5",SRC); R=importlib.util.module_from_spec(spec); sys.modules["r5"]=R; spec.loader.exec_module(R)
sys.setrecursionlimit(10000)
t0=time.time(); reach=set(); nodes=0
for lane in range(25):
    n,f=R.lane_dfs(lane); nodes+=n; reach|=f
    assert n==R.LANE_NODES[lane]
    print("lane",lane,n,len(f),round(time.time()-t0,1),flush=True)
print("T1 nodes",nodes,"cores",len(reach),flush=True)
cores=sorted(reach)
kept=[c for c in cores if R.p45pos(c)]
print("kept",len(kept),round(time.time()-t0,1),flush=True)
ms=[[R.NIN[o] for _,o in R.rows_of(c)] for c in kept]
sc2=sum(math.prod(m) for m in ms)
hv=sum(min(math.prod(m[:k])+math.prod(m[k:]) for k in range(1,len(m))) for m in ms)
print("KNOWN ANSWER: kept",len(kept),"sum_c2",sc2,"hv",hv, "expect 467 1379275399350 48592224", flush=True)
ok = len(cores)==1741 and len(kept)==467 and sc2==1379275399350 and hv==48592224
# cores.bin exact size per export.py
per=[]
for c,m in zip(kept,ms):
    rows=R.rows_of(c)
    assert [R.NIN[o] for _,o in rows]==m   # ins[j] = d with DDT[d][o] => len = NIN[o]
    per.append(4 + sum(16 + 324*mj for mj in m))
binsize = 4 + sum(per) + 32 + 1024
mem = {
 "ok_known_answer": ok, "n_all_cores": len(cores), "n_kept": len(kept),
 "cores_bin_bytes": binsize, "per_core_bytes_max": max(per), "per_core_bytes_min": min(per), "per_core_bytes_mean": sum(per)/len(per),
 "sum_rows": sum(len(m) for m in ms), "sum_m": sum(sum(m) for m in ms),
 "bits_kept": sum(len(c) for c in kept), "bits_all": sum(len(c) for c in cores),
 "max_bits": max(len(c) for c in kept), "rows_hist": {str(k): sum(1 for m in ms if len(m)==k) for k in range(1,11)},
 "t1t2_seconds": round(time.time()-t0,1),
}
# per-core half table entries and max single core 2*9^5 check
mx=0
for m in ms:
    h=min(range(1,len(m)),key=lambda k:(math.prod(m[:k])+math.prod(m[k:]),k)); mx=max(mx,math.prod(m[:h])+math.prod(m[h:]))
mem["max_half_entries"]=mx
json.dump(mem,open("cores_stats.json","w"),indent=1)
print(json.dumps(mem,indent=1))
