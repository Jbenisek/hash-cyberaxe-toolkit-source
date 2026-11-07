#!/usr/bin/env python3
"""pf.py TARGET LANES CAP [dry] : pub39 pair factory + two-stage tail pick (Keystone order 10-28; builds and measures, never submits).
Factory job = (source pair, band s..s+3, s = 6..19) on pinladder/ladder.py's char (pub39, R=39, own char, cv and words free, sfs):
both copies' A/E on the band pinned to the source's values; one exclusion clause per known pair with the pub39 message difference
(KNOWN_FILES.txt list + tail_var replicas + found/). SAT -> 'v' lines -> kit/sha_cnf.py --decode + kit/indep_verify.py ->
found/FOUND_pf_NNN.txt; every new on-char pair becomes a source. Stage A: tail_var_gen_mid1028.py staging (CV=chain, MX, PIN=E17,E18)
+ 14 public seeds (work/req 01..14). Stage B: top 5 by stage-A mean_lin + shipped b16/db6c on 14 fresh seeds (work/req_pool 15..28),
ranked by stage B only. Streams RESULTS.tsv, TAILS_A.tsv, TAILS_B.tsv, PROGRESS.txt; START/DONE in research/luna/SYSTEMS_LEDGER.md."""
import sys, os, re, json, random, subprocess, threading, time, io, contextlib, shutil
from collections import deque
HERE = os.path.dirname(os.path.abspath(__file__)); G = os.path.dirname(HERE)
RES = os.path.normpath(os.path.join(G, '..', '..', '..'))
WORK = os.path.join(RES, 'pkg_r39_combined', 'work'); LEDGER = os.path.join(RES, 'luna', 'SYSTEMS_LEDGER.md'); KIT = os.path.join(G, 'kit')
sys.path.insert(0, os.path.join(G, 'pinladder')); sys.path.insert(0, KIT)
os.environ['SIGNED'] = '1'; os.environ['TAIL'] = 'own'
import ladder, char_pair_profile as cpp
M = 0xffffffff
TARGET, LANES, CAP = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]); DRY = len(sys.argv) > 4 and sys.argv[4] == 'dry'
FMAX = int(os.environ.get('FMAX', '2')); BANDS = list(range(6, 20)); NSEED = 14
REFS = {'b16': 'p_pin39b_mid40_ctl2_ctl_pub39_b16', 'db6c': 'db6c9b07fb'}
SHM = '/dev/shm/pairfactory'; TH = os.path.expanduser('~/r39comb/pf'); FOUND = os.path.join(HERE, 'found')
for d in (SHM, TH, FOUND): os.makedirs(d, exist_ok=True)
lock = threading.RLock(); rng = random.Random(1028)
def now(): return time.strftime('%Y-%m-%d %H:%M')
def ledger(msg):
    with open(LEDGER, 'a') as f: f.write(f'- {now()} | PC | pairfactory | {msg} | subagent pairfactory\n')
def tsv(name, head, row):
    p = os.path.join(HERE, name)
    with lock:
        new = not os.path.exists(p)
        with open(p, 'a') as f:
            if new: f.write('#' + '\t'.join(head) + '\n')
            f.write('\t'.join(map(str, row)) + '\n')

# ---- base char and CNF (built once; jobs add units + exclusion clauses only, so one map decodes every job)
BX = os.path.join(SHM, 'base'); ladder.mkchar('pub39', 39, BX + '.xml')
import sha_cnf
with contextlib.redirect_stdout(io.StringIO()): sha_cnf.encode(BX + '.xml', BX + '.cnf', BX + '.map', 'sfs')
MP = json.load(open(BX + '.map')); shutil.copy(BX + '.map', os.path.join(HERE, 'base.map')); shutil.copy(BX + '.xml', os.path.join(HERE, 'base.xml'))
_h, BODY = open(BX + '.cnf').read().split('\n', 1); NV, NC = int(_h.split()[2]), int(_h.split()[3]); BODY = BODY.rstrip('\n') + '\n'
assert not re.search(r'^x ', BODY, re.M)
CH = {int(m.group(1)): (m.group(2), m.group(3), m.group(4)) for m in
      re.finditer(r'^\s*(-?\d+)\s+A:\s*(\S+)\s+E:\s*(\S+)(?:\s+W:\s*(\S+))?', open(BX + '.xml').read(), re.M)}
