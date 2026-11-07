'''Counted-op tallies (one modular add/sub, XOR or rotation = 1 op) for the t1filter solver pieces, with the same
counting rule as split_e3/ev.py Design.cuda():
  - per proposal: the pre-part words that depend on K0.b1 and are needed for (S12, S1, X0, X5, K1.b1, K1.d1);
  - per root (after a hit): every remaining word (post part + loop words), to hand the E1 trial a full point;
  - the original loop (43) for reference.'''

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

import sys
sys.dont_write_bytecode = True
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/fifties/split_e3'))
import ev
M = ev.M
d = ev.Design(*ev.DESIGN)
def ops_of(r, u):
    if r[0] == 'add':
        terms = [w for w in r[1] if w != u]; const = (-r[2]) & M if r[1][u] == 1 else r[2] & M
        return len(terms) - (0 if const else 1)
    x = 1 if r[2] else 0; ru = None; n = 0
    for w, k in r[1]:
        if w == u: ru = k
        else: x += 1; n += 1 if k else 0
    return n + x - 1 + (1 if ru else 0)
need = {'S12', 'S1', 'X0', 'X5', 'K1.b1', 'K1.d1'}
par = {w: [x for x in ev.wset(ev.REL[i]) if x != w] for i, w in d.ord}
anc, st = set(), list(need)
while st:
    x = st.pop()
    if x in anc or x not in par: continue
    anc.add(x); st += par[x]
pre_k = [(i, w) for i, w in d.pre if 'K0.b1' in d.dep[w] and w in anc]
print('per-proposal pre words depending on K0.b1 and needed:', [w for _, w in pre_k])
print('  ops:', sum(ops_of(ev.REL[i], w) for i, w in pre_k))
pre_k_all = [(i, w) for i, w in d.pre if 'K0.b1' in d.dep[w]]
print('all pre words depending on K0.b1:', len(pre_k_all), 'ops', sum(ops_of(ev.REL[i], w) for i, w in pre_k_all))
d2 = ev.Design(('Y4', 'Y9', 'w8'), ('D2.b1', 'K3.d1', 'S15', 'X4', 'D3.a1', 'K0.b1'), 'C0.b1')
need2 = need | {'X9', 'S6'}
par2 = {w: [x for x in ev.wset(ev.REL[i]) if x != w] for i, w in d2.ord}
anc2, st = set(), list(need2)
while st:
    x = st.pop()
    if x in anc2 or x not in par2: continue
    anc2.add(x); st += par2[x]
pre2 = [(i, w) for i, w in d2.pre if ({'D3.a1', 'K0.b1'} & d2.dep[w]) and w in anc2]
print('LAYOUT 2 per-proposal pre words (depend on D3.a1 or K0.b1, needed):', len(pre2), [w for _, w in pre2])
print('  ops:', sum(ops_of(ev.REL[i], w) for i, w in pre2))
post = [(i, w) for i, w in d.ord if d.g in d.dep[w]]
print('words depending on g (loop + post):', len(post), 'ops', sum(ops_of(ev.REL[i], w) for i, w in post))
print('loop only:', len(d.loop), 'ops', sum(ops_of(ev.REL[i], w) for i, w in d.loop), '(cuda() count incl. check:', d.cuda()[2], ')')
