'''Subset of split_e3's own generator instances (gen.py seed 2: inst_2.json, reference roots roots_2.txt from the GPU
exhaustive solve) for the t1filter solver: every instance whose reference roots include one with T1 in [1,2^19), plus
random others, plus generating instances (root with T1 = 0, must not be returned).  Each instance is its own batch
(all six B words random per instance in gen.py), so the solver runs in stream mode (one 2^32 pass per instance).
Writes batch_i2.txt (layout-2 solver format), inst_i2.json and ref_i2.txt (copied reference lines) here.
usage: python mk_i2.py <n_random> <n_gen> <seed>'''

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

import sys, json, random
sys.dont_write_bytecode = True
SE = _hca_public_path_text('__HCA_WORKSPACE__/research/fifties/split_e3')
sys.path.insert(0, SE)
import ev
d0 = ev.Design(*ev.DESIGN)
BATCH_CONST = ('Y4', 'Y9', 'X4', 'X8', 'w6', 'S11', 'X13')
PROP_VARS = ('S12', 'S1', 'X0', 'X5', 'K1.b1', 'K1.d1', 'X9', 'S6')
nr, ng, seed = map(int, sys.argv[1:4])
inst = {i['id']: i for i in json.load(open(SE + r'\inst_2.json'))}
lines, roots = {}, {}
for line in open(SE + r'\roots_2.txt'):
    p = line.split(); pid = int(p[0]); lines[pid] = line; roots[pid] = [int(x, 16) for x in p[2:]]
inr = []
for pid, rs in roots.items():
    it = inst[pid]
    if it['gen']: continue
    for g in rs:
        v, h = d0.run(dict(it['E3'], **it['B'], **{d0.g: g}))
        if 0 < v['T1'] < (1 << 19): inr.append((pid, g, v['T1']))
print('reference roots with T1 in [1,2^19):', inr)
rnd = random.Random(seed)
inr_ids = sorted({p for p, _, _ in inr})
others = [p for p in roots if not inst[p]['gen'] and p not in inr_ids]
gens = [p for p in roots if inst[p]['gen']]
sel = sorted(inr_ids + rnd.sample(others, nr) + rnd.sample(gens, ng))
out = []
with open('batch_i2.txt', 'w', newline='\n') as f, open('ref_i2.txt', 'w', newline='\n') as fr:
    f.write('%d\n' % len(sel))
    for b, pid in enumerate(sel):
        it = inst[pid]; pv = d0.pre_values(dict(it['E3'], **it['B']))
        f.write('B %d 1 %s\n' % (b, ' '.join('%08x' % pv[w] for w in BATCH_CONST)))
        f.write('I %d %s\n' % (pid, ' '.join('%08x' % pv[w] for w in PROP_VARS)))
        fr.write(lines[pid])
        out.append({'id': pid, 'batch': b, 'kind': 'gen' if it['gen'] else 'rand', 'planted': it['gen'], 'E3': it['E3'],
                    'B': it['B'], 'g_true': it['g_true'], 'T1_true': 0 if it['gen'] else None})
json.dump(out, open('inst_i2.json', 'w'))
print('selected', len(sel), '(in-range-root instances %d, random %d, generating %d)' % (len(inr_ids), nr, ng))