def onchar(pr): return all(pr['rows']['A'][t] == CH[t][0] and pr['rows']['E'][t] == CH[t][1] and pr['rows']['W'][t] == CH[t][2] for t in range(39))
wcv, wm1, wm2, wpr = ladder.pair('pub39'); assert onchar(wpr), 'witness not on the base char'
DLP = [(b - a) & M for a, b in zip(wm1, wm2)]
def norm(cv, m1, m2):
    """copy-1 orientation of the char (M2 - M1 = pub39 DL); None if the message difference is not pub39's"""
    if len(cv) != 8 or len(m1) != 16 or len(m2) != 16: return None
    if [(b - a) & M for a, b in zip(m1, m2)] == DLP: return tuple(cv), tuple(m1), tuple(m2)
    if [(a - b) & M for a, b in zip(m1, m2)] == DLP: return tuple(cv), tuple(m2), tuple(m1)
    return None
def parse_txt(s):
    a = re.search(r'^M1: W=([0-9a-f ]+)', s, re.M); b = re.search(r'^M2: W=([0-9a-f ]+)', s, re.M); c = re.search(r'chain=([0-9a-f ]+)', s)
    if not (a and b and c): return None
    h = lambda g: [int(x, 16) for x in g.split()]
    return norm(h(c.group(1))[:8], h(a.group(1)), h(b.group(1)))
def parse_any(p):
    try:
        s = open(p, errors='replace').read()
        if p.endswith('.json'):
            w = json.loads(s); return norm(*[[int(x, 16) for x in w[k]] for k in ('cv', 'M1', 'M2')])
        if p.endswith('r39tail_free.py'):
            cv = [int(x, 16) for x in re.search(r'^CV=\[int\(x,16\)for x in "([0-9a-f ]+)"', s, re.M).group(1).split()]
            mx = [int(x, 16) for x in ''.join(re.search(r'^MX=\[int\(x,16\)for x in\(("[^)]+)\)', s, re.M).group(1).split('"')[1::2]).split()]
            dl = eval(re.search(r'^DL=(\[.*\])$', s, re.M).group(1)); return norm(cv, mx, [(x + d) & M for x, d in zip(mx, dl)])
        return parse_txt(s)
    except Exception: return None
def pin(bits, v): return [(l if (v >> i) & 1 else -l) for i, l in enumerate(bits)]
def excl(cv, m1, m2):
    cl = []
    for i in range(4):
        for k in '12':
            cl += [-l for l in pin(MP['A' + k][str(-1 - i)], cv[i])] + [-l for l in pin(MP['E' + k][str(-1 - i)], cv[4 + i])]
    for w in range(16): cl += [-l for l in pin(MP['W1'][w], m1[w])] + [-l for l in pin(MP['W2'][w], m2[w])]
    return ' '.join(map(str, cl)) + ' 0'
def bkey(pr, s): return (s,) + tuple(pr[k][t] for t in range(s, s + 4) for k in ('A1', 'A2', 'E1', 'E2'))

# ---- known pairs (exclusions) and sources (on-char pairs)
KNOWN = {}; EXCL = {}; SRC = {}; ORIGIN = {}
def add_known(p, origin):
    k = p[0] + p[1]
    if k in KNOWN: return None
    KNOWN[k] = p; EXCL[k] = excl(*p); ORIGIN[k] = origin; return k
