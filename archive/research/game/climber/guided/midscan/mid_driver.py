#!/usr/bin/env python3
"""mid_driver.py : cv-FREE MID-band scan over release cells that have a verified pair (Keystone 10-28).

Generalizes skeleton_hyb38/skel3.py + run3.sh (proven setup; verified result
skeleton_hyb38/v3/FOUND_hyb38_A10_mid11-14_cvfree.txt) to EVERY MAP_DATA group=release cell whose
characteristic has a verified pair:
  - kepler_in/*WITNESS*.json  (hyb38, zh37, mns38, pin38b, llw39, nb2_wonly16, nb3_row20, pin39b<-pub39)
  - the published pub38 pair  (pin38; derived once from its own base_pin38.xml, cached wit_pin38.json)
Per cell (freed row, relscan/cells/<char>/rel_<char>_<piece>.xml): cv FREE (sfs), J=0 (no message words
pinned), MID = 4-row bands (lo..lo+3) stepped by 2 across the char (lo = 0,2,.. < R-3), the verified pair
EXCLUDED (cv + all 16 message words, both copies).
Each run: kissat under a 1200 CPU-s cap -> UNDECIDED (open, NEVER a wall). SAT -> decode the 'v' lines ONLY
(never the full kissat output) with kit/sha_cnf.py --decode -> kit/indep_verify.py must print INDEP VERIFIED
-> found/FOUND_<char>_<piece>_mid<lo>-<hi>_cvfree.txt. One line per run to RESULTS.tsv as it lands.
Restart-safe: runs already in RESULTS.tsv are skipped.

  --dry                                   enumerate + count every run, per-char breakdown, a sample command; no solve
  --jobs P                                run the whole scan, up to P concurrent kissat lanes (default 8)
  --one CHAR PIECE LO-HI [--mode real|ctl] [--cap S]   build+solve exactly one instance (dry run / positive control)
"""
import sys, os, re, json, time, glob, subprocess, threading
from collections import defaultdict, deque

HERE = os.path.dirname(os.path.abspath(__file__))
GUI = os.path.normpath(os.path.join(HERE, '..'))                       # .../guided
CLIMB = os.path.normpath(os.path.join(GUI, '..'))                     # .../climber
WS = os.path.normpath(os.path.join(CLIMB, '..', '..', '..'))         # workspace root (research/game/climber -> up 3)
KIT = os.path.join(GUI, 'kit')
ENC = os.path.join(KIT, 'sha_cnf.py')
IVER = os.path.join(KIT, 'indep_verify.py')
CELLS = os.path.join(GUI, 'relscan', 'cells')
MAP = os.path.join(CLIMB, 'MAP_DATA.jsonl')
WSRC = os.path.join(HERE, 'witness_src.json')
RESULTS = os.path.join(HERE, 'RESULTS.tsv')
FOUND = os.path.join(HERE, 'found')
CAP = 1200                                                            # CPU seconds per run (ulimit -t): UNDECIDED, not a wall

sys.path.insert(0, KIT)
import sha_cnf                                                        # only for sha_cnf.K (32-bit SHA-256 round constants)
MASK = 0xffffffff
R = lambda x, k: ((x >> k) | (x << (32 - k))) & MASK


