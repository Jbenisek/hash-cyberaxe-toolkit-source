
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

import sys, os, json, math
os.environ['G02FAST']='1'
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming2/sha256-38-G02-U01/work'))
from g02_lib import *
def bestk(nbB, kmax=50, **kw):
    return best(sweep(nbB, kmax, **kw))
print('base', bestk(True), bestk(False))
# a. count-in-header: no sentinels. +3 ops per NE unit (dec+bnz), prefix +2 per nonempty header
a = dict(nosent=True, xne=3, xprefix=2)
print('cnt-in-header D126', bestk(True, **a), ' strict', bestk(False, **a))
# b. packed 1-word entries: esz=1, unpack +2 per NE unit, +4 per W pass; fill +132 ops/(Y,var)
p2 = dict(p2base); p2['P6_FILL'] += 132
b = dict(esz=1, xne=2, xcw=4, p2=p2)
print('pack1 D126', bestk(True, **b), ' strict', bestk(False, **b))
c = dict(esz=1, nosent=True, xne=5, xcw=4, p2=p2, xprefix=2)
print('pack1+cnt D126', bestk(True, **c), ' strict', bestk(False, **c))
for k in (0,):
    print('pack1+cnt k0', S(run(k, False, **c)), 'cnt k0', S(run(0, False, **a)))
# scan-R (table-free, hold R_j and F7), B=1
scan_var = 21
sR = Fr(SR, NB) * scan_var
o = ledger(show=False, B=1, scan_ops=sR, drop=('tables',)); print('scanR (R+F7 held)', o['time_log2'], o['memory_log2_bytes'], S(o), 'mem B', o['words']*32)
# P5 stream: per lookup full P5 window of A0 j, drop R and F7 and tables, code 2^23 B
cand = 768 * (p2base['P5_SETUP'] + (1 << 29) * (p2base['P5_BODY_MAX'] + p2base['P5_LOOP']))
candmean = 768 * (p2base['P5_SETUP'] + (1 << 29) * (33.69 + 3))
for lab, cc in (('ledger max body 58', cand), ('measured mean body 33.69', candmean)):
    for code in (1 << 23, 1 << 20):
        sp = Fr(cc) + Fr(SR, NB) * scan_var
        sp = Fr(sp).limit_denominator(10**6)
        o = ledger(show=False, B=1, scan_ops=sp, drop=('tables', 'R', 'F7'), code_B=code)
        print('P5 stream', lab, 'code', code, 'time', o['time_log2'], 'memB', o['words']*32, 'log2', o['memory_log2_bytes'], 'S', S(o))
# F7 computed inline instead of held, on the scanR line: cost 25 ops per entry visited (NE/3 per group)
o = ledger(show=False, B=1, scan_ops=sR, drop=('tables','F7'), xne=Fr(25,3)); print('scanR + F7 inline', o['time_log2'], o['memory_log2_bytes'], S(o))
# F7 inline on table line at k=19
print('table k19 F7 inline', S(run(19, True, drop=('F7',), xne=Fr(25,3))), 'vs', S(run(19)))
# R_j streamed on the table line (2 extra P5 passes, P5_enum x3 total instead of x1)
