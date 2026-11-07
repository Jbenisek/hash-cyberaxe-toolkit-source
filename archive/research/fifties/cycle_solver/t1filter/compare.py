'''Compare the t1filter solver output with the exhaustive reference (split_e3/solve: ALL roots g of the 21-equation
loop over 2^32 values).  For each reference root: rebuild the full outer point with the exact evaluator (ev.Design.run),
check all 79 relations, compute T1; the expected solver output is {roots with T1 in [1,2^W)}.
Also: planted roots, solver T1 vs evaluator T1, candidates and ops per proposal, optional compress2 verification of
returned roots.  usage: python compare.py <tag> <W> <outfile> [<outfile> ...]  [--verify]'''

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

import sys, json, math, collections
sys.dont_write_bytecode = True
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/fifties/split_e3'))
import ev
d = ev.Design(*ev.DESIGN)
args = [a for a in sys.argv[1:] if not a.startswith('--')]; verify = '--verify' in sys.argv
tag, W, outs = args[0], int(args[1]), args[2:]
inst = {i['id']: i for i in json.load(open('inst_%s.json' % tag))}
ref = {}
for line in open('ref_%s.txt' % tag):
    p = line.split(); ref[int(p[0])] = (int(p[1]), [int(x, 16) for x in p[2:]])
sol, stats, tot = collections.defaultdict(dict), {}, None
for fn in outs:
    for line in open(fn):
        p = line.split()
        if p[0] == 'R': sol[int(p[1])][int(p[2], 16)] = int(p[3])
        elif p[0] == 'S': stats[int(p[1])] = (int(p[2]), int(p[3]))
covered = set(stats)
exp_set, all_roots, bad_rel, t1s = set(), 0, 0, []
planted_ok = planted_n = 0; ctl_t1zero = 0
for pid in sorted(covered):
    c, rs = ref[pid]; assert c == len(rs) and c < 64
    it = inst[pid]
    for g in rs:
        start = dict(it['E3'], **it['B']); start[d.g] = g
        v, h = d.run(start)
        okrel = h and all(ev.holds(r, v) for r in ev.REL)
        bad_rel += not okrel; all_roots += 1; t1s.append(v['T1'])
        if 0 < v['T1'] < (1 << W): exp_set.add((pid, g, v['T1']))
    if it['planted']:
        planted_n += 1
        if it['T1_true'] == 0: ctl_t1zero += it['g_true'] in rs
        else: planted_ok += it['g_true'] in rs
got = {(pid, g, t) for pid, m in sol.items() for g, t in m.items()}
missing, extra = exp_set - got, got - exp_set
print('tag %s W=%d: proposals %d, reference roots (all T1) %d, relation failures %d' % (tag, W, len(covered), all_roots, bad_rel))
print('  expected roots with T1 in [1,2^%d): %d ; solver returned %d ; missing %d ; extra %d' % (W, len(exp_set), len(got), len(missing), len(extra)))
print('  planted (T1 in [1,2^19)) present in reference: %d ; planted returned by solver: %d ; T1=0 controls in reference: %d (solver must not return)'
      % (planted_ok, sum(1 for pid in covered if inst[pid]['planted'] and inst[pid]['T1_true'] and inst[pid]['g_true'] in sol.get(pid, {})), ctl_t1zero))
print('  T1=0 controls returned by solver (must be 0):', sum(1 for pid in covered if inst[pid]['planted'] and inst[pid]['T1_true'] == 0 and inst[pid]['g_true'] in sol.get(pid, {})))
nat = [x for x in exp_set if not inst[x[0]]['planted'] or inst[x[0]]['g_true'] != x[1]]
print('  non-planted expected roots in range: %d (uniform-T1 expectation %.2f)' % (len(nat), (all_roots - planted_n) * ((1 << W) - 1) / 2 ** 32))
if missing: print('  MISSING', sorted(missing)[:10])
if extra: print('  EXTRA', sorted(extra)[:10])
cand = [stats[p][0] for p in covered]; ops = [stats[p][1] for p in covered]
print('  candidates per proposal: mean 2^%.4f (=%.0f) min %d max %d (2^%d = %d)' % (math.log2(sum(cand) / len(cand)), sum(cand) / len(cand), min(cand), max(cand), W, 1 << W))
print('  counted ops per proposal (candidates*17 + 9 + 2 per search step): mean %.0f = 2^%.4f, max %d = 2^%.4f' % (
    sum(ops) / len(ops), math.log2(sum(ops) / len(ops)), max(ops), math.log2(max(ops))))
if verify:
    nv = nok = 0
    for pid, g, t in sorted(got):
        it = inst[pid]; start = dict(it['E3'], **it['B']); start[d.g] = g
        v, h = d.run(start)
        ok, info = ev.verify(v, it['E3'], ev.y14_of(v)); nv += 1; nok += bool(ok)
    print('  compress2 verification of returned roots: %d/%d pass' % (nok, nv))
