#!/usr/bin/env python3
"""collect.py: gather every saved real collision of the scaled-down end-to-end runs, re-hash both messages
independently, recover the search parameters, and write the input of feat8/feat10 (hits + null trials).
Research only. Reads (never writes) the run folders; writes only into this folder.

Sources:
  T5   astra-jobs/server_tasks_2026-10-06/task5_small_h8/out          (server task 5, two-level order, W 8 and 10)
  T5L  task5_small_h8/ref/{local_job2,local_job3,test_job}           (local runs; duplicates of T5 removed)
  CT   research/newpaths/counter/toy/out                            (counter toy, W 8: filed / ctrH / ctrAll)
  FL   research/proveout/small_filed_layout/out                     (filed layout with X14, W 8 and 10)
Outputs: hits.tsv, feat_in8.txt, feat_in10.txt
"""
import glob, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
T5 = os.path.join(WS, 'astra-jobs', 'server_tasks_2026-10-06', 'task5_small_h8')
CTD = os.path.join(WS, 'research', 'newpaths', 'counter', 'toy')
FLD = os.path.join(WS, 'research', 'proveout', 'small_filed_layout')
sys.path.insert(0, CTD)
from verify_tree import Toy  # independent Python tree hash (read-only import)

TOYS = {8: Toy(8, 2, (4, 3, 2, 1)), 10: Toy(10, 2, (5, 4, 3, 2))}
_zcv = {}


def zero_chunk_cv(T, c):
    key = (T.W, c)
    if key not in _zcv:
        _zcv[key] = T.compress(*T.chunk_output([0] * T.chunk, c))
    return _zcv[key]


def tree_hash(T, t, last):
    """hash of t all-zero chunks followed by the short message `last` (Toy.hash logic, prefix CVs cached)"""
    stack = []
    for c in range(t):
        cv = zero_chunk_cv(T, c)
        tot = c + 1
        while tot & 1 == 0:
            cv = T.compress(T.iv, stack.pop() + cv, 0, T.block, 4)
            tot >>= 1
        stack.append(cv)
    out = T.chunk_output(last, t)
    while stack:
        out = (T.iv, stack.pop() + T.compress(*out), 0, T.block, 4)
    cv, w, _, bl, fl = out
    return T.compress(cv, w, 0, bl, fl | 8)


def kvparse(line):
    f = line.split()
    d = {}
    i = 1
    while i < len(f) - 1:
        d.setdefault(f[i], f[i + 1])
        i += 2
    return f, d


def parse_runfile(fn, src):
    """yields hit dicts with the run's HEAD and RUN data attached"""
    head, runs, hits = None, {}, []
    for line in open(fn, encoding='utf-8', errors='replace'):
        if line.startswith('HEAD '):
            f = line.split()
            head = {k: f[f.index(k) + 1] for k in ('ncls', 'beta', 'nd') if k in f}
        elif line.startswith('RUN '):
            f = line.split()
            i = f.index('seed')
            run = int(f[f.index('run') + 1])
            runs[run] = dict(seed=[int(x, 16) for x in f[i + 1:i + 5]], nouter=int(f[f.index('nouter') + 1]),
                             trials=int(f[f.index('trials') + 1]), coll=int(f[f.index('coll') + 1]))
        elif line.startswith('HIT '):
            f = line.split()
            fa = f[:f.index('A')]          # keys only before the messages (digest tokens can look like keys)
            kv = dict(zip(fa[1::2], fa[2::2]))
            g = lambda k: kv[k]
            h = dict(src=src, W=int(g('W')), set=int(g('set')), run=int(g('run')), outer=int(g('outer')),
                     member=int(g('member')), y4=int(g('y4'), 16), A=f[f.index('A') + 1], B=f[f.index('B') + 1],
                     dig=[int(x, 16) for x in f[f.index('digest') + 1:f.index('digest') + 9]])
            h['ser'] = int(g('ser')) if 'ser' in kv else -1
            h['x2'] = int(g('x2'), 16) if 'x2' in kv else -1
            h['arr'] = g('arr') if 'arr' in kv else 'filed'
            h['d1'] = int(g('d1'), 16) if 'd1' in kv else -1
            h['t'] = int(g('t')) if 't' in kv else 0
            if src == 'FL':
                h['x14'] = int(g('x14'), 16); h['vc'] = int(g('vc'), 16); h['vd'] = int(g('vd'), 16)
            hits.append(h)
    for h in hits:
        r = runs.get(h['run'])
        if r is None:
            continue
        h.update(seed=r['seed'], nouter=r['nouter'])
        h['ncls'] = int(head['ncls']) if head and 'ncls' in head else 0
        if head and 'beta' in head:
            h['beta'] = int(head['beta'], 16)
            h['nd'] = int(head['nd'])
        tag = os.path.basename(fn).split('_')[0].replace('', '').replace('\r', '')
        if src == 'CT':
            h['arr'] = tag            # filed / ctrH / ctrAll
        yield h


