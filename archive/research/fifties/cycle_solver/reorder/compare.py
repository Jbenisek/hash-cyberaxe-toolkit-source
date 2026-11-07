'''Compare the CPU scan cut at C1.a1 (val_*.txt: "id n root:C0.b1 ...") with the GPU reference cut at C0.b1
(split_e3/roots_2.txt: "id n C0.b1 ..."), instance by instance, as SETS of full solutions (keyed by C0.b1).
Also rebuilds every CPU root through all 78 relations (ev.Design.run) from the instance's E3 and free words.
usage: python compare.py  (writes compare_out.txt)'''

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

import sys, json, glob, collections
sys.dont_write_bytecode = True
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/fifties/split_e3'))
import ev
SP = _hca_public_path_text('__HCA_WORKSPACE__/research/fifties/split_e3')
ref = {}
for l in open(SP + r'\roots_2.txt'):
    t = l.split(); ref[int(t[0])] = (int(t[1]), sorted(t[2:]))
inst = {x['id']: x for x in json.load(open(SP + r'\inst_2.json'))}
d = ev.Design(ev.DESIGN[0], ev.DESIGN[1], 'C1.a1')
n = same = 0; bad = []; nroots = 0; rebuilt = 0; hist = collections.Counter(); gen_ok = 0; gens = 0
for fn in sorted(glob.glob('val_*.txt')):
    for l in open(fn):
        t = l.split(); i = int(t[0]); c = int(t[1]); pairs = [x.split(':') for x in t[2:]]
        mine = sorted(b for _, b in pairs)
        n += 1; hist[c] += 1; nroots += c
        if (c, mine) == ref[i]: same += 1
        else: bad.append((i, (c, mine), ref[i]))
        x = inst[i]; start = dict(x['E3']); start.update(x['B'])
        for r, b in pairs:
            s = dict(start); s['C1.a1'] = int(r, 16)
            v, ok = d.run(s)
            rebuilt += ok and v['C0.b1'] == int(b, 16)
        if x['gen']:
            gens += 1; gen_ok += x['g_true'] is not None and ('%08x' % x['g_true']) in mine
out = open('compare_out.txt', 'w')
def p(*a):
    print(*a); print(*a, file=out)
p('instances compared', n, ' identical root sets', same, ' mismatches', len(bad))
p('roots', nroots, ' rebuilt and all 78 relations hold', rebuilt, ' root-count histogram', sorted(hist.items()))
p('generator instances', gens, ' generating C0.b1 among the roots', gen_ok)
for b in bad[:10]: p('MISMATCH', b)
