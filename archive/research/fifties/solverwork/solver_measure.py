#!/usr/bin/env python3
"""solver_measure.py (fifties/solverwork; research only, local, nothing submitted).
Executed solver work versus its cap C(T) on REAL passing outer steps.
  Generator: prereg7 (pkg19/as_subset/prereg7): Philox4x32-10 words with the prereg7 MAIN seeds, h12.ctr_outer, the
  14-outcome automata, formula (V); T = H_Q & H_E & S(0x5f) & VMASK[v]. The GPU (passgpu, a copy of v7gpu.cu plus a
  filter mode) only lists the indices with T != 0; every listed step is recomputed here with the unchanged Python
  reference (run_prereg.eight_words, ref_fields) and the T must agree.
  Solver: the pkgBA16 halfsearch.py functions (unchanged, loaded as module BA): row_setup (guards (a)-(g), (G7), walks
  of bits 0..6), FORCED/DUAL/SELECTED arrays, fixed_arc, g15/g15_words, is_joint_root. trav() below is BA.traverse with
  one switch: g15=True deletes free position 15 and prescribes h15 by (G15) exactly as BA.path16 does at i == 15
  (CF 7.1/7.2, Sol CD 11.3). g15=False is BA.traverse itself (checked call by call against BA.traverse).
  Units: the cap ledgers with the ACTUAL node counts.
    C_G layout (G15):  1024 + 2304 F + 1408 rows + 20 forced + 48 free + 4 sel20 + 64 g15 + 80 leaf + 120 root
      cap C_G(T)    = 1024 + 2304 F + 3328 n_s + 5216 n_l
    old C7 layout (G7 only): 4096 + 2304 F + 1280 rows + 20 forced + 48 free + 4 sel20 + 80 leaf + 288 root
      cap C_old(T)  = 4096 + 2304 F + 6016 n_s + 10720 n_l
  Program-only extras (halfsearch node_units, not in the cap ledgers) are summed separately: walks 20, g25 9, g29 4,
  e29 1.
Modes: static | fncheck N | run PER_STREAM_LIMIT WORKERS"""
import sys, os, json, time, gzip, importlib.util
from collections import Counter
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(RES, 'pkg19', 'as_subset', 'prereg7'))
import run_prereg as RP                                   # noqa: E402  (imports sample -> h12 = pkg12b halfsearch)
sample = RP.sample
h12 = sample.h12
_spec = importlib.util.spec_from_file_location(
    'hs_ba16', os.path.join(RES, 'tools', 'build_pkg', 'scratch', 'pkgBA16', 'pkg', 'blake3-r2', 'experiments',
                            'halfsearch.py'))
BA = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(BA)
M = 0xFFFFFFFF
SEEDS = RP.MAIN_SEEDS
SMALL = {0x175020A0, 0x185020A0, 0x685020A0}
LARGE = {0x275020A0, 0x285020A0, 0x385020A0}
WALK = 'P'          # P: prereg7 generator as validated (pkg12b ctr_outer, CTR_FLAGS = 3); R: root-instance flags 11
PASSLIST = None
FQ = FE = T1 = T2 = None


def setup(walk='P'):
    global FQ, FE, T1, T2, WALK, PASSLIST
    WALK = walk
    PASSLIST = os.path.join(HERE, 'pass_list_%s.txt' % walk)
    if walk == 'R':
        h12.CTR_FLAGS = BA.FLAGS                        # 11: pkgBA16 step CO (checked name by name below)
    sample.configure()
    FQ, FE = h12.ctr_tables()
    BA.arrays()
    T1, T2 = BA.build_tables()


def cap_G(F, ns, nl):
    return 1024 + 2304 * F + 3328 * ns + 5216 * nl


def cap_old(F, ns, nl):
    return 4096 + 2304 * F + 6016 * ns + 10720 * nl


def new_cnt():
    return dict(forced=0, selected=0, free=0, leaves=0, roots=0, walk=0, g25=0, g29=0, e29=0, g15=0)


