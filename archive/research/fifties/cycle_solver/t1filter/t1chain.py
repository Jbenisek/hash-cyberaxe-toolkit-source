'''For every k=1 design in split_e3/designs.pkl (counter 2, T1 free): rebuild it on the exact relation set (ev.py, outer
system, F = Y4,Y9,w8) and classify how T1 = K1.a1 ^ rol(K1.d1,16) depends on the loop variable g:
  - which of K1.a1 / K1.d1 depends on g;
  - whether the g-dependent one is reached from g by a CHAIN of one-input bijections (each relation on the path has
    exactly one g-dependent input besides its output, and that relation is an XOR/rot or +/- with g-free terms).
If such a chain exists, T1 in [1,2^19) is equivalent to g lying in an explicitly enumerable set of 2^19 values
(invert the chain on each allowed value), so the filter disappears by construction.
Also report loop length (ops per candidate) for the designs.'''

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

import sys, pickle, collections
sys.dont_write_bytecode = True
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/fifties/split_e3'))
import ev
rows = pickle.load(open(_hca_public_path_text('__HCA_WORKSPACE__/research/fifties/split_e3/designs.pkl'), 'rb'))
F = ('Y4', 'Y9', 'w8')
stats = collections.Counter(); good = []
for t1g, nl, g, B, cname, cwords, path, pre in rows:
    try:
        d = ev.Design(F, B, g)
    except AssertionError:
        stats['not_valid_on_outer'] += 1; continue
    stats['valid'] += 1
    ga = g in d.dep['K1.a1']; gd = g in d.dep['K1.d1']
    stats[('K1.a1 dep g', ga, 'K1.d1 dep g', gd)] += 1
    if ga and gd: continue
    tgt = 'K1.a1' if ga else 'K1.d1'
    # walk back from tgt to g: every step must have exactly one g-dependent input
    solved = {w: i for i, w in d.ord}
    w, chain, ok = tgt, [], True
    while w != g:
        i = solved[w]; r = ev.REL[i]
        ins = [x for x in ev.wset(r) if x != w and g in d.dep.get(x, set())]
        if len(ins) != 1: ok = False; break
        chain.append((w, ev.rels.show(r))); w = ins[0]
    _, _, ops = d.cuda()
    stats[('simple chain', ok)] += 1
    if ok: good.append((ops, g, B, tgt, chain))
print(dict(stats))
good.sort(key=lambda x: x[0])
for ops, g, B, tgt, chain in good[:10]:
    print('loop ops %d  g=%s B=%s  T1 word %s chain:' % (ops, g, B, tgt))
    for c in chain: print('     ', c)
