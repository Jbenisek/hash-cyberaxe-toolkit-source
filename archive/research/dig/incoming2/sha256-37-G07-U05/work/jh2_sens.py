
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

import sys, importlib.util, io, contextlib, json
from fractions import Fraction as Fr
P=_hca_public_path_text('__HCA_WORKSPACE__/research/tools/build_pkg/scratch/pkgR37X2/pkg/sha256-r37/experiments/xtab.py')
sys.argv=['xtab.py']
spec=importlib.util.spec_from_file_location('xtab',P); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
def tl(**kw):
    buf=io.StringIO()
    with contextlib.redirect_stdout(buf):
        r=m.ledger(show=False,**kw)
    return r
r=tl()
print(type(r), (list(r)[:6] if isinstance(r,dict) else r))
base=r['time_log2_exact'] if 'time_log2_exact' in r else r['log2_T']
print('base',r['time_log2'],r['log2_T'])
known={ 'q3=-72.0129':(60.16846,dict(q3_log2=-72.0129)), 'q3=-72.5':(60.23041,dict(q3_log2=-72.5)), 'q3=-73':(60.31551,dict(q3_log2=-73)),
        'q3=-74.02':(60.57978,dict(q3_log2=-74.02)), 'AC=64':(64.01134,dict(ac_log2=64)), 'AC=56':(57.59403,dict(ac_log2=56)),
        'exq=1':(60.38458,dict(exq=Fr(1))), 'exq=2.40':(60.17365,dict(exq=Fr(240,100))), 'exq=pooled 402680/164011':(60.17000,dict(exq=Fr(402680,164011))),
        'safety1.00':(60.16957,dict(safety=Fr(1))), 'safety1.05':(60.18547,dict(safety=Fr(105,100)))}
ok=0
for k,(want,kw) in known.items():
    got=tl(**kw)['time_log2']; flag=abs(got-want)<1.5e-5; ok+=flag
    print('CONTROL %-28s proof %.5f ours %.5f %s'%(k,want,got,'MATCH' if flag else 'DIFF'))
print('controls matched',ok,'of',len(known))
# R4 numbers
for q in (-71.0,-71.5,-71.974,-72.04,-72.5,-73.0,-73.5,-74.0,-74.5,-75.0):
    print('q3_log2 %.3f  time %.5f'%(q,tl(q3_log2=q)['log2_T']))
b=tl()['log2_T']
import math
d=tl(q3_log2=-72.04-0.01)['log2_T']-b
print('slope bits of score per bit of q3 charge (0.01 bit step): %.5f'%(d/0.01))
# margins on shipped statement: measured kept-fibre ratio and cell factor
mp=tl(q3_log2=-71.974,exq=Fr(246455,100000))['log2_T']; print('measured pt (cell 2^-71.974, ratio 2.46455) %.5f  vs charged %.5f  slack bits %.5f'%(mp,b,b-mp))
# q3 shortfall that moves the 5th decimal (score rounding: time_log2 is ceil to 5 decimals)
import bisect
lo,hi=0.0,1.0
for _ in range(60):
    mid=(lo+hi)/2
    if tl(q3_log2=-72.04-mid)['time_log2']>tl()['time_log2']: hi=mid
    else: lo=mid
print('q3 bits of extra loss until time_log2 (5dp) rises: %.5f bit (%.5f raw), score now %s'%(hi,hi,tl()['time_log2']))
# organizer-text SFS statement: score does not depend on it
