
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

import sys,json,subprocess,hashlib,time
sys.path.insert(0,_hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/generic/pkg/experiments'))
sys.path.insert(0,'/root/hashsmash/yukon/pos_posr5m')
import rho
from verifier import poseidon as vp
for x in (0,5,12345,rho.P-1):
    assert vp.digest(rho.enc(x)+bytes(32),56)==rho.enc(rho.digest(x,0)), x
print("digest == organizer digest at r=56")
for eid,nb,mask in (("rho-n14",14,(1<<14)-1),("proj-w254",10,1023)):
    req={"schema_version":1,"experiment_id":eid,"target_profile":"x","event":{},"max_message_bytes":4096,
         "trials":[{"trial":i,"seed":hashlib.sha256(b"s%d"%i).hexdigest()} for i in range(256)]}
    t=time.time()
    out=subprocess.run(["python3",_hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/generic/pkg/experiments/rho.py')],input=json.dumps(req),capture_output=True,text=True).stdout
    dt=time.time()-t
    tr=json.loads(out)["trials"]; ok=0
    for r in tr:
        if r["message_a_hex"]:
            a=bytes.fromhex(r["message_a_hex"]); b=bytes.fromhex(r["message_b_hex"]); assert a!=b
            da=int.from_bytes(vp.digest(a,56),'little'); db=int.from_bytes(vp.digest(b,56),'little')
            assert (da^db)&mask==0; ok+=1
    print(eid,"pairs",ok,"of 256 all verified by organizer digest; %.1fs"%dt)