files = [os.path.join(RES, l.strip().replace('\\', '/')) for l in open(os.path.join(HERE, 'KNOWN_FILES.txt')) if l.strip()]
files += sorted(os.path.join(WORK, 'tail_var', d, 'r39tail_free.py') for d in os.listdir(os.path.join(WORK, 'tail_var')) if not d.startswith('pf_'))
nprior = 0
for f in files:
    p = parse_any(f)
    if p and add_known(p, os.path.relpath(f, RES)):
        nprior += 1; pr = cpp.profile(list(p[0]), list(p[1]), list(p[2]), 39)
        if onchar(pr): SRC['k%03d' % len(SRC)] = (p, pr)
nsrc0 = len(SRC)
FOUNDS = sorted(f for f in os.listdir(FOUND) if f.startswith('FOUND_pf_'))
for f in FOUNDS:                                                   # resume: earlier factory pairs
    p = parse_txt(open(os.path.join(FOUND, f)).read()); k = add_known(p, 'pairfactory/found/' + f)
    if k:
        pr = cpp.profile(list(p[0]), list(p[1]), list(p[2]), 39)
        if onchar(pr): SRC[f[6:-4]] = (p, pr)
NFOUND = len(FOUNDS)
USED = set(); FQ0 = deque(); FQC = deque(); REP = []
jobs0 = [(sid, s) for s in BANDS for sid in SRC]; rng.shuffle(jobs0); FQ0.extend(jobs0)

# ---- tail staging (tail_var_gen_mid1028.py logic, self-tested against the shipped replica)
TSRC = open(os.path.join(WORK, 'tail', 'r39tail_free.py')).read()
DL = eval(re.search(r'^DL=(\[.*\])$', TSRC, re.M).group(1)); PIN0 = eval(re.search(r'^PIN=(\{.*\})$', TSRC, re.M).group(1))
CV0 = [int(x, 16) for x in re.search(r'^CV=\[int\(x,16\)for x in "([0-9a-f ]+)"', TSRC, re.M).group(1).split()]
MX0 = [int(x, 16) for x in ''.join(re.search(r'^MX=\[int\(x,16\)for x in\(("[^)]+)\)', TSRC, re.M).group(1).split('"')[1::2]).split()]
sys.path.insert(0, os.path.join(RES, 'pkg_r39_newchar', 'sha256', 'experiments'))
with contextlib.redirect_stdout(io.StringIO()): import r39joint as J
def pin_of(cv, mx): A, E, W = J.traj(list(cv), list(mx)); return E[20], E[21]
assert pin_of(CV0, MX0) == (PIN0[16], PIN0[17]), 'PIN rule self-test failed'
def stage_tail(sig, cv, m1, m2):
    dl = [(b - a) & M for a, b in zip(m1, m2)]
    if dl != DL and [(a - b) & M for a, b in zip(m1, m2)] == DL: m1, m2 = m2, m1; dl = DL
    if dl != DL: return False
    p16, p17 = pin_of(cv, m1); t = TSRC
    t = re.sub(r'^CV=\[int\(x,16\)for x in "[0-9a-f ]+"', 'CV=[int(x,16)for x in "%s"' % ' '.join('%08x' % v for v in cv), t, flags=re.M)
    t = re.sub(r'^MX=\[int\(x,16\)for x in\("[^)]+\)', 'MX=[int(x,16)for x in("%s "\n"%s")' % (' '.join('%08x' % v for v in m1[:8]), ' '.join('%08x' % v for v in m1[8:])), t, flags=re.M)
    t = re.sub(r'^PIN=\{.*\}$', 'PIN={16:0x%08x,17:0x%08x}' % (p16, p17), t, flags=re.M)
    d = os.path.join(WORK, 'tail_var', sig); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'r39tail_free.py'), 'w', newline='\n').write(t); shutil.copy(os.path.join(d, 'r39tail_free.py'), f'{TH}/r39tail_{sig}.py')
    return True
def outok(p):
    try: return os.path.getsize(p) > 0 and 'trials' in json.load(open(p))
    except Exception: return False
