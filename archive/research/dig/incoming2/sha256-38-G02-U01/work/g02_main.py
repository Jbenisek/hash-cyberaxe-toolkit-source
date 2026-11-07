
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

import sys, json, math, copy
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming2/sha256-38-G02-U01/work'))
from g02_ledger38 import ledger, Fr, RUNS, SR, NB
import os
p2base = json.load(open(os.path.join(RUNS, 'pre2.json')))
def S(o): return o['log2_T'] + max(0.0, o['memory_log2_bytes'] - 20)
def run(k, nbB=True, **kw):
    B = 1 << k
    if 'xiter' in kw and nbB: kw['xiter'] = Fr(kw['xiter'], B)
    return ledger(show=False, B=B, nbB=nbB, **kw)
def sweep(nbB=True, kmax=50, **kw):
    out = []
    for k in range(0, kmax + 1):
        o = run(k, nbB, **kw); out.append((k, S(o), o['log2_T'], o['memory_log2_bytes']))
    return out
def best(sw): return min(sw, key=lambda r: r[1])
R = {}
if __name__ != "__main__": raise SystemExit
# known answers
o0 = run(0, False); o19 = run(19)
R['ka'] = dict(k0_time=o0['time_log2'], k0_mem=o0['memory_log2_bytes'], k0_S=S(o0), k0_words=o0['words'], k19_time=o19['time_log2'], k19_mem=o19['memory_log2_bytes'], k19_S=S(o19), k19_bytes=o19['words']*32)
print('known answers', R['ka'])
# sweep, both pricings of the sentinel pass
sw_d = sweep(True); sw_s = sweep(False)
R['best_d126'] = best(sw_d); R['best_strict'] = best(sw_s)
print('D126-faithful best', best(sw_d)); print('strict (sentinel pass NB kept per group) best', best(sw_s))
print('strict k=0,19:', sw_s[0], sw_s[19])
# M1 bytes per object
for k in (0, 19):
    o = run(k, True if k else False)
    print('k', k, {n: w * 32 for n, w in o['memw'].items()}, 'total B', o['words'] * 32)
# nonempty expected
H = NB * (1 << 64); E = SR * 22 * (1 << 32); lam = E / H
print('lambda per header', lam, 'nonempty fraction', 1 - math.exp(-lam))
# ceilings: drop one object, time unchanged
for name in ('SENT', 'HDR', 'P6T', 'FIX'):
    for nb, lab in ((True, 'D126'), (False, 'strict')):
        sw = sweep(nb, drop=(name,))
        b = best(sw); base = best(sw_d if nb else sw_s)
        print('drop', name, lab, 'best', b[:2], 'vs base', base[:2], 'ceiling gain', base[1] - b[1], '| at k0', sw[0][1], 'vs', (sw_d if nb else sw_s)[0][1])
        R.setdefault('drop', {})[name + '_' + lab] = dict(best=b, base=base, k0=sw[0][1], base_k0=(sw_d if nb else sw_s)[0][1], k19=sw[19][1], base_k19=(sw_d if nb else sw_s)[19][1])
json.dump(R, open('g02_main_out.json', 'w'), default=str)