def arg(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def traj(Wm, N):
    """full 32-bit SHA-256 trajectory from 16 message words Wm and chaining CV (a..d,e..h); returns A,E dicts."""
    Wx = list(Wm)
    s0 = lambda x: (R(x, 7) ^ R(x, 18) ^ (x >> 3)) & MASK
    s1 = lambda x: (R(x, 17) ^ R(x, 19) ^ (x >> 10)) & MASK
    for t in range(16, N):
        Wx.append((s1(Wx[t-2]) + Wx[t-7] + s0(Wx[t-15]) + Wx[t-16]) & MASK)
    A = {-1 - i: CVG[i] for i in range(4)}; E = {-1 - i: CVG[4 + i] for i in range(4)}
    for t in range(N):
        a, b, c, d = A[t-1], A[t-2], A[t-3], A[t-4]; e, f, g, h = E[t-1], E[t-2], E[t-3], E[t-4]
        T1 = (h + (R(e, 6) ^ R(e, 11) ^ R(e, 25)) + ((e & f) ^ (~e & g)) + sha_cnf.K[t] + Wx[t]) & MASK
        T2 = ((R(a, 2) ^ R(a, 13) ^ R(a, 22)) + ((a & b) ^ (a & c) ^ (b & c))) & MASK
        A[t] = (T1 + T2) & MASK; E[t] = (d + T1) & MASK
    return A, E


def encode(xml, cnf, mp):
    env = dict(os.environ, SIGNED='1')
    subprocess.run(['python3', ENC, xml, cnf, mp, 'sfs'], env=env, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def pin(bits, v): return [(l if (v >> i) & 1 else -l) for i, l in enumerate(bits)]


def build(xml, cnf, mp_path, M1, M2, CV, N, mid, mode):
    """encode the cell, then append J=0 (none) + MID-band pins + (mode real) the pair-exclusion clause. Mirrors skel3.py."""
    global CVG
    CVG = CV
    encode(xml, cnf, mp_path)
    mp = json.load(open(mp_path))
    U = []                                                            # J=0: no message words pinned
    if mid != '-':
        lo, hi = map(int, mid.split('-'))
        (A1, E1), (A2, E2) = traj(M1, N), traj(M2, N)
        for t in range(lo, hi + 1):
            U += pin(mp['A1all'][str(t)], A1[t]) + pin(mp['A2all'][str(t)], A2[t])
            U += pin(mp['E1all'][str(t)], E1[t]) + pin(mp['E2all'][str(t)], E2[t])
    extra = ['%d 0' % u for u in U]
    if mode == 'real':
        cl = []
        for i in range(4):
            for k in '12':
                cl += [-l for l in pin(mp['A' + k][str(-1 - i)], CV[i])] + [-l for l in pin(mp['E' + k][str(-1 - i)], CV[4 + i])]
        for w in range(16):
            cl += [-l for l in pin(mp['W1'][w], M1[w])] + [-l for l in pin(mp['W2'][w], M2[w])]
        extra.append(' '.join(map(str, cl)) + ' 0')
    L = open(cnf).read().split('\n', 1); h = L[0].split()
    with open(cnf, 'w') as f:
        f.write('p cnf %s %d\n' % (h[2], int(h[3]) + len(extra)))
        f.write(L[1].rstrip('\n') + '\n' + '\n'.join(extra) + '\n')


def kissat(cnf, cap):
    """kissat under an `ulimit -t cap` CPU cap; returns (verdict, wall_s, cpu_s, conflicts, model_v_lines|None)."""
    t0 = time.time()
    cmd = 'ulimit -t %d; exec nice -n 10 kissat %s' % (cap, cnf)
    p = subprocess.run(['bash', '-c', cmd], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    dt = time.time() - t0
    v = {10: 'SAT', 20: 'UNSAT'}.get(p.returncode, 'UNDECIDED')
    out = p.stdout.decode(errors='replace')
    nc = None; vlines = []
    for ln in out.splitlines():
        if ln.startswith('c conflicts:'):
            try: nc = int(ln.split()[2])
            except (IndexError, ValueError): pass
        elif ln.startswith('v '):
            vlines.append(ln[2:])                                    # 'v' lines ONLY (the model); never the full output
    return v, dt, nc, (' '.join(vlines) if v == 'SAT' else None)


def verify(mp_path, model, dst):
    """decode the 'v' lines only, gate on sha_cnf --decode, then kit/indep_verify.py; on INDEP VERIFIED write dst."""
    mf = mp_path + '.model'; open(mf, 'w').write(model + '\n')
    dec = subprocess.run(['python3', ENC, '--decode', mp_path, mf],
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode(errors='replace')
    try: os.remove(mf)
    except OSError: pass
    if not ('messages differ: True' in dec and 'outputs equal: True' in dec):
        return False
    chk = mp_path + '.chk'; open(chk, 'w').write(dec)
    iv = subprocess.run(['python3', IVER, mp_path, chk], stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT).stdout.decode(errors='replace')
    try: os.remove(chk)
    except OSError: pass
    if 'INDEP VERIFIED' not in iv:
        return False
    open(dst, 'w').write(dec + '\n' + iv)
    return True


# ---- witness resolution -------------------------------------------------------------------------
_wit_lock = threading.Lock()
_wit_cache = {}


def resolve(char):
    """return (M1,M2,CV) as int lists for a char. kepler WITNESS json, or derive+cache the published pin38 pair."""
    with _wit_lock:
        if char in _wit_cache:
            return _wit_cache[char]
        src = json.load(open(WSRC))[char]
        if src.startswith('PUBFILE:'):
            cache = os.path.join(HERE, 'wit_%s.json' % char)
            fail = cache + '.FAILED'                                  # one failed derive -> later runs BUILDFAIL fast (no re-solve)
            if os.path.exists(fail):
                raise RuntimeError(open(fail).read().strip())
            if not os.path.exists(cache):
                try:
                    derive_pub(char, src[len('PUBFILE:'):], cache)   # published pair: solve the char's own base once
                except Exception as e:
                    open(fail, 'w').write(str(e) + '\n'); raise
            d = json.load(open(cache))
        else:
            d = json.load(open(os.path.join(WS, src)))
        w = ([int(x, 16) for x in d['M1']], [int(x, 16) for x in d['M2']], [int(x, 16) for x in d['cv']])
        _wit_cache[char] = w
        return w


def derive_pub(char, pubfile, cache):
    """derive a concrete pair for a published char by solving its OWN base_<char>.xml (guaranteed cell-consistent),
    then decode; store {M1,M2,cv}. (pubfile = the published pair_file this char is pinned from; recorded for provenance.)"""
    base = os.path.join(CELLS, char, 'base_%s.xml' % char)
    cnf = '/dev/shm/midderive_%s.cnf' % char; mp = cnf[:-4] + '.map'
    encode(base, cnf, mp)
    v, dt, nc, model = kissat(cnf, CAP)
    if v != 'SAT' or not model:
        raise RuntimeError('pub derive %s: base solve %s (no pair)' % (char, v))
    mf = mp + '.model'; open(mf, 'w').write(model + '\n')
    dec = subprocess.run(['python3', ENC, '--decode', mp, mf], stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT).stdout.decode(errors='replace')
    M = {}; cv = {}; k = None
    for ln in dec.splitlines():
        m = re.match(r'M([12]): W=(.*)', ln)
        if m: k = m.group(1); M[k] = m.group(2).split(); continue
        m = re.match(r'\s+chain=(.*)', ln)
        if m and k: cv[k] = m.group(1).split()
    if 'messages differ: True' not in dec or 'outputs equal: True' not in dec:
        raise RuntimeError('pub derive %s: decode failed' % char)
    tmp = cache + '.tmp'
    json.dump({'char': char, 'source': 'solved base_%s.xml (published char from %s)' % (char, pubfile),
               'M1': M['1'], 'M2': M['2'], 'cv': cv['1']}, open(tmp, 'w'), indent=1)
    os.replace(tmp, cache)


# ---- enumeration --------------------------------------------------------------------------------
def bands(Rn): return [(lo, lo + 3) for lo in range(0, Rn - 3, 2)]


def runs():
    """every (char, piece, xml, R, lo, hi) run: release cells with a verified pair and an existing cell xml."""
    wsrc = json.load(open(WSRC))
    out = []
    for ln in open(MAP):
        c = json.loads(ln)
        if c.get('group') != 'release':
            continue
        ch = c.get('char')
        if ch not in wsrc:
            continue
        piece = c.get('piece'); Rn = c.get('R')
        xml = os.path.join(CELLS, ch, 'rel_%s_%s.xml' % (ch, piece))
        if not os.path.exists(xml):
            continue
        for lo, hi in bands(Rn):
            out.append((ch, piece, xml, Rn, lo, hi))
    return out


def key(ch, piece, lo, hi): return '%s|%s|%d-%d' % (ch, piece, lo, hi)


def done_keys():
    d = set()
    if os.path.exists(RESULTS):
        for ln in open(RESULTS):
            p = ln.rstrip('\n').split('\t')
            if len(p) >= 5 and not ln.startswith('#') and p[4] not in ('', 'BUILDFAIL'):
                d.add('%s|%s|%s' % (p[0], p[1], p[2].replace('mid=', '')))
    return d


# ---- one run ------------------------------------------------------------------------------------
_res_lock = threading.Lock()


def write_result(resfile, line):
    with _res_lock:
        with open(resfile, 'a') as f:
            f.write(line + '\n')


def run_one(ch, piece, xml, Rn, lo, hi, mode, cap, tag, resfile, founddir):
    cnf = '/dev/shm/mid_%s.cnf' % tag; mp = cnf[:-4] + '.map'
    mid = '%d-%d' % (lo, hi)
    try:
        M1, M2, CV = resolve(ch)
        build(xml, cnf, mp, M1, M2, CV, Rn, mid, mode)
    except Exception as e:
        write_result(resfile, '%s\t%s\tmid=%s\t%s\tBUILDFAIL\t0\t0\t\t%s' % (ch, piece, mid, mode, str(e).replace('\t', ' ')[:120]))
        return 'BUILDFAIL'
    v, dt, cpu_unused, model = kissat(cnf, cap)
    verdict, how = v, 'solve'
    if v == 'SAT':
        os.makedirs(founddir, exist_ok=True)
        dst = os.path.join(founddir, 'FOUND_%s_%s_mid%s_cvfree.txt' % (ch, piece, mid))
        if verify(mp, model, dst):
            verdict, how = 'FOUND', 'solve+indep_verified'
        else:
            verdict, how = 'SAT_NOVERIFY', 'solve+verify_failed'
    write_result(resfile, '%s\t%s\tmid=%s\t%s\t%s\t%.1f\t%s' % (ch, piece, mid, mode, verdict, dt, how))
    for ext in ('.cnf', '.map'):
        try: os.remove(cnf[:-4] + ext)
        except OSError: pass
    return verdict


# ---- modes --------------------------------------------------------------------------------------
def do_dry():
    rs = runs(); per = defaultdict(lambda: [set(), 0, 0])
    for ch, piece, xml, Rn, lo, hi in rs:
        per[ch][0].add(piece); per[ch][1] += 1; per[ch][2] = Rn
    print('# MID-band cv-free scan (group=release, verified-pair chars). DRY: no solve.')
    for ch in sorted(per):
        print('%-30s cells=%-3d R=%-3d bands=%-3d runs=%d' % (ch, len(per[ch][0]), per[ch][2], len(bands(per[ch][2])), per[ch][1]))
    print('TOTAL RUNS: %d  (chars=%d)' % (len(rs), len(per)))
    if rs:
        ch, piece, xml, Rn, lo, hi = rs[0]
        print('sample: python3 mid_driver.py --one %s %s %d-%d --mode real --cap %d' % (ch, piece, lo, hi, CAP))


def do_one():
    ch = arg('--one'); i = sys.argv.index('--one')
    piece, mid = sys.argv[i + 2], sys.argv[i + 3]
    lo, hi = map(int, mid.split('-'))
    mode = arg('--mode', 'real'); cap = int(arg('--cap', str(CAP)))
    Rn = None
    for ln in open(MAP):
        c = json.loads(ln)
        if c.get('group') == 'release' and c.get('char') == ch and c.get('piece') == piece:
            Rn = c.get('R'); break
    if Rn is None:
        Rn = json.load(open(os.path.join(HERE, 'wit_%s.json' % ch)))['R'] if os.path.exists(os.path.join(HERE, 'wit_%s.json' % ch)) else 38
    xml = os.path.join(CELLS, ch, 'rel_%s_%s.xml' % (ch, piece))
    probe = os.path.join(HERE, 'RESULTS_probe.tsv')                  # probe runs NEVER touch the real RESULTS.tsv
    t0 = time.time()
    v = run_one(ch, piece, xml, Rn, lo, hi, mode, cap, 'one_%d' % os.getpid(), probe, os.path.join(FOUND, 'probe'))
    print('%s %s mid=%s mode=%s cap=%ds -> %s  (%.0fs wall)' % (ch, piece, mid, mode, cap, v, time.time() - t0))


def do_scan():
    import concurrent.futures as cf
    P = int(arg('--jobs', '8'))
    rs = runs(); dk = done_keys()
    todo = [r for r in rs if key(r[0], r[1], r[4], r[5]) not in dk]
    first = [c for c in arg('--first', '').split(',') if c]   # owner 10-28: chars to run first (e.g. the 39 families)
    if first: todo.sort(key=lambda r: first.index(r[0]) if r[0] in first else len(first))
    if not os.path.exists(RESULTS):
        write_result(RESULTS, '# char\tpiece\tmid\tmode\tverdict\twall_s\thow  (cv-free MID scan, 1200 CPU-s cap)')
    print('# scan start %s  total %d  todo %d  lanes %d' % (time.strftime('%F %T'), len(rs), len(todo), P), flush=True)
    q = deque((r, n) for n, r in enumerate(todo))
    lock = threading.Lock()

    def worker(wid):
        while True:
            with lock:
                if not q: return
                (ch, piece, xml, Rn, lo, hi), n = q.popleft()
            run_one(ch, piece, xml, Rn, lo, hi, 'real', CAP, 'w%d' % wid, RESULTS, FOUND)
    with cf.ThreadPoolExecutor(max_workers=P) as ex:
        list(ex.map(worker, range(P)))
    print('# scan done %s' % time.strftime('%F %T'), flush=True)


if __name__ == '__main__':
    os.makedirs(FOUND, exist_ok=True)
    if '--dry' in sys.argv:
        do_dry()
    elif '--one' in sys.argv:
        do_one()
    else:
        do_scan()