def trav(row, Q, y, E, Ep, kappa, e1, h, states, cnt, g15=False, w=None, static=False):
    'BA.traverse; g15=True: position 15 prescribed by (G15) as in BA.path16. static: every arc present (count check).'
    u = BA.bit(e1, 21)
    free = set(BA.free16(row)) if g15 else set(row.free_positions())
    if static:
        keys, pref0 = {i: 0 for i in range(7, 32)}, 0
    else:
        keys = {i: BA.descriptor(row, Q, y, E, Ep, kappa, i, 1, h[i]) if i in h else
                BA.descriptor(row, Q, y, E, Ep, kappa, i, 0, 0) for i in range(7, 32)}
        pref0 = sum(h[i] << i for i in range(7))
    roots = []
    stack = [(7, uu, aa, pref0, 0) for (uu, aa) in states]
    while stack:
        i, uu, aa, pref, e29 = stack.pop()
        if i == 32:
            cnt["leaves"] += 1
            if not static and BA.is_joint_root(Q, y, E, pref, row.tau):
                cnt["roots"] += 1
                roots.append(pref)
            continue
        cp = (uu << 1) | aa
        if g15 and i == 15:
            cnt["forced"] += 1
            cnt["g15"] += 1
            if static:
                arcs = [0x10]
            else:
                h15 = BA.g15(pref, w)
                arcs = [0 if h15 is None else BA.FORCED[((keys[15] | 8 | h15 << 2) << 2) | cp]]
        elif i in free:
            cnt["free"] += 1
            if static:
                arcs = [0x10, 0x12]
            else:
                wd = BA.DUAL[(keys[i] << 2) | cp]
                arcs = [wd & 0x1F, (wd >> 5) & 0x1F]
        elif static:
            cnt["forced"] += 1
            cnt["selected"] += i == 20
            cnt["g25"] += i == 25
            cnt["g29"] += i == 29
            arcs = [0x10]
        else:
            arcs = [BA.fixed_arc(i, keys[i], cp, pref, e29, u, cnt)]
        for arc in arcs:
            if arc:
                if i == 9:
                    cnt["e29"] += 1
                stack.append((i + 1, (arc >> 3) & 1, (arc >> 2) & 1, pref | (((arc >> 1) & 1) << i),
                              (arc & 1) if i == 9 else e29))
    return roots


def tree_units_G(c):
    return 20 * c["forced"] + 48 * c["free"] + 4 * c["selected"] + 64 * c["g15"] + 80 * c["leaves"] + 120 * c["roots"]


def tree_units_old(c):
    return 20 * c["forced"] + 48 * c["free"] + 4 * c["selected"] + 80 * c["leaves"] + 288 * c["roots"]


def extras(c):
    return 20 * c["walk"] + 9 * c["g25"] + 4 * c["g29"] + 1 * c["e29"]


def static_check():
    out = {}
    for t in sorted(SMALL | LARGE):
        row = BA.ROWS[t]
        for g in (False, True):
            c = new_cnt()
            trav(row, 0, 0, 0, 0, 0, 0, {}, [(0, 0)], c, g15=g, static=True)
            out['%08x %s' % (t, 'G15' if g else 'G7')] = dict(c, tree_cap=(tree_units_G(dict(c, roots=c["leaves"])) if g
                                                                         else tree_units_old(dict(c, roots=c["leaves"]))))
    fams = {'%08x' % t: str(BA.ROWS[t].family) for t in sorted(SMALL | LARGE)}
    return out, fams


