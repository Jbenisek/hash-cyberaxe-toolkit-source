'''T1 = K1.a1 ^ rol16(K1.d1) with K1.d1 independent of the loop word, so 1 <= T1 < 2^19 fixes the top 13 bits of K1.a1.
(1) Which core words can be the single loop word (propagation from F + front B + that word alone)?
(2) For each valid cut: ops spent before K1.a1 is known (early abort on the 13-bit T1 test), and the resulting
    exhaustive price per usable E1 trial: 2^12.95 * 2^32 * (a + 1 + 2^-13 * rest)  [the +1 is the compare].
usage: python t1abort.py  (writes t1abort_out.txt)'''

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
sys.dont_write_bytecode = True
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/fifties/split_e3'))
import ev
F, B, g0 = ev.DESIGN
front = ev.Design(F, B, g0)
core = [g0] + [w for _, w in front.loop]
out = open('t1abort_out.txt', 'w')
def p(*a):
    print(*a); print(*a, file=out)
p('K1.d1 depends on the loop word:', g0 in front.dep['K1.d1'])
base = set(F) | set(B)
for gw in core:
    o, c, kn = ev.order(base | {gw})
    if not kn >= set(ev.WORDS):
        stuck = [ev.rels.show(r) for r in ev.REL if gw in ev.wset(r)]
        p('%-6s NOT a loop word (propagation stalls); its equations: %s' % (gw, stuck)); continue
    d = ev.Design(F, B, gw)
    lines, chk, ops = d.cuda()
    # ops up to and including the line that defines K1.a1 (or K1.a1 = g)
    acc = 0; a = None
    for k in range(len(d.loop)):
        sub = ev.Design.__new__(ev.Design); sub.__dict__.update(d.__dict__); sub.loop = d.loop[:k + 1]
        acc = sub.cuda()[2] - 0
        # cuda() adds the check's ops; remove them
        r = ev.REL[d.chk]
        chk_ops = len(r[1]) if r[0] == 'add' else len(r[1]) + sum(1 for _, kk in r[1] if kk)
        if d.loop[k][1] == 'K1.a1':
            a = acc - chk_ops; break
    if gw == 'K1.a1': a = 0
    rest = ops - a
    per = 2 ** 12.95 * 2 ** 32 * (a + 1 + rest * 2 ** -13)
    p('%-6s loop ops %d, ops before K1.a1 known %s, early-abort cost per usable trial 2^%.2f (score %.2f), plain 2^%.2f' %
      (gw, ops, a, math.log2(per), 42.98 + math.log2(per) - math.log2(430), math.log2(2 ** 12.95 * 2 ** 32 * ops)))