TQ = deque(); TLEFT = {}; STATA = {}; STATB = {}
def enqueue_tails(sig, odir, reqs, stage):
    os.makedirs(odir, exist_ok=True); n = 0
    for i, rq in enumerate(reqs, 1):
        if not outok(f'{odir}/out_{i:02d}.json'): TQ.append((sig, i, rq, odir, stage)); n += 1
    TLEFT[(sig, stage)] = n
    if n == 0: finish_sig(sig, odir, stage)
REQA = [os.path.join(WORK, 'req', 'r39-tail-%02d.json' % i) for i in range(1, 15)]
REQB = [os.path.join(WORK, 'req_pool', 'r39-tail-%02d.json' % i) for i in range(15, 29)]
def stats(odir):
    r = subprocess.run(['python3', os.path.join(WORK, 'tail_stats_dir.py'), odir], capture_output=True, text=True)
    m = re.search(r'mean_lin (\S+)\s+lcb99 (\S+)\s+lcb999 (\S+)', r.stdout)
    return (float(m.group(1)), float(m.group(3))) if m else None
def finish_sig(sig, odir, stage):
    st = stats(odir)
    with lock:
        (STATA if stage == 'A' else STATB)[sig] = st
        tsv('TAILS_%s.tsv' % stage, ['sig', 'mean_lin', 'lcb999', 'dir'], [sig, '%.4f' % st[0] if st else 'ERR', '%.4f' % st[1] if st else 'ERR', os.path.relpath(odir, RES)])

# ---- factory job
CNT = {'SAT': 0, 'UNSAT': 0, 'UNDECIDED': 0, 'NEW': 0, 'DUP': 0, 'OFFCHAR': 0, 'IVFAIL': 0, 'jobs': 0}
RUNF = 0; RUNT = 0; PHASE = 'A'; NJ = 0
def fjob(lane, sid, s, kind, nj):
    global NFOUND
    p, pr = SRC[sid]; b = f'{SHM}/lane{lane}'; U = []
    for t in range(s, s + 4):
        U += pin(MP['A1all'][str(t)], pr['A1'][t]) + pin(MP['A2all'][str(t)], pr['A2'][t])
        U += pin(MP['E1all'][str(t)], pr['E1'][t]) + pin(MP['E2all'][str(t)], pr['E2'][t])
    with lock: X = list(EXCL.values())
    with open(b + '.cnf', 'w') as f:
        f.write(f'p cnf {NV} {NC + len(U) + len(X)}\n'); f.write(BODY); f.write(''.join(f'{u} 0\n' for u in U)); f.write('\n'.join(X) + '\n')
    t0 = time.time()
    with open(b + '.out', 'w') as fo:
        pp = subprocess.Popen(['bash', '-c', f'ulimit -t {CAP}; exec nice -n 10 kissat -q {b}.cnf'], stdout=fo, stderr=subprocess.STDOUT)
        _, _, ru = os.wait4(pp.pid, 0); pp.returncode = 0
    wall, cpu = time.time() - t0, ru.ru_utime + ru.ru_stime
    out = open(b + '.out').read(); sl = re.search(r'^s (\S+)', out, re.M)
    v = {'SATISFIABLE': 'SAT', 'UNSATISFIABLE': 'UNSAT'}.get(sl.group(1) if sl else '', 'UNDECIDED'); res = '-'; iv = '-'
    if v == 'SAT':
        open(b + '.model', 'w').write('\n'.join(l[2:] for l in out.splitlines() if l.startswith('v ')) + '\n')
        chk = subprocess.run(['python3', os.path.join(KIT, 'sha_cnf.py'), '--decode', BX + '.map', b + '.model'], capture_output=True, text=True).stdout
        open(b + '.chk', 'w').write(chk)
        chk += subprocess.run(['python3', os.path.join(KIT, 'indep_verify.py'), BX + '.map', b + '.chk'], capture_output=True, text=True).stdout
        iv = 'INDEP_VERIFIED' if re.search(r'^INDEP VERIFIED', chk, re.M) else 'INDEP_FAIL'
        q = parse_txt(chk) if iv == 'INDEP_VERIFIED' else None
        if q is None: res = 'IVFAIL' if iv != 'INDEP_VERIFIED' else 'NODL'
        else:
            qpr = cpp.profile(list(q[0]), list(q[1]), list(q[2]), 39); oc = onchar(qpr)
            with lock:
                k = q[0] + q[1]
                if k in KNOWN: res = 'DUP'
                else:
                    NFOUND += 1; nid = 'pf_%03d' % NFOUND; fn = os.path.join(FOUND, f'FOUND_{nid}.txt')
                    open(fn, 'w').write(chk + f'# pairfactory {nid}: source {sid} band {s}-{s + 3} ({kind}), R=39 pub39 own char sfs; '
                                        f'cpu {cpu:.1f} s; on-char {oc}; {now()}\n')
                    add_known(q, 'pairfactory/found/' + os.path.basename(fn)); res = nid
                    if oc:
                        SRC[nid] = (q, qpr); ch = [(nid, s2) for s2 in BANDS if s2 != s]; rng.shuffle(ch); FQC.extend(ch)
                    REP.append((sid, s))
                    if stage_tail(nid, q[0], q[1], q[2]): enqueue_tails(nid, os.path.join(WORK, 'tail_var', nid), REQA, 'A')
                    else: res += '(tail-DL-skip)'
    with lock:
        CNT['jobs'] += 1; CNT[v] += 1
        if res.startswith('pf_'): CNT['NEW'] += 1
        elif res in CNT: CNT[res] += 1
    tsv('RESULTS.tsv', ['job', 'source', 'band', 'kind', 'verdict', 'wall_s', 'cpu_s', 'indep', 'result', 'excl'],
        [nj, sid, f'{s}-{s + 3}', kind, v, '%.0f' % wall, '%.1f' % cpu, iv, res, len(X)])