def one(k, idx, Tv):
    'One listed outer step: recompute, check, run both trees on every row of T. Returns a result dict.'
    Tg, vg = Tv & 0xFFFF, (Tv >> 16) & 15
    e = RP.eight_words(SEEDS[k], idx)
    f, split_ok = RP.ref_fields(h12, FQ, FE, e)
    v = f[15]
    T = f[14] & f[13] & 0x5F & BA.VMASK[v]
    chk = Counter()
    chk['gpu_T_or_v_mismatch'] += (T != Tg) or (v != vg)
    chk['split_mismatch'] += not split_ok
    o = h12.ctr_outer(e)
    if WALK == 'R':
        vv = BA.scalar_outer(e[:7] + [BA.member_word(e[7] % BA.CLASS_SIZE)])
        chk['name_mismatch_vs_pkgBA16_scalar_outer'] += any(vv[n] != o[n] for n in o)
    else:
        vv = dict(o)
        vv['e1'] = (BA.Y3 + o['Y4']) & M
        vv['omega'] = (BA.Y3 + o['Y4'] + o['w8']) & M
    Q, y, E, e1, C, B = vv["Y9"], vv["Y4"], vv["omega"], vv["e1"], vv["C2.c1"], vv["C2.b1"]
    chk['nu_mismatch'] += BA.nu_of(Q, e1, C, B) != v
    X_ba = BA.look(T1, Q) & BA.look(T2, E)
    chk['pkg_filter_T_mismatch'] += (X_ba & BA.VMASK[v]) != T
    rows = [t for j, t in enumerate(BA.TAUS) if T >> j & 1 and t in BA.S_TAUS]
    F = len({BA.ROWS[t].family for t in rows})
    ns, nl = sum(t in SMALL for t in rows), sum(t in LARGE for t in rows)
    Ep = (E + BA.DY3) & M
    A, V = (vv["Y1"] + vv["w12"]) & M, vv["Y12"]
    tot7, tot15, ex7, ex15 = new_cnt(), new_cnt(), 0, 0
    per_row = []
    for t in rows:
        row = BA.ROWS[t]
        kappa = row.sigma ^ BA.EPS ^ E ^ Ep
        notes, cw = [], new_cnt()
        res = BA.row_setup(row, Q, y, E, Ep, e1, kappa, C, B, notes, cw)
        for n_ in notes:
            chk['note: ' + n_] += 1
        c7, c15 = dict(cw), dict(cw)
        r7 = r15 = []
        if res is not None:
            h, states = res
            chk['multi_state_rows'] += len(states) > 1
            r7 = trav(row, Q, y, E, Ep, kappa, e1, h, states, c7)
            cb = BA.new_count()
            rb = BA.traverse(row, Q, y, E, Ep, kappa, e1, h, states, cb)
            chk['trav_vs_BA_traverse_mismatch'] += (sorted(rb) != sorted(r7)) or any(cb[x] != c7[x] for x in cb
                                                                                      if x not in ('walk',))
            w = BA.g15_words(e1, C, B, A, V, h[6])
            r15 = trav(row, Q, y, E, Ep, kappa, e1, h, states, c15, g15=True, w=w)
            chk['g15_root_not_in_g7_roots'] += len(set(r15) - set(r7))
            chk['roots_g7'] += len(r7)
            chk['roots_g15'] += len(r15)
            chk['roots_removed_by_g15'] += len(set(r7) - set(r15))
        else:
            chk['rows_dropped_by_setup'] += 1
        chk['rows'] += 1
        for x in tot7:
            tot7[x] += c7[x]
            tot15[x] += c15[x]
        per_row.append((t, tree_units_G(c15), tree_units_old(c7)))
    exec_G = 1024 + 2304 * F + 1408 * len(rows) + tree_units_G(tot15)
    exec_old = 4096 + 2304 * F + 1280 * len(rows) + tree_units_old(tot7)
    return dict(T=T, F=F, ns=ns, nl=nl, capG=cap_G(F, ns, nl), capO=cap_old(F, ns, nl), exG=exec_G, exO=exec_old,
                xG=extras(tot15), xO=extras(tot7), rows=per_row, chk=chk,
                cnt15=tot15, cnt7=tot7)


def work(items):
    agg = dict(cells=Counter(), rowG=Counter(), rowO=Counter(), chk=Counter(), cnt15=Counter(), cnt7=Counter(),
               calls=0, sumG=0, sumO=0, sumxG=0, sumxO=0, sumcapG=0, sumcapO=0, overG=0, overO=0, maxG=0, maxO=0,
               ratio_hist=Counter())
    for k, idx, Tv in items:
        r = one(k, idx, Tv)
        agg['calls'] += 1
        agg['cells'][(r['T'], r['exG'], r['exO'])] += 1
        for t, uG, uO in r['rows']:
            agg['rowG'][(t, uG)] += 1
            agg['rowO'][(t, uO)] += 1
        agg['chk'].update(r['chk'])
        agg['cnt15'].update(r['cnt15'])
        agg['cnt7'].update(r['cnt7'])
        agg['sumG'] += r['exG']
        agg['sumO'] += r['exO']
        agg['sumxG'] += r['xG']
        agg['sumxO'] += r['xO']
        agg['sumcapG'] += r['capG']
        agg['sumcapO'] += r['capO']
        agg['overG'] += r['exG'] > r['capG']
        agg['overO'] += r['exO'] > r['capO']
        agg['maxG'] = max(agg['maxG'], r['exG'])
        agg['maxO'] = max(agg['maxO'], r['exO'])
        agg['ratio_hist'][int(20 * r['exG'] / r['capG'])] += 1
    return agg


