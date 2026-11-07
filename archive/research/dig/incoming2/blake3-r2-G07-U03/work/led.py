
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

import sys, math
from fractions import Fraction as Fr
P=_hca_public_path_text('__HCA_WORKSPACE__/research/tools/build_pkg/scratch/pkgB3S/pkg/blake3-r2/experiments/frontline.py')
src=open(P).read(); NL=chr(10)
def N_for(**rep):
    s=src
    for a,b in rep.items():
        assert a in s,a; s=s.replace(a,b)
    s=NL.join(l for l in s.split(NL) if not l.startswith("assert _MC =="))
    ns={"__name__":"m"}; exec(compile(s,"fl","exec"),ns); return ns["N"],ns
N0,ns=N_for()
print("shipped N",N0,"time_log2",math.log2(N0/430))
def t(rep): N,_=N_for(**rep); return math.log2(N/430)
b=t({})
for g in (7164,7100,7000,7198,8000,12466):
    print("F",g,"%.6f"%t({"G_BUDGET = 7164 *":"G_BUDGET = %d *"%g}), "delta %.6f"%(t({"G_BUDGET = 7164 *":"G_BUDGET = %d *"%g})-b))
# per unit F
d=(t({"G_BUDGET = 7164 *":"G_BUDGET = 7165 *"})-b); print("bits per +1 F: %.3e  per 100 F: %.5f"%(d,d*100))
# credit factor sensitivity (101/100)
for num in ("1006","1003","1010","1020"):
    r=t({"101 * RUN_STEPS * U_U) // (100 << 48)":"%s * RUN_STEPS * U_U) // (1000 << 48)"%num}); print("credit factor",num,"%.6f"%r,"delta %.6f"%(r-b))
# negative control: charge U0 (old ledger) instead of U
U0n=727329595507749*2  # over 2^49 -> to 2^48 numerator
r=t({"U_U = 335060079487497":"U_U = %d"%U0n}); print("U0 charged (old): %.6f delta %.6f"%(r,r-b))
# 0.9734 worst-case-ratio form
u=Fr(335060079487497,2**48); u0=Fr(727329595507749,2**49)
print("u_U",float(u),"u0",float(u0),"ratio",float(u/u0))
pc=Fr(279070422111,2**50)
print("recount u0-410pc:",float(u0-410*pc), "exact equal:", u0-410*pc==u)
print("7506/7711",7506/7711)
print("credit change U vs U0 fraction",float(1-u/u0))
print("--- control fixed")
U0n=-(-727329595507749//2)
r=t({"U_U = 335060079487497":"U_U = %d"%U0n}); print("U0 (unconverted, 1.01 x) charged: %.6f delta %.6f"%(r,r-b))
Uo=-(-U0n*7506//7711)
r=t({"U_U = 335060079487497":"U_U = %d"%Uo}); print("old 7506/7711 x U0 charged: %.6f delta %.6f"%(r,r-b))
# bits per unit of u_U (relative 1%)
r=t({"U_U = 335060079487497":"U_U = %d"%(335060079487497*101//100)}); print("u_U +1%%: delta %.6f"%(r-b))