def tjob(sig, i, rq, odir, stage):
    t0 = time.time()
    with open(rq) as fi, open(f'{odir}/out_{i:02d}.json', 'w') as fo, open(f'{odir}/err_{i:02d}.txt', 'w') as fe:
        r = subprocess.run(['nice', '-n', '10', 'python3', '-B', f'{TH}/r39tail_{sig}.py'], stdin=fi, stdout=fo, stderr=fe, cwd=TH)
    with open(f'{odir}/times.txt', 'a') as f: f.write(f'{i:02d} rc={r.returncode} {time.time() - t0:.3f} s\n')
    with lock: TLEFT[(sig, stage)] -= 1; done = TLEFT[(sig, stage)] == 0
    if done: finish_sig(sig, odir, stage)

def factory_open():
    return NFOUND < TARGET
def next_fjob():
    """(sid, band, kind) with an unused pin key, children interleaved with first-generation jobs; repeats when both run dry"""
    while True:
        if not FQ0 and not FQC:
            if REP and RUNF == 0: FQC.extend((sid, s, 'rep') for sid, s in REP); REP.clear()
            else: return None
        q = FQC if FQC and (not FQ0 or rng.random() < 0.5) else FQ0
        j = q.popleft(); sid, s = j[0], j[1]; kind = j[2] if len(j) > 2 else ('child' if q is FQC else 'first')
        if kind == 'rep': return sid, s, kind
        key = bkey(SRC[sid][1], s)
        if key in USED: continue
        USED.add(key); return sid, s, kind

def progress():
    with lock:
        best = sorted(((v[0], k) for k, v in STATA.items() if v), reverse=True)[:5]
        txt = (f'{now()} phase {PHASE} | pairs new {NFOUND}/{TARGET} (prior known {nprior}, sources {len(SRC)}) | factory {CNT} running {RUNF} '
               f'queued {len(FQ0)}+{len(FQC)} | tails queued {len(TQ)} running {RUNT}, stage A done {len(STATA)}, stage B done {len(STATB)}\n'
               + ''.join(f'A {m:.4f} {k}\n' for m, k in best) + ''.join(f'B {v[0]:.4f} {k}\n' for k, v in sorted(STATB.items(), key=lambda x: -(x[1] or (-999,))[0])))
    open(os.path.join(HERE, 'PROGRESS.txt'), 'w').write(txt)