def merge(a, b):
    for key, val in b.items():
        if isinstance(val, Counter):
            a[key].update(val)
        elif key in ('maxG', 'maxO'):
            a[key] = max(a[key], val)
        else:
            a[key] += val
    return a


def read_list(limit):
    by = {k: [] for k in range(8)}
    heads = {}
    for line in open(PASSLIST):
        if line.startswith('#'):
            p = line.split()
            heads[int(p[2])] = dict(steps=int(p[4]), found=int(p[6]), kept=int(p[8]))
            continue
        k, idx, tv = line.split()
        by[int(k)].append((int(idx), int(tv)))
    items = []
    for k in range(8):
        by[k].sort()
        items += [(k, i, tv) for i, tv in by[k][:limit]]
    return heads, by, items


def main():
    mode = sys.argv[1]
    setup(sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] in ('P', 'R') else 'P')
    if len(sys.argv) > 2 and sys.argv[2] in ('P', 'R'):
        del sys.argv[2]
    if mode == 'static':
        out, fams = static_check()
        print(json.dumps(dict(static=out, families=fams), indent=1))
        return
    if mode == 'fncheck':
        n = int(sys.argv[2])
        heads, by, _ = read_list(10 ** 9)
        got = []
        for i in range(n):
            e = RP.eight_words(SEEDS[0], i)
            f, _ = RP.ref_fields(h12, FQ, FE, e)
            T = f[14] & f[13] & 0x5F & BA.VMASK[f[15]]
            if T:
                got.append((i, T))
        gpu = [(i, tv & 0xFFFF) for i, tv in by[0] if i < n]
        print(json.dumps(dict(fncheck_indices=n, python_T_nonzero=len(got), gpu_listed=len(gpu), identical=got == gpu)))
        return
    if mode == 'run':
        limit, nw = int(sys.argv[2]), int(sys.argv[3])
        heads, by, items = read_list(limit)
        t0 = time.time()
        import multiprocessing as mp
        chunks = [items[j:j + 2000] for j in range(0, len(items), 2000)]
        agg = None
        with mp.get_context('fork').Pool(nw) as pool:
            for a in pool.imap_unordered(work, chunks):
                agg = a if agg is None else merge(agg, a)
        steps_scanned = {k: (heads[k]['steps'] if len(by[k]) <= limit else by[k][limit][0]) for k in range(8)}
        res = dict(heads=heads, limit=limit, steps_scanned=steps_scanned, seconds=round(time.time() - t0, 1),
                   calls=agg['calls'], sumG=agg['sumG'], sumO=agg['sumO'], sumxG=agg['sumxG'], sumxO=agg['sumxO'],
                   sumcapG=agg['sumcapG'], sumcapO=agg['sumcapO'], overG=agg['overG'], overO=agg['overO'],
                   maxG=agg['maxG'], maxO=agg['maxO'], chk=dict(agg['chk']), cnt15=dict(agg['cnt15']),
                   cnt7=dict(agg['cnt7']), ratio_hist={str(k): v for k, v in sorted(agg['ratio_hist'].items())},
                   cells=[[T, g, o, n] for (T, g, o), n in sorted(agg['cells'].items())],
                   rowG=[['%08x' % t, u, n] for (t, u), n in sorted(agg['rowG'].items())],
                   rowO=[['%08x' % t, u, n] for (t, u), n in sorted(agg['rowO'].items())])
        res['walk'] = WALK
        out = os.path.join(HERE, 'measure_%s_%d.json' % (WALK, limit))
        json.dump(res, open(out, 'w'))
        print('wrote', out, 'calls', agg['calls'], 'seconds', res['seconds'])
        print('mean exec G', agg['sumG'] / agg['calls'], 'mean cap G', agg['sumcapG'] / agg['calls'])
        print('chk', dict(agg['chk']))


if __name__ == '__main__':
    main()
