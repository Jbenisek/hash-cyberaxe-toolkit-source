#!/usr/bin/env python3
"""e3sat_time.py [REPS_MAIN] [REPS_REC] [CONFIGS]   (research/newpaths/untried/ctr_alg; research only)

Splits each solver's measured CPU time into (parse + set-up) and (solve = preprocessing + search) for the systems of
systems.json (written by e3sat.py).  For every formula F a config runs (F, and F plus blocking clauses for the plants'
enumeration runs), it times F and F_bot = F with a fresh variable v and the units (v), (-v) appended at the END: the
solver reads and stores all of F, then finds the formula inconsistent and stops without preprocessing or search.
    solve_cpu = median cpu(F) - median cpu(F_bot)     parse_cpu = median cpu(F_bot) - median cpu(trivial)
Runs are interleaved (F, F_bot, F, F_bot, ...) and print nothing but the status line (kissat -q -n, cadical -q -n,
cms --verb 0 --printsol 0), so formatting statistics does not enter the time.  CPU time = getrusage of the child.
Cycles = seconds x 4.7e9 (Ryzen 9 7900X); 1 word op per cycle.  One solver process at a time.
"""
import json, os, resource, statistics, subprocess, sys
from math import log2
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e3sat as X  # noqa: E402

TL = 300
CFG = {
    'kissat': ('cnf', ['kissat', f'--time={TL}', '--check=0', '-q', '-n']),
    'kissat-nc': ('cnf', ['kissat', f'--time={TL}', '--check=0', '--congruence=false', '-q', '-n']),
    'cadical': ('cnf', ['cadical', '-t', str(TL), '-q', '-n']),
    'cms': ('xnf', ['cryptominisat5', '--maxtime', str(TL), '--verb', '0']),   # '--printsol 0' is rejected by 5.11.21
}


def cpu_of(cmd, path):
    r0 = resource.getrusage(resource.RUSAGE_CHILDREN)
    out = subprocess.run(cmd + [path], capture_output=True, text=True).stdout
    r1 = resource.getrusage(resource.RUSAGE_CHILDREN)
    st = 'SAT' if 's SATISFIABLE' in out else 'UNSAT' if 's UNSATISFIABLE' in out else 'UNKNOWN'
    return (r1.ru_utime + r1.ru_stime) - (r0.ru_utime + r0.ru_stime), st


def l2(x): return log2(x) if x > 0 else float('-inf')


def main():
    reps_main = int(sys.argv[1]) if len(sys.argv) > 1 else 9
    reps_rec = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    if len(sys.argv) > 3:                                # optional: only these configs (comma list)
        for c in [c for c in CFG if c not in sys.argv[3].split(',')]:
            del CFG[c]
    suffix = '' if len(sys.argv) <= 3 else '_' + sys.argv[3].replace(',', '_')
    systems = json.load(open(os.path.join(HERE, 'systems.json')))
    tmp = {e: os.path.join(X.CNFDIR, f'_time.{e}') for e in ('cnf', 'xnf')}
    bot = {e: os.path.join(X.CNFDIR, f'_time_bot.{e}') for e in ('cnf', 'xnf')}
    triv = {e: os.path.join(X.CNFDIR, f'_time_triv.{e}') for e in ('cnf', 'xnf')}
    base = {}
    for c, (e, cmd) in CFG.items():
        with open(triv[e], 'w') as f:
            f.write('p cnf 1 1\n1 0\n')
        base[c] = statistics.median(cpu_of(cmd, triv[e])[0] for _ in range(21))
    print('trivial-formula CPU (s), no printing: ' + ', '.join(f'{c} {v:.5f}' for c, v in base.items()))
    res = []
    for sy in systems:
        reps = reps_main if sy['main'] else reps_rec
        row = dict(name=sy['name'], set=sy['set'], step=sy['step'], main=sy['main'])
        for xmode, e in ((False, 'cnf'), (True, 'xnf')):
            enc = X.build(sy['y'], sy['q'], sy['w8'], tuple(sy['tgt']), xmode)
            body, m, lits = enc.body()
            sols = sy['dfs']['sols']
            for c, (ee, cmd) in CFG.items():
                if ee != e: continue
                solve = parse = 0.0; stats_ok = True
                for nb in range(len(sols) + 1):             # the enumeration sequence: F, F + 1 block, ...
                    blk = ''.join(' '.join(str(-(i + 1)) if h >> i & 1 else str(i + 1) for i in range(32)) + ' 0\n'
                                  for h in sols[:nb])
                    with open(tmp[e], 'w') as f:
                        f.write(f'p cnf {enc.n} {m + nb}\n'); f.write(body); f.write(blk)
                    with open(bot[e], 'w') as f:
                        f.write(f'p cnf {enc.n + 1} {m + nb + 2}\n'); f.write(body); f.write(blk)
                        f.write(f'{enc.n + 1} 0\n{-(enc.n + 1)} 0\n')
                    tf, tb = [], []
                    for _ in range(reps):
                        t, st = cpu_of(cmd, tmp[e]); tf.append(t)
                        stats_ok &= st == ('SAT' if nb < len(sols) else 'UNSAT')
                        t, st = cpu_of(cmd, bot[e]); tb.append(t)
                        stats_ok &= st == 'UNSAT'
                    solve += statistics.median(tf) - statistics.median(tb)
                    parse += statistics.median(tb) - base[c]
                row[c] = dict(solve_cyc=solve * X.CLOCK, parse_cyc=parse * X.CLOCK, ok=stats_ok, lits=lits)
        res.append(row)
        if sy['main']:
            print(f"{sy['name']:18s} " + ' | '.join(
                f"{c} solve 2^{l2(row[c]['solve_cyc']):.2f} parse 2^{l2(row[c]['parse_cyc']):.2f}"
                f"{'' if row[c]['ok'] else ' STATUS?'}" for c in CFG), flush=True)
    for p in list(tmp.values()) + list(bot.values()) + list(triv.values()):
        if os.path.exists(p): os.remove(p)
    with open(os.path.join(HERE, f'time_split{suffix}.json'), 'w') as f:
        json.dump(dict(base=base, rows=res), f)
    # per passing step (record sets), means; negative medians differences are kept (noise), clipped only in log
    for tags in (('rec11',), ('rec7',), ('rec11', 'rec7')):
        st = {}
        for r in res:
            if r['set'] in tags:
                st.setdefault((r['set'], r['step']), []).append(r)
        print(f'\n{"+".join(tags)}: {len(st)} passing steps; per passing step (mean; median):')
        for c in CFG:
            sv = sorted(sum(x[c]['solve_cyc'] for x in s) for s in st.values())
            pv = sorted(sum(x[c]['parse_cyc'] for x in s) for s in st.values())
            lv = sorted(sum(x[c]['lits'] for x in s) for s in st.values())
            bad = sum(not x[c]['ok'] for s in st.values() for x in s)
            print(f'  {c:9s} solve 2^{l2(sum(sv) / len(sv)):.2f}; 2^{l2(sv[len(sv) // 2]):.2f} | parse+setup '
                  f'2^{l2(sum(pv) / len(pv)):.2f} | literals 2^{l2(sum(lv) / len(lv)):.2f} | status mismatches {bad}')


if __name__ == '__main__':
    main()