def start_B():
    global PHASE
    PHASE = 'B'; top = sorted(((v[0], k) for k, v in STATA.items() if v), reverse=True)[:5]
    for _, sig in top: enqueue_tails(sig, os.path.join(WORK, 'tail_varB', sig), REQB, 'B')
    for name, sig in REFS.items():
        shutil.copy(os.path.join(WORK, 'tail_var', sig, 'r39tail_free.py'), f'{TH}/r39tail_{sig}.py')
        enqueue_tails(sig, os.path.join(WORK, 'tail_varB', sig), REQB, 'B')
    ledger(f'stage A DONE: {len(STATA)} tails; stage B STARTED: top 5 {[k for _, k in top]} + shipped b16/db6c on fresh seeds req_pool 15..28')

def worker(lane):
    global RUNF, RUNT, NJ
    while True:
        job = None
        with lock:
            fo = factory_open() and PHASE == 'A'
            if fo and (RUNF < FMAX or not TQ):
                j = next_fjob()
                if j: RUNF += 1; NJ += 1; job = ('F', j + (NJ,))
            if job is None and TQ: RUNT += 1; job = ('T', TQ.popleft())
            if job is None:
                fdone = not fo or (not FQ0 and not FQC and not REP and RUNF == 0)
                if PHASE == 'A' and fdone and RUNF == 0 and RUNT == 0 and not TQ:
                    ledger(f'factory DONE: {NFOUND} pairs in found/ ({CNT})') if not getattr(worker, 'fdone', 0) else None; worker.fdone = 1
                    start_B()
                    continue
                if PHASE == 'B' and RUNT == 0 and not TQ: return
        if job is None: time.sleep(3); continue
        try:
            if job[0] == 'F': fjob(lane, *job[1])
            else: tjob(*job[1])
        except Exception as e:
            tsv('ERRORS.tsv', ['time', 'job', 'error'], [now(), repr(job[1])[:200], repr(e)[:300]])
        finally:
            with lock:
                if job[0] == 'F': RUNF -= 1
                else: RUNT -= 1
            progress()

if __name__ == '__main__':
    print(f'base char: NV {NV} NC {NC}; prior known pub39-DL pairs {nprior}, on-char sources {nsrc0}; found/ {NFOUND}; first-gen jobs {len(FQ0)}')
    if DRY: sys.exit(0)
    for f in FOUNDS:                                               # resume: stage A for earlier factory pairs not yet measured
        sig = f[6:-4]; d = os.path.join(WORK, 'tail_var', sig)
        if os.path.exists(os.path.join(d, 'r39tail_free.py')):
            shutil.copy(os.path.join(d, 'r39tail_free.py'), f'{TH}/r39tail_{sig}.py'); enqueue_tails(sig, d, REQA, 'A')
    ledger(f'STARTED: pub39 pair factory (target {TARGET} new pairs, bands 6..19, cap {CAP} CPU-s) + stage A (14 public seeds/pair) + stage B '
           f'(top 5 + b16/db6c on 14 fresh seeds); {LANES} lanes (factory <= {FMAX} while tails wait), nice 10; guided/pairfactory/PROGRESS.txt')
    T = [threading.Thread(target=worker, args=(i,)) for i in range(LANES)]
    for t in T: t.start()
    for t in T: t.join()
    progress()
    rk = sorted(((v[0], k) for k, v in STATB.items() if v), reverse=True)
    ledger(f'DONE: {NFOUND} new pairs; stage B ranking ' + ', '.join(f'{k} {m:.4f}' for m, k in rk) + ' (guided/pairfactory/TAILS_B.tsv)')
