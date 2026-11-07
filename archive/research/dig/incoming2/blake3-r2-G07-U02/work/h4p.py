
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

import sys, math, json
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming2/blake3-r2-G07-U02/work'))
import ledger_ext as L
from math import log2
out = {}
# R2a: exact recount of S_old
s = 116*5*2**53 + 116*(2**51+2**10) + 2**50
out['S_old_recount'] = s; assert s == L.S_OLD == 5_486_510_246_044_225_536
out['S_old_log2'] = log2(s)
# bytes of advice record
rec = {'six constants':24,'eta':4,'beta*+mask+value':12,'beta2+mask+value':12,'tau,eps,eps2':12,'rows of S':3,'mask S':1}
out['record_bytes'] = sum(rec.values()); assert sum(rec.values())==68
# hex word counts: 6 words*4, 1 word, 3 words, 3 words, 3 words
assert 6*4==24 and 3*4==12
# R2b ledger recompute
for nm,c in (('BASE',L.BASE),('NEW',L.NEW)):
    r = L.ledger(c); out[nm+'_N']=r['N']; out[nm+'_log2']=log2(r['N']/430); out[nm+'_k']=L.certificate(r['N'])
N = out['NEW_N']
out['share_S_old'] = L.S_OLD/N
out['bits_per_1e18_of_S'] = log2((N+10**18)/N)
out['bits_per_pow2_of_cap'] = None
def with_S(sv):
    L.S_OLD = sv; r = L.ledger(L.NEW); return log2(r['N']/430)
base = with_S(5_486_510_246_044_225_536)
out['recomputed_new'] = base
# R3 controls: negative control: other S_old values must change the number
out['S_4.859e18'] = with_S(4_859_000_000_000_000_000) - base
out['S_4.76e18'] = with_S(4_760_000_000_000_000_000) - base
out['S_zero'] = with_S(0) - base
# alternative cap values for 116 runs: cap=2^54.3,2^54.6,2^55.0,2^55.14 (observed max 9010.5s*2^42)
def S_for(cap): return int(116*cap + 116*(2**51+2**10) + 2**50)
for lab,cap in (('cap2^54.3',2**54.3),('cap2^54.6',2**54.6),('cap2^55',2**55),('cap2^55.14',2**55.14),('obs9010.5s',9010.5*2**42)):
    out[lab] = with_S(S_for(cap)) - base
# only 51 runs (lengths 55/63)
out['51runs_5x2^53'] = with_S(51*5*2**53 + 51*(2**51+2**10)+2**50) - base
# step 2 cap 2^51 -> observed 320s*2^42
out['step2_320s'] = with_S(116*5*2**53 + 116*(320*2**42+2**10)+2**50) - base
out['step2_share'] = 116*(2**51+2**10)/s
out['pre_log2_units'] = log2(s/430)
out['4770s_run_ops_log2'] = log2(4770*2**42)
out['margin_cap_over_run'] = log2(5*2**53/(4770*2**42))
print(json.dumps(out,indent=1,default=str))