def main():
    files = []
    files += [(f, 'T5') for f in sorted(glob.glob(os.path.join(T5, 'out', 'w*_set*.txt')))]
    for j in ('local_job2', 'local_job3', 'test_job'):
        files += [(f, 'T5L') for f in sorted(glob.glob(os.path.join(T5, 'ref', j, 'w*_set*.txt')))]
    files += [(f, 'CT') for f in sorted(glob.glob(os.path.join(CTD, 'out', '*.txt'))) if not f.endswith('progress.txt')]
    files += [(f, 'FL') for f in sorted(glob.glob(os.path.join(FLD, 'out', '*.txt')))
              if re.match(r'(w8_p|w10_p|x10_|cpu_rep_w8)', os.path.basename(f))]
    seen, allh, dup = set(), [], 0
    for fn, src in files:
        for h in parse_runfile(fn, src):
            key = (h['W'], h['t'], h['A'], h['B'])
            if key in seen:
                dup += 1
                continue
            seen.add(key)
            allh.append(h)
    # independent re-hash of both messages
    bad = 0
    for h in allh:
        T = TOYS[h['W']]
        A = [int(c) for c in h['A']]; B = [int(c) for c in h['B']]
        ha, hb = tree_hash(T, h['t'], A), tree_hash(T, h['t'], B)
        h['ok'] = int(ha == hb and ha == h['dig'] and A != B)
        bad += 1 - h['ok']
    with open(os.path.join(HERE, 'hits.tsv'), 'w') as o:
        cols = ['src', 'W', 'arr', 'set', 'ser', 'run', 'outer', 'x2', 'member', 'y4', 'd1', 't', 'nouter', 'ncls', 'ok']
        o.write('\t'.join(cols + ['seed', 'beta', 'A', 'B']) + '\n')
        for h in allh:
            o.write('\t'.join(str(h.get(c, '')) for c in cols) + '\t' + ' '.join(map(str, h['seed'])) + '\t' +
                    str(h.get('beta', -1)) + '\t' + h['A'] + '\t' + h['B'] + '\n')
    from collections import Counter
    c = Counter((h['src'], h['W'], h['arr']) for h in allh)
    for k in sorted(c):
        print('HITS', k, c[k])
    print(f'total {len(allh)} unique pairs, {dup} duplicates dropped, re-hash failures {bad}')
    # feat input: hits + nulls (T5, T5L, CT only: their construction is in feat.c)
    for W in (8, 10):
        with open(os.path.join(HERE, f'feat_in{W}.txt'), 'w') as o:
            for i, h in enumerate(allh):
                if h['W'] != W or h['src'] == 'FL':
                    continue
                mode = 1 if h['arr'] in ('ctrH', 'ctrAll') else 0
                s = ' '.join(map(str, h['seed']))
                nmid = h['nouter'] << W
                g = (h['outer'] << W) | h['x2']
                o.write(f"H h{i} {mode} {h['set']} {s} {g} {h['member']} {max(h['d1'], 0)}\n")
                beta = h.get('beta', 1 << W) if mode else (1 << W)
                if h['arr'] == 'ctrAll':
                    beta = 1 << W
                o.write(f"N n0_{i} {mode} {h['set']} {s} {nmid} {beta} 20 0 {1000003 * i + 17}\n")
                if W == 8:
                    o.write(f"N n1_{i} {mode} {h['set']} {s} {nmid} {beta} 20 1 {1000003 * i + 29}\n")


if __name__ == '__main__':
    main()
