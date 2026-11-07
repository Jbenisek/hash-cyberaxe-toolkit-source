
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

import sys, importlib.util
from math import log2
spec = importlib.util.spec_from_file_location("bs", _hca_public_path_text('__HCA_WORKSPACE__/research/blake3_r4/b4b/pkg/blake3/experiments/bsrho.py'))
bs = importlib.util.module_from_spec(spec); spec.loader.exec_module(bs)
bs.REGISTERS=800; bs.REGFILE=800*32
DPX=int(sys.argv[1]) if len(sys.argv)>1 else 30
for E in (26,22,18,16,12,10,9,8):
    bs.ENTRY=E
    p=bs.plan(256,None,None,800)
    lg=bs.ledger(p,None,800)
    tot=lg["total"]
    circ=bs.packed_circuit(bs.step256().qwords)[1]
    extra=0
    if E<18:   # lengths not stored: second pass
        extra=p["capr"]*(circ+bs.RECOVER_EXTRA+DPX)
    P=bs.loss(p)["P_lower"]
    print(E,"tmax",p["tmax"],"Tp",p["Tp"],"c",float(p["c"]),"base",round(log2(tot/bs.UNIT),5),"withrec2",round(log2((tot+extra)/bs.UNIT),5),"P",round(P,4),"rec frac",round(float(lg["parts"]["recovery"]/tot),4))
