#!/usr/bin/env python3
"""coverage.py - the coverage universe of the row dig and what is already scanned.

Reads (read only): CELLS.jsonl, SCHEMA.md conventions, the characteristics chi37.txt / chi38.txt, ATLAS37.md (full matrix),
atlas38_gen.py (its evidence table, evaluated up to the point where it would write files), the row cards, and a few result
files of our own trail lab that are named in the rules below.
Writes: UNIVERSE.jsonl, COVERAGE.md, UNITS.jsonl (next to this file). Re-runnable; never writes CELLS.jsonl.

Universe = (hash, location, object, question) cells.  Wave-1 cells carry group W1; the gap dimensions G02 (memory objects, M1-M4),
G04 (CV / first block / padding), G05 (BLAKE3 init / pins / output fold / mode / message reads / doors), G06 (SHA3 message, digest lanes,
condition groups, route ledger) and G07 (premises, op ledgers, judge causes) were added 2026-10-12 from UNIVERSE_GAPS.md sections 4-7 and 9
(G01 Poseidon, G03 characteristic family, G08, G09 are NOT here: they are owned elsewhere).
  sha256-37 / sha256-38 : rows -4..last, objects A, E, W and REL (the row's two-bit relations / plus links), questions Q1..Q4;
                          interaction cells (i,j), j-i in 1..4, and every schedule link W_j <- W_i, question Q5.
  sha3-r5 / sha3-r6     : rounds x {theta, rho, pi, chi, iota}, questions Q1..Q4.
  blake3-r2             : 16 G calls x 4 quarter-steps (the 64 steps of GRID_BLAKE3.md) and the 16 message words, Q1..Q4.

A cell is SCANNED when (a) it is structurally trivial (reason recorded), (b) a CELLS.jsonl record of ours (own_test=true,
status BEDROCK/COMPUTED/SAMPLED/LOCAL_ONLY/KILLED) answers that question for that location (ids recorded), or (c) a result file
of our own code that is not yet in CELLS.jsonl answers it (basis FILE: pending ingest, ids = paths).  A cell is EXCLUDED when a
running job owns it and nothing scanned it.  Everything else is UNSCANNED.  When unsure: UNSCANNED.
Every rule below carries its reason; nothing is inferred silently.
"""
import os, re, json, sys, collections, math

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..'))
TL = os.path.join(WS, 'research', 'tools', 'traillab')
CELLS_PATH = os.path.join(HERE, 'CELLS.jsonl')

OWN_STATUS = {'BEDROCK', 'COMPUTED', 'SAMPLED', 'LOCAL_ONLY', 'KILLED'}


def W(path):
    return os.path.join(WS, path)


def exists(path):
    return os.path.exists(W(path))


def read_text(path):
    try:
        return open(W(path), encoding='utf-8', errors='replace').read()
    except OSError:
        return ''


# ----------------------------------------------------------------------------------------------------------- store
RECS = {}
for _l in open(CELLS_PATH, encoding='utf-8'):
    _l = _l.strip()
    if _l:
        _r = json.loads(_l)
        RECS[_r['id']] = _r


def own(r):
    return bool(r.get('own_test')) and r.get('status') in OWN_STATUS


def ok_ids(ids):
    """keep only ids that exist in CELLS.jsonl and are own tests"""
    return [i for i in ids if i in RECS and own(RECS[i])]


# own-test records that name their universe cell in notes ("universe cell <hash>|<loc>|<object>|<Q>"), e.g. the scan-once wave
_CELLREF = re.compile(r'(sha256-3[78]|sha3-r[56]|blake3-r[23]|poseidon-r[12])\|[^\s,;|]+\|[^\s,;|]+\|(?:Q[1-5]|M[1-4]|R[1-4]|D1)')
# short form written by the sha3-r6 scan-once units: "universe cell round2.chi|Q1" (hash and object come from the record)
_CELLSHORT = re.compile(r'[Uu]niverse cell (round\d\.(\w+))\|(Q[1-5])')
NAMED = {}
for _i, _r in RECS.items():
    if own(_r):
        for _m in _CELLREF.finditer(_r.get('notes', '') + ' ' + _r.get('object', '')):
            NAMED.setdefault(_m.group(0), []).append(_i)
        for _m in _CELLSHORT.finditer(_r.get('notes', '')):
            NAMED.setdefault('%s|%s|%s|%s' % (_r['hash'], _m.group(1), _m.group(2), _m.group(3)), []).append(_i)


# ----------------------------------------------------------------------------------------------------------- chi files
def parse_chi(path):
    rows, rels, steps = {}, [], None
    for line in open(path, encoding='utf-8'):
        m = re.match(r'steps\s+(\d+)', line)
        if m:
            steps = int(m.group(1))
        m = re.match(r'row\s+(-?\d+)\s+(\S{32})\s+(\S{32})\s+(\S{32})', line)
        if m:
            rows[int(m.group(1))] = dict(A=m.group(2), E=m.group(3), W=m.group(4))
        m = re.match(r'x2\s+([AEW])(\d+)\[(\d+)\]\s*(!=|=)\s*([AEW])(\d+)\[(\d+)\]', line)
        if m:
            o1, r1, b1, op, o2, r2, b2 = m.groups()
            rels.append(dict(o1=o1, r1=int(r1), b1=int(b1), op=op, o2=o2, r2=int(r2), b2=int(b2),
                             text='%s%s[%s]%s%s%s[%s]' % (o1, r1, b1, op, o2, r2, b2),
                             row=min(int(r1), int(r2))))
    return rows, rels, steps


class Chi:
    def __init__(self, name, path):
        self.name = name
        self.rows, self.rels, self.steps = parse_chi(path)
        self.last = self.steps - 1
        self.relrow = collections.defaultdict(list)
        for r in self.rels:
            self.relrow[r['row']].append(r)

    def s(self, r, o):
        return self.rows.get(r, {}).get(o, '=' * 32)

    def cond_bits(self, r, o):
        """bit positions (LSB=0) with a value or signed-difference condition: 0 1 n u"""
        s = self.s(r, o)
        return sorted(31 - k for k, c in enumerate(s) if c in '01nu')

    def sign_bits(self, r, o):
        s = self.s(r, o)
        return sorted(31 - k for k, c in enumerate(s) if c in 'nu')

    def plus_bits(self, r, o):
        s = self.s(r, o)
        return sorted(31 - k for k, c in enumerate(s) if c == '+')

    def rel_conds(self, r):
        """conditions of the REL object of row r: x2 lines assigned to r, plus the plus-links not already stated by an x2 line.
        A plus link between row r and r+1 belongs to the earlier row r."""
        out = [('x2', x['text'], None, None, None) for x in self.relrow.get(r, [])]
        ends = set()
        for x in self.rels:
            ends.add((x['o1'], x['r1'], x['b1']))
            ends.add((x['o2'], x['r2'], x['b2']))
        for o in 'AEW':
            for b in self.plus_bits(r, o):
                if (o, r, b) in ends:
                    continue
                nxt = (31 - b) < 32 and self.s(r + 1, o)[31 - b] == '+'
                prv = self.s(r - 1, o)[31 - b] == '+'
                if prv and not nxt:
                    continue
                out.append(('plus', 'plus %s%d[%d]' % (o, r, b), o, r, b))
        return out

    def has_rel(self, r):
        return bool(self.rel_conds(r))


CHI = {'sha256-37': Chi('chi37', os.path.join(TL, 'chi', 'chi37.txt')),
       'sha256-38': Chi('chi38', os.path.join(TL, 'chi', 'chi38.txt'))}
SHA256 = ['sha256-37', 'sha256-38']
QNAME_SHA256 = {'Q1': 'printed-vs-pair', 'Q2': 'necessity (drop each printed condition singly)',
                'Q3': 'local freedom (log2 values consistent given earlier rows)',
                'Q4': 'alternative signings (same modular difference)', 'Q5': 'joint drop / interaction (singles vs pair)'}
QNAME_OTHER = {'Q1': 'difference/condition count as used', 'Q2': 'necessity of each condition group',
               'Q3': 'degrees of freedom', 'Q4': 'alternatives'}

# ----------------------------------------------------------------------------------------------------------- atlas matrices
def atlas37_codes():
    """ATLAS37.md full matrix -> {(i,j): code}"""
    txt = read_text('research/tools/traillab/ATLAS37.md')
    codes = {}
    i0 = txt.find('## Full matrix')
    if i0 < 0:
        return codes
    block = txt[i0:].split('\n## ', 1)[0]
    lines = [l for l in block.split('\n') if l.startswith('|')]
    cols = None
    for l in lines:
        cells = [c.strip() for c in l.strip().strip('|').split('|')]
        if cells[0].startswith('i \\') or cells[0].startswith('i \\\\') or cells[0].startswith('i'):
            if cols is None and cells[0].replace(' ', '').startswith('i\\'):
                cols = [int(c) for c in cells[1:]]
                continue
        m = re.match(r'\*\*(-?\d+)\*\*', cells[0])
        if m and cols:
            i = int(m.group(1))
            for j, c in zip(cols, cells[1:]):
                codes[(i, j)] = c
    return codes


def atlas38_cells():
    """evaluate atlas38_gen.py up to the point where it starts writing files; returns (cells, ev) or ({}, {})"""
    p = os.path.join(TL, 'atlas38_gen.py')
    try:
        src = open(p, encoding='utf-8').read()
        cut = src.index('\nmd = []')
        ns = {'__name__': 'atlas38_gen_readonly', '__file__': p}
        exec(compile(src[:cut], p, 'exec'), ns)
        return ns['CELLS'], ns['EVBY']
    except Exception as e:  # honest fallback: everything undecided
        sys.stderr.write('atlas38_gen read failed: %r\n' % (e,))
        return {}, {}


A37 = atlas37_codes()
A38, EV38 = atlas38_cells()

# ----------------------------------------------------------------------------------------------------------- Q2 parse
def build_q2_cover(h, chi):
    """conditions named in own drop/necessity records of CELLS.jsonl: {(obj,row,bit): [ids]} and {relation text: [ids]}"""
    cov, relcov = {}, {}
    relkeys = {r['text']: r for r in chi.rels}
    for r in RECS.values():
        if r['hash'] != h or not own(r):
            continue
        t = r['object'] + ' || ' + r['question']
        if not (re.search(r'drop|necess|implied|free\?|parit|Can .* be', t, re.I) or r['id'] in Q2_EXTRA_IDS):
            continue
        tn = re.sub(r'\s+', '', t)
        for k in relkeys:
            if k in tn:
                relcov.setdefault(k, []).append(r['id'])
                tn = tn.replace(k, '')
        for m in re.finditer(r'([AEW])(\d+)\[(\d+)\]', tn):
            cov.setdefault((m.group(1), int(m.group(2)), int(m.group(3))), []).append(r['id'])
        for m in re.finditer(r'([AEW])(\d+)\[([\d,]+)\]', tn):
            for b in m.group(3).split(','):
                if b.isdigit() and int(b) < 32:
                    cov.setdefault((m.group(1), int(m.group(2)), int(b)), []).append(r['id'])
        for m in re.finditer(r'\b([AEW])(\d+)\b[^|;]*?\bbits?\s+([0-9][0-9, ;=01]*)', t):
            for b in re.findall(r'(\d+)(?:=[01])?', m.group(3)):
                if int(b) < 32:
                    cov.setdefault((m.group(1), int(m.group(2)), int(b)), []).append(r['id'])
        for m in re.finditer(r'\b([AEW])(\d+)\s+(?:value\s+)?(?:mask\s+)?([0-9a-f]{8})\b', t):
            v = int(m.group(3), 16)
            for b in range(32):
                if v >> b & 1:
                    cov.setdefault((m.group(1), int(m.group(2)), b), []).append(r['id'])
    return cov, relcov


Q2_EXTRA_IDS = {'S37-E1', 'S37-E4', 'S37-E15', 'S37-E5', 'S37-E6', 'S37-O1', 'S37-O2', 'S37-O3', 'S37-O4', 'S37-FP-base'}

# ----------------------------------------------------------------------------------------------------------- cell model
def mk(h, kind, loc, obj, q, **kw):
    c = dict(id='%s|%s|%s|%s' % (h, loc, obj, q), hash=h, kind=kind, loc=loc, object=obj, q=q)
    c.update(kw)
    return c


def build_sha256_universe(h):
    chi = CHI[h]
    cells = []
    for r in range(-4, chi.last + 1):
        objs = ['A', 'E'] if r < 0 else ['A', 'E', 'W']
        if r >= 0 and chi.has_rel(r):
            objs.append('REL')
        for o in objs:
            for q in ('Q1', 'Q2', 'Q3', 'Q4'):
                cells.append(mk(h, 'row', 'r%d' % r, o, q, row=r))
    for i in range(-4, chi.last + 1):
        for k in range(1, 5):
            j = i + k
            if j <= chi.last:
                cells.append(mk(h, 'pair', 'int(%d,%d)' % (i, j), 'PAIR', 'Q5', row=j, row_i=i, row_j=j))
    for j in range(16, chi.last + 1):
        for d, kind in ((2, 's1'), (7, 'add'), (15, 's0'), (16, 'add')):
            i = j - d
            cells.append(mk(h, 'sched', 'sched(W%d<-W%d:%s)' % (j, i, kind), 'LINK', 'Q5', row=j, row_i=i, row_j=j, tap=kind))
    return cells


def build_sha3_universe(h):
    rounds = 5 if h == 'sha3-r5' else 6
    cells = []
    for rd in range(rounds):
        for st in ('theta', 'rho', 'pi', 'chi', 'iota'):
            for q in ('Q1', 'Q2', 'Q3', 'Q4'):
                cells.append(mk(h, 'sha3step', 'round%d.%s' % (rd, st), st, q, round=rd))
    return cells


B3_CALLS = ['K0', 'K1', 'K2', 'K3', 'D0', 'D1', 'D2', 'D3', 'C0', 'C1', 'C2', 'C3', 'E0', 'E1', 'E2', 'E3']
B3_CODE = {}
for _c in B3_CALLS:
    if _c[0] in 'KD' or _c in ('C0', 'C2'):
        B3_CODE[_c] = ['I', 'I', 'I', 'I']
    elif _c == 'C1':
        B3_CODE[_c] = ['$', '$', '$', '$']
    elif _c == 'C3':
        B3_CODE[_c] = ['P', 'P', 'P', 'P']
    elif _c in ('E0', 'E2'):
        B3_CODE[_c] = ['0', '0', '0', '0']
    elif _c == 'E1':
        B3_CODE[_c] = ['0', '$', 'L', 'F']
    elif _c == 'E3':
        B3_CODE[_c] = ['F', '$', 'F', '$']
B3_GRID_ROUND = {c: (1 if c[0] == 'E' else 0) for c in B3_CALLS}   # as printed in GRID_BLAKE3.md


def build_blake3_universe():
    h = 'blake3-r2'
    cells = []
    for c in B3_CALLS:
        for qi in range(1, 5):
            for q in ('Q1', 'Q2', 'Q3', 'Q4'):
                cells.append(mk(h, 'b3step', '%s.q%d' % (c, qi), 'step', q, call=c, quarter=qi, code=B3_CODE[c][qi - 1]))
    for w in range(16):
        for q in ('Q1', 'Q2', 'Q3', 'Q4'):
            cells.append(mk(h, 'b3word', 'm%d' % w, 'msgword', q, word=w))
    return cells


# ----------------------------------------------------------------------------------------------------------- results
def res(state, basis, reason, evidence=(), owner=None, missing=None):
    return dict(state=state, basis=basis, reason=reason, evidence=list(evidence), owner=owner, missing=missing or [])


def scanned_struct(reason):
    return res('SCANNED', 'STRUCTURAL', reason)


def scanned_cells(ids, reason):
    return res('SCANNED', 'CELLS', reason, ids)


def scanned_file(paths, reason):
    return res('SCANNED', 'FILE', reason + ' [result file of our own code, not yet in CELLS.jsonl: pending ingest]', paths)


def excluded(owner, reason):
    return res('EXCLUDED', 'OWNED', reason, owner=owner)


def unscanned(reason, missing=None):
    return res('UNSCANNED', 'NONE', reason, missing=missing)


OWN_JOBS = {
    'rows38': 'workflow rows38-full-dig',
    'close37': 'workflow close-open-rows-37',
    'dense': 'workflow dense-dig',
    'luna2': 'Luna 2 (folder 2nd_openai_workspace)',
    'd180': 'Luna local D180 (SHA3 cell fill)',
    'd181': 'Luna local D181 (BLAKE3 G-step cell fill)',
}


def covered_by_rule(h, c, ids):
    return ok_ids(ids)


# ----------------------------------------------------------------------------------------------------------- sha256 evaluation
def r37_obj_info(chi, r, o):
    if o == 'REL':
        rc = chi.rel_conds(r)
        return dict(conds=[x[1] for x in rc], nsign=len(rc))
    cb = chi.cond_bits(r, o)
    return dict(conds=['%s%d[%d]' % (o, r, b) for b in cb], nsign=len(chi.sign_bits(r, o)))


def row_has_any_cond(chi, r):
    return any(chi.cond_bits(r, o) for o in 'AEW') or chi.has_rel(r)


# row-level knowledge for sha256-37 (reasons are the evidence statements of the cited records)
ZD37 = {r: 'S37-ZDOWN-%02d' % r for r in range(4, 14)}


def eval_sha256(h, c, chi, q2cover, relcover):
    r, o, q = c.get('row'), c['object'], c['q']
    is37 = (h == 'sha256-37')
    last = chi.last
    # ---- row cells
    if c['kind'] == 'row':
        info = r37_obj_info(chi, r, o) if r >= 0 else dict(conds=[], nsign=0)
        conds = info['conds']
        # structural: chaining value rows
        if r < 0:
            return scanned_struct('CV coordinate: the two members share the chaining value; no step, no word, no condition (BEDROCK by structure)')
        # ----- Q1
        if q == 'Q1':
            if r in range(0, 4) and not row_has_any_cond(chi, r) and r <= 3:
                return scanned_struct('rows 0..3 carry no difference and no condition; identical inputs give identical states')
            if is37:
                ids = ok_ids(['S37-DB-BASIC'])
                if ids:
                    return scanned_cells(ids, 'S37-DB-BASIC: both members of the published pair reproduce the digest; 0 failures on every cell of rows -4..36, every plus pair and all 31 two-bit conditions')
            else:
                f = 'research/tools/traillab/atlas_runs38/A-dense/check.txt'
                if 'published pair vs every printed condition (rows 0..37): 0 failing rows' in read_text(f):
                    return scanned_file([f], 'traillab check: published 38-step pair vs every printed condition (rows 0..37): 0 failing rows, both digests equal')
            return unscanned('no own record replays the published pair against this cell')
        # ----- Q2
        if q == 'Q2':
            if not conds:
                return scanned_struct('no printed condition on this object, nothing to drop (trivially empty)')
            res_ = q2_status(h, chi, c, info, q2cover, relcover)
            if res_:
                return res_
            return q2_exclusion_or_unscanned(h, c, info, q2cover, relcover)
        # ----- Q3
        if q == 'Q3':
            return eval_q3(h, c, chi, info)
        # ----- Q4
        if q == 'Q4':
            return eval_q4(h, c, chi, info)
    # ---- interaction / schedule cells
    return eval_q5(h, c, chi)


def q2_status(h, chi, c, info, q2cover, relcover):
    r, o = c['row'], c['object']
    # row-level own dossiers (dense rows): Zone D dossier of the row = necessity of the printed conditions of that row
    if h == 'sha256-37' and r in ZD37:
        ids = ok_ids([ZD37[r]])
        if ids:
            return scanned_cells(ids, 'Zone D dossier of row %d (own trail lab): necessity of the row\'s printed conditions and the row\'s local freedom' % r)
    # parse coverage
    ids = []
    missing = []
    if o == 'REL':
        for kind, text, oo, rr, b in chi.rel_conds(r):
            if kind == 'x2':
                if text in relcover:
                    ids += relcover[text]
                else:
                    missing.append(text)
            else:
                if (oo, rr, b) in q2cover:
                    ids += q2cover[(oo, rr, b)]
                else:
                    missing.append(text)
    else:
        for b in chi.cond_bits(r, o):
            if (o, r, b) in q2cover:
                ids += q2cover[(o, r, b)]
            else:
                manual = Q2_MANUAL.get((h, o, r, b))
                if manual and ok_ids(manual[0]):
                    ids += ok_ids(manual[0])
                else:
                    missing.append('%s%d[%d]' % (o, r, b))
    ids = sorted(set(ids))
    if not missing:
        return scanned_cells(ids, 'every printed condition of this object is named in an own drop/necessity record')
    c['_q2_partial'] = (ids, missing)
    return None


# conditions covered by a named own record whose text does not list them bit by bit
Q2_MANUAL = {
    ('sha256-37', 'E', 22, 29): (['S37-E4', 'S37-E15'], 'E22[29] is the coin of the exact event (rows 22+): S37-E4 exact event, S37-E15 row 22 adds no state condition'),
}


def q2_exclusion_or_unscanned(h, c, info, q2cover, relcover):
    r, o = c['row'], c['object']
    part = c.pop('_q2_partial', (None, None))
    missing = part[1] if part[1] is not None else info['conds']
    if h == 'sha256-38':
        if r <= 16:
            return excluded(OWN_JOBS['luna2'], 'sha256-38 rows -4..16 Q2/Q3 are assigned to Luna 2')
        return excluded(OWN_JOBS['rows38'], 'sha256-38 rows 17..37 Q2/Q5 are owned by rows38-full-dig')
    if h == 'sha256-37' and r in (22, 24) and o in ('W', 'REL'):
        return excluded(OWN_JOBS['close37'], 'rows 22/24 matrix (W22/W24 exact sets and their conditions) is owned by close-open-rows-37')
    msg = 'conditions without an own drop/necessity record: ' + ', '.join(missing[:40])
    return unscanned(msg, missing)


def eval_q3(h, c, chi, info):
    r, o = c['row'], c['object']
    conds = info['conds']
    is37 = (h == 'sha256-37')
    last = chi.last
    if r in range(0, 4) and not row_has_any_cond(chi, r):
        return scanned_struct('rows 0..3 have no condition: W%d is a free base word (32 bits), E/A are bijective images of it; nothing to count' % r)
    if is37:
        if r in ZD37:
            ids = ok_ids([ZD37[r]])
            if ids:
                return scanned_cells(ids, 'Zone D dossier of row %d: freedom left in the row (own trail lab)' % r)
        if r == 14:
            ids = ok_ids(['S37-ATLAS-A1', 'S37-assign014'])
            if ids:
                return scanned_cells(ids, 'row 14 holds with Pr 1 given the dense part; X_E 0 free bits exact; X_A 30 free bits sampled (atlas_runs derive-anchor-row14-and-row16)')
        if r == 15:
            ids = ok_ids(['S37-ATLAS-H1a', 'S37-assign014'])
            if ids:
                return scanned_cells(ids, 'row 15 holds for 32 of 32 l with count 1 each (exhaustive, hot-H1)')
        if r == 16 and (conds or o == 'REL'):
            ids = ok_ids(['S37-E8-OWN', 'S37-DB-STAGES', 'S37-ATLAS-A2'])
            if ids:
                return scanned_cells(ids, 'row 16 exact per-L* enumeration (1,052,672 (u,l) pairs, 28 of 32 l) and stage cost 2^-16.994')
        if r == 17 and (conds or o == 'REL'):
            ids = ok_ids(['S37-O10', 'S37-D175-E17', 'S37-D174-MASK', 'S37-DB-STAGES'])
            if ids:
                return scanned_cells(ids, 'exact row-17 pass rate given row 16 (S37-O10), nine-bit E17 pattern enumeration, stage cost 2^-13')
        if 18 <= r <= 24 and (conds or o == 'REL'):
            ids = ok_ids(['S37-DB-STAGES', 'S37-JOB2-PAT', 'S37-E4'])
            if ids:
                return scanned_cells(ids, 'per-row stage cost of rows 16..36 on an independent particle filter (S37-DB-STAGES: 15/6/7/1/11/4 bits) and per-pattern survival rows 18..21')
        if r >= 16 and not conds and o != 'REL':
            return scanned_struct('rows >= 16: this object is determined by the E-driven choice, the earlier rows and the schedule; zero local freedom (S37-assign25 for rows 25..36; rows 16..24 stage costs in S37-DB-STAGES)')
        if (r == 23 or 25 <= r <= last):
            ids = ok_ids(['S37-assign25', 'S37-E14', 'S37-E21'])
            if ids:
                return scanned_cells(ids, 'rows 23, 25..36: no state lever; collision <=> equal after row 24 AND dW26 = 0 (BEDROCK); dW23 = dW25 = 0 proved')
        if r == 24 and not conds and o != 'REL':
            return scanned_struct('row 24 A/E: no printed condition, determined by earlier rows')
        if r == 24 or r == 22 and o in ('W', 'REL'):
            return excluded(OWN_JOBS['close37'], 'rows 22/24 matrix owned by close-open-rows-37')
        if r == 22:
            ids = ok_ids(['S37-DB-STAGES', 'S37-E4'])
            if ids:
                return scanned_cells(ids, 'row 22: stage cost and exact-event coin E22[29]')
        return unscanned('no own freedom count for this row/object')
    # sha256-38
    if r < 0:
        return scanned_struct('CV coordinate')
    if r <= 4 and not row_has_any_cond(chi, r):
        return scanned_struct('rows 0..4 carry no condition and no difference (ATLAS38 A1: dW0..dW6 = 0, common CV)')
    # run-time facts: result files of the running job (our traillab), cited by their atlas38_gen evidence ids
    f_exact = {rr: 'research/tools/traillab/atlas_runs38/R-rows/exact_r%d_E%dall_%s.txt' % (rr, rr, 'pub' if rr == 16 else 'smc2') for rr in range(16, 22)}
    if r == 16 and o == 'E' and exists(f_exact[16]):
        return scanned_file([f_exact[16]], 'row 16 on the head: E16 over all 2^32 with rows <= 15 held: exactly 32 values pass')
    if 17 <= r <= 21 and (conds or o == 'REL') and exists(f_exact[r]):
        return scanned_file([f_exact[r]], 'exact enumeration of E%d over all 2^32 on two SMC bases: cells count (all-or-none) for row %d' % (r, r))
    if r >= 22 and not conds and o != 'REL':
        return scanned_struct('rows 22..37: automatic once E21[2]=E21[16], E22[29]=0, E23[29]=1, dW23, dW25 hold; X_E has 1 value over 0 free bits (determined state)')
    if r >= 17 and not conds and o != 'REL':
        return scanned_struct('rows >= 17: determined by the E-driven choice (rows 16..21), earlier rows and the schedule; zero local freedom')
    if r in (22, 23, 24, 25) or r >= 22:
        ev_ok = [e for e in ('G1', 'G2', 'G4', 'G5', 'G6', 'G7') if e in EV38]
        if ev_ok:
            files = sorted({f for e in ev_ok for f in EV38[e]['files']})
            return scanned_file(files[:6], 'ATLAS38 evidence %s: W23 exact set 9,830,400, W25 exact set 293,601,280, rows 22..37 automatic' % ','.join(ev_ok))
    if r <= 16:
        return excluded(OWN_JOBS['luna2'], 'sha256-38 rows -4..16 Q2/Q3 are assigned to Luna 2')
    return unscanned('no own freedom count for this 38-step row/object')


def eval_q4(h, c, chi, info):
    r, o = c['row'], c['object']
    is37 = (h == 'sha256-37')
    last = chi.last
    if r < 0:
        return scanned_struct('CV coordinate: no difference, no signing')
    if o != 'REL' and info['nsign'] == 0:
        return scanned_struct('object has no signed (n/u) cell: its modular difference is zero, the only pattern is the all-equal one (trivially empty)')
    dense_max = 15 if is37 else 16
    # records first (scanned beats excluded)
    if is37:
        if r == 16 and o == 'A':
            ids = ok_ids(['S37-O5'])
            if ids:
                return scanned_cells(ids, 'S37-O5: alternative signings of the A16 difference path into E20 (own, COMPUTED)')
    else:
        if r == 16 and o == 'E':
            f = 'research/tools/traillab/atlas_runs38/H-drops/out/t05_sE16.txt'
            if exists(f):
                return scanned_file([f], 'ATLAS38 H4: other E16 signings (dropsign E16): the relaxed row-16 set is still exactly the 32 printed words; no alternative signing on this head')
        if (r == 25 and o in ('W', 'REL')) or (r == 23 and o == 'W'):
            ids = ok_ids(['S38-W25mod-p', 'S38-W25mod-o']) if r == 25 else []
            files = [f for f in ('research/retest/backward38/wcount.txt',) if exists(f)]
            if ids:
                return scanned_cells(ids, 'W25 alternative carry patterns with the same modular difference: S38-W25mod (modular-only accepted patterns)')
            if files and 'G1' in EV38 and r == 23:
                return scanned_file(files, 'W23 exact set 9,830,400 of 2^32 (every W23 with the right modular s1 difference) and the 8 value-bit patterns: only the printed one keeps the later differences (ATLAS38 G1)')
        if r in (19, 20) and o == 'E':
            ids = ok_ids(['S38-FP', 'S38-STACK-A'])
            if ids:
                return scanned_cells(ids, 'E19/E20 four patterns + tie (S38-FP): alternatives of the E19/E20 value pattern measured on the 38-step law')
    # exclusions
    if is37:
        if r <= dense_max:
            return excluded(OWN_JOBS['dense'], 'dense rows <= 15: alternative dense characteristics belong to dense characteristic derivation')
        if r == 8 and o == 'W':
            return excluded(OWN_JOBS['close37'], 'W8 signings')
        if r == 20 and o == 'E':
            return excluded(OWN_JOBS['close37'], 'E20 signing')
        if 18 <= r <= 21 and o in ('E', 'REL'):
            return excluded(OWN_JOBS['close37'], 'per-pattern survival rows 18/19 and 20/21')
        if r in (22, 24):
            return excluded(OWN_JOBS['close37'], 'rows 22/24 matrix')
        if r == 16 and o in ('E', 'REL'):
            return excluded(OWN_JOBS['close37'], 'R16x per l (E16 / row-16 relation alternatives)')
    else:
        if r <= dense_max:
            return excluded(OWN_JOBS['dense'], 'dense rows <= 16: alternative dense characteristics belong to dense characteristic derivation')
    return unscanned('signed cells / relations with no own alternatives test: %s' % ('relations' if o == 'REL' else 'n/u cells at bits ' + ','.join(str(b) for b in chi.sign_bits(r, o))))


def eval_q5(h, c, chi):
    i, j = c['row_i'], c['row_j']
    is37 = (h == 'sha256-37')
    last = chi.last
    if is37:
        code = A37.get((i, j))
        if code is None:
            return unscanned('pair is outside the ATLAS37 matrix')
        if i < 0 and c['kind'] == 'pair':
            return scanned_struct('CV rows -4..-1: chaining-value words, no difference; ATLAS37 cell (%d,%d) = %s' % (i, j, code))
        if '?' in code:
            return unscanned('ATLAS37 cell (%d,%d) = %s still carries ? (read but undecided)' % (i, j, code))
        # joint-drop records name both rows
        ids = []
        for rid, r in RECS.items():
            if r['hash'] == h and own(r) and (r.get('row_i'), r.get('row_j')) == (i, j) and r['id'].startswith(('S37-Q', 'S37-ATLAS', 'S37-PAIR', 'S37-O')):
                ids.append(rid)
        if code == '.':
            return scanned_struct('ATLAS37 cell (%d,%d) is neutral: no direct state read or schedule tap, nothing to interact' % (i, j))
        return res('SCANNED', 'CELLS' if ids else 'FILE', 'ATLAS37 matrix cell (%d,%d) = %s, decided (no ?): our measured/proved result for how row %d acts on row %d' % (i, j, code, i, j),
                   ids or ['research/tools/traillab/ATLAS37.md'])
    # 38
    cell = A38.get((i, j))
    if cell is None:
        return unscanned('pair is outside the ATLAS38 matrix')
    if i < 0:
        return scanned_struct('CV rows -4..-1: chaining-value words, no difference')
    labs = cell['labels']
    if '?' in labs:
        if j >= 17:
            return excluded(OWN_JOBS['rows38'], 'sha256-38 rows 17..37 Q2/Q5 are owned by rows38-full-dig (ATLAS38 cell (%d,%d) = ?)' % (i, j))
        return unscanned('ATLAS38 cell (%d,%d) is undecided (?)' % (i, j))
    if labs == ['N']:
        return scanned_struct('ATLAS38 cell (%d,%d) neutral: no direct state read or schedule tap' % (i, j))
    evs = cell['ev']
    if not evs:
        return unscanned('ATLAS38 cell (%d,%d) %s has no evidence id' % (i, j, ''.join(labs)))
    files = sorted({f for e in evs for f in EV38[e]['files']})[:4]
    return scanned_file(files, 'ATLAS38 cell (%d,%d) = %s decided by evidence %s' % (i, j, ''.join(L for L in labs if L != 'N'), ','.join(evs)))


# ----------------------------------------------------------------------------------------------------------- sha3 evaluation
SHA3_ATLAS = 'research/tools/traillab/ATLAS_SHA3.md'
SHA3_SCRIPTS = 'research/tools/traillab/sha3_atlas/'


def eval_sha3(c):
    h, rd, st, q = c['hash'], c['round'], c['object'], c['q']
    r5 = (h == 'sha3-r5')
    if st in ('rho', 'pi'):
        return scanned_struct('%s is a fixed bit permutation: output difference is a fixed function of the input difference, no condition, no freedom, no alternative (BEDROCK by the Keccak-f definition)' % st)
    if st == 'iota':
        return scanned_struct('iota XORs a round constant into one lane: differences are unchanged, no condition, no freedom, no alternative (BEDROCK by definition)')
    if st == 'theta':
        if q in ('Q1', 'Q2', 'Q3'):
            return scanned_struct('theta is a linear bijection: differences propagate deterministically, no condition, freedom is carried through unchanged (BEDROCK by definition)')
        # Q4: kernel / non-kernel alternatives
        if r5 and rd == 3 and exists(SHA3_SCRIPTS + 'ex.py'):
            return scanned_file([SHA3_ATLAS, SHA3_SCRIPTS + 'ex.py'], 'round-2 cluster count: the 512 in-kernel alpha3 variants and 50 single-row off-kernel changes were enumerated exactly; the CP-kernel test is the theta of round 3')
        if (not r5) and rd >= 2:
            return excluded(OWN_JOBS['d180'], 'r6 zero-digest 4-round cores (kernel class / parity sheets): D180 owns the open cells (partial own test C0020)')
        return unscanned('column-parity kernel alternatives at this theta have no own test')
    # chi
    if r5:
        if rd == 2:
            return scanned_file([SHA3_ATLAS, SHA3_SCRIPTS + 'ex.py', SHA3_SCRIPTS + 'clus2.py'],
                                'r5 round-2 cluster count, exact: 2^24 compatible alpha3, 511/512 in-kernel alternatives and 50/50 single-row changes give P45 = 0, 4,000 random of 2^24 give 0; the 24 printed equations are what the event needs')
        if rd == 3:
            if q == 'Q2':
                return scanned_struct('round 3 prints no condition (nothing to drop)')
            if q == 'Q1':
                return excluded(OWN_JOBS['d180'], 'r5 rounds 3-4 Markov premise (OTHER_HASH_DIG #5 / ATLAS_SHA3 ranked gap 2)')
            return scanned_file([SHA3_ATLAS, SHA3_SCRIPTS + 'ex.py'], 'P45 sums all 2^19 alpha4 exactly (ex.py reproduces 55/2^19); alternatives and freedom are inside that sum')
        if rd == 4:
            if q in ('Q1', 'Q3'):
                return excluded(OWN_JOBS['d180'], 'r5 rounds 3-4 Markov premise (ATLAS_SHA3 ranked gap 2)')
            return scanned_file([SHA3_ATLAS, SHA3_SCRIPTS + 'ex.py'], 'digest rows: DDT[q][0]+DDT[q][16], 4 of 5 bits per plane-0 row, lanes 0..3; branching over the 10 allowed digest-row values; event-exact')
        if rd in (0, 1):
            if q in ('Q2', 'Q4'):
                return excluded(OWN_JOBS['d180'], 'r5 connector relaxation (rounds 0-1; ATLAS_SHA3 ranked gap 3) and the D180 r5 trail-round cell fill')
            return unscanned('round %d connector/linear conditions are stated by the package proof (Lemma 2, 127 conditions) but no own count of this cell is recorded' % rd)
    # r6
    if rd == 5:
        if q == 'Q1':
            return scanned_file([SHA3_ATLAS], 'r6 filter: 8 digest-determined bits (z=0,1, lanes 0..3) equal-digest implied; width ledger k=7 21.25 / k=8 20.80 / k=9 23.77 (own exact ledger arithmetic)')
        if q == 'Q2':
            return scanned_file([SHA3_ATLAS, SHA3_SCRIPTS + 'deg6.py'], 'r6 filter width k=8 is the optimum by exact ledger arithmetic; all 8 forms have degree exactly 8 on 24 random cosets x 8-dim subspaces (deg6.py)')
        if q == 'Q3':
            return excluded(OWN_JOBS['d180'], 'r6 key/filter joint charge (ATLAS_SHA3 ranked gap 5)')
        return excluded(OWN_JOBS['d180'], 'r6 alternative 8-bit predicates (ATLAS_SHA3 ranked gap 4)')
    if q == 'Q4' and rd >= 2:
        return excluded(OWN_JOBS['d180'], 'r6 zero-digest 4-round cores (kernel class, parity sheets): D180 owns the open cells; partial own test C0020')
    return unscanned('the r6 line is a bit-sliced Gray-order birthday with prefix conditions (SHA3R6_MAP.md, leader route); there is no per-round count of the conditions, freedom or alternatives at this chi')


# ----------------------------------------------------------------------------------------------------------- blake3 evaluation
B3_ATLAS = 'research/tools/traillab/ATLAS_BLAKE3.md'


def eval_blake3(c):
    q = c['q']
    if c['kind'] == 'b3word':
        return unscanned('message word m%d: block layout (free / pinned / cancelling) and its conditions are stated in pkgB3U proof.md Sections 1-3 but no own per-word count is recorded' % c['word'])
    code, call, qi = c['code'], c['call'], c['quarter']
    if code == 'I':
        return scanned_struct('quarter-step solved exactly by construction (inversion): no characteristic layer, no condition, no carry-pattern choice; free words are a bijection onto admissible blocks (Lemma T2; ATLAS_BLAKE3 bottom line)')
    if code == '0':
        if q in ('Q1', 'Q3'):
            return scanned_struct('zero difference by identical inputs: output equal, nothing counted, no freedom')
        return unscanned('the zero-difference requirement is stricter than the XOR event; relaxing it activates more calls (CLOSED_DOORS BLAKE3 doors 22/24, both relabelled CLAIMED-UNTESTED); no own enumeration of the relaxation')
    if code == 'P':
        if q in ('Q1', 'Q3'):
            return scanned_struct('pinned advice constants (Fact P: equal b,d outputs; a,c differ by DY3,DY11): defined by construction, zero freedom')
        return unscanned('necessity of the C3 pin and alternative constants (door 33 constants search, old H8 profile) have no own test on the current ledger')
    if call == 'C1':
        if q in ('Q1', 'Q3'):
            return scanned_file([B3_ATLAS, 'research/tools/traillab/b3atlas/rows_dp.py'], 'C1 forward: the only condition is filter (1) on Y9 = Q: exact count 14,110,208 / 2^32 reproduced by our own DP (rows_dp.py); other quarter-steps of C1 carry no condition')
        if q == 'Q4':
            return excluded(OWN_JOBS['d181'], 'carry-pattern alternatives (75/32 effect) on every probabilistic stage')
        return unscanned('necessity of filter (1) / the exact prefilter PF: no own relaxation test')
    if call == 'E1':
        if qi == 2:
            if q == 'Q1':
                return scanned_file([B3_ATLAS, 'research/tools/traillab/b3atlas/rows_dp.py'], 'E1 q2 cube Q* fixes beta exactly: 14 outcomes of beta*, 19 of beta2, exact whole-word counts by our own DP (ATLAS_BLAKE3 table A)')
            if q == 'Q4':
                return excluded(OWN_JOBS['d181'], 'beta2 other 18 taus, third-beta row, carry-pattern alternatives on every probabilistic stage')
            return unscanned('necessity / freedom of the 11-bit cube Q*: stated by the proof (x2^11 rate), no own count of the cube dimension')
        if qi == 3:
            if q == 'Q4':
                return excluded(OWN_JOBS['d181'], 'beta2 other 18 taus (OTHER_HASH_DIG #4) and third-beta row')
            return scanned_file([B3_ATLAS, 'research/tools/traillab/b3atlas/rows_dp.py', 'research/tools/traillab/b3atlas/third.py'],
                                'E1 q3 listed tau 285020a0: parts r_j, filter words and ratios per outcome (table A/B of ATLAS_BLAKE3, own DP): every added outcome loses at the current ledger; listed subset is the optimum')
        if qi == 4:
            if q == 'Q1':
                return scanned_file([B3_ATLAS, 'research/tools/traillab/b3atlas/ey.py'], 'E1 q4 eps forced by beta (Lemma N), checked for all three listed betas by our own script')
            return scanned_struct('eps and b2 are exact XOR consequences of beta (Lemma N): forced, no condition, no freedom, no alternative')
    if call == 'E3':
        if qi == 1:
            ids = ok_ids(['B3-D179-affine-classes', 'B3-D179-exact-rep'])
            if q == 'Q2':
                return scanned_struct('e1 class / eta is an exact consequence of R = 0 (Lemma Q): forced, nothing to drop')
            if ids:
                return scanned_cells(ids, 'E3 q1: the class that fixes eta has exactly 16 classes x 32768 members, XOR rank 15 (D179 exact computations); counts and class alternatives')
            return unscanned('class structure not recorded')
        if q == 'Q1':
            return scanned_file([B3_ATLAS, 'research/tools/traillab/b3atlas/typed_check.py'], 'E3 J1/J2/J3 lists: filter (1) = 14,110,208, typed (2) union = 63,633,856, typed 23,820,160 / 34,028,800, all exact by our own DP and reproduced against the package')
        return excluded(OWN_JOBS['d181'], 'coupled omega list (J1 and J3 share h), carry-pattern alternatives on E3 $ stages, OPEN/CLAIMED cells of GRID_BLAKE3')
    return unscanned('no rule')


# ===================================================================================================== gap dimensions
# G02 memory objects, G04 CV / first block / padding, G05 BLAKE3 init / output / mode / doors, G06 SHA3 message / digest /
# condition groups / route ledger, G07 premises / op ledgers / judge causes.  Source of the dimensions: UNIVERSE_GAPS.md sections
# 4-7 and 9 (critic pass 2026-10-12).  NOT added (owned elsewhere): G01 Poseidon, G03 characteristic family, G08, G09.
# Every new cell is (hash, loc, object, question) like the wave-1 cells; group = G02 ... G07 (wave-1 cells carry group W1).
# A new cell is SCANNED only through GMAP below (rule + evidence ids/files + reason); the default is UNSCANNED.  Records that name
# "universe cell <id>" in notes (full id, as for wave 1) count as well.

GQ = {  # question text per group
    'G02': {'M1': 'bytes held by this object at its peak (exact allocation of the shipped program; say bound vs exact)',
            'M2': 'time (ledger operations, exact charge) to recompute / stream / shard this object instead of holding it, priced on the filed ledger',
            'M3': 'score-optimal point for this object: S = time_log2 + max(0, log2 bytes - 20) at the best hold-versus-recompute split, others fixed',
            'M4': 'breakpoint at 2^20 bytes: size/time trade at which total memory crosses 2^20 B, S on both sides, is crossing worth it'},
    'STD': dict(QNAME_OTHER),
    'G07': {'R1': 'value charged / stated and where (read the package, name the exact line)',
            'R2': 'own re-measurement or exact recount (fresh seed, preregistered rule, or metered run of the shipped program)',
            'R3': 'control: the same tool on a known answer or a negative control (fails where it must fail)',
            'R4': 'score sensitivity: bits per unit change of this premise / row, and slack candidates (best case the program executes)'},
    'D1': {'D1': 'the test written in the RELABEL column of CLOSED_DOORS.md for this door, run on our own code'},
}

_G_WEIGHT = {
    'M1': 3, 'M2': 7, 'M3': 5, 'M4': 5,
    'Q1': 4, 'Q2': 8, 'Q3': 6, 'Q4': 8,
    'R1': 3, 'R2': 14, 'R3': 7, 'R4': 5,
    'D1': 25,
}


def gc(h, group, kind, loc, obj, q, label, facts, cl, **kw):
    c = mk(h, kind, loc, obj, q, group=group, label=label, facts=facts, cl=cl)
    c.update(kw)
    return c


def _expand(h, group, kind, obj, qs, items, qtab=None):
    out = []
    for key, label, facts, cl in items:
        for q in qs:
            out.append(gc(h, group, kind, '%s.%s' % (obj, key), obj, q, label, facts, cl))
    return out


# ------------------------------------------------------------------------------------------------------------------ G02 objects
R37P = 'research/tools/build_pkg/scratch/pkgR37M3/pkg/sha256-r37/proof.md'
R38P = 'research/tools/build_pkg/scratch/pkgR38M3/pkg/sha256-r38/proof.md'
B3P = 'research/tools/build_pkg/scratch/pkgB3S2/pkg/blake3-r2/proof.md'
D126 = 'research/sol_answer_D126_memory_rule.md'
D152 = 'research/sol_answer_D152_r5_memshrink.md'
D161 = 'research/sol_answer_D161_r5_memory_tables.md'
D166 = 'research/sol_answer_D166_s6db_memory.md'
D117 = 'research/sol_answer_D117_r6_time_memory.md'
B3MAX = 'research/retest/b3m_maxphase/RESULT.md'
S5T = 'research/tighten/S5T_r5_memrule.md'
S6R = 'research/tighten/S6R_r6_memrule.md'
B3M = 'research/tighten/B3M_blake3_memrule.md'

MEM_OBJS = {
    'sha256-37': [
        ('T0', 'T0 table of the filed table line (x -> class)', '2^32 8-byte words = 34,359,738,368 B; the x-dependent region that D126 shards by B = 2^k; the filed R37/R37X lines hold it (memory bound 2^49.97 B)', 'line'),
        ('REC', '(x,class) record store of the filed table line', '15,130,951,680 records x 73,024 B = 1.1049e15 B (D126 reading of the r37 table-line proof)', 'line'),
        ('R16T', 'row-16 table of the filed table line', '2^34 32-byte words = 549,755,813,888 B; R37M3 replaces it by two 4096-word chunk tables (proof 6.2)', 'line'),
        ('ANC', 'ancillary code and working space of the filed table line', 'bound < 2^33 B; D126 marks the exact occupancy OPEN', 'line'),
        ('F7', 'F7 membership set (class gate on x = A_-1)', '|F7| = 68,157,440 of 2^32; R37M3 stores no table: a straight-line test of 166 primitives for all 222 classes; a bitmap would be 2^23 B', 'sets'),
        ('F6', 'F6 membership set (W6 test on cb = C6 - A_-2)', '|F6| = 287,309,824 of 2^32; R37M3 evaluates it as a bit-sliced plane program (404-431 primitives per batch of 256 reps), no table', 'sets'),
        ('G', 'A0-variant family G and the 222 class lists', '|G| = 12,103,680; 22,976 c7 classes; 222 classes >= 3456 = 782,800 variants; only the 222 descriptors (28,416 B) stay resident, lists are rebuilt in preprocessing', 'sets'),
        ('R16SET', 'row-16 accepted set (u, l) pairs', '1,052,672 accepted (u,l) pairs, 1,042,240 distinct u, 28 usable l of 32 (S37-E8-OWN); raw as 4-byte pairs 4.2 MB, held in R37M3 only through the two 4096-word chunk tables', 'sets'),
        ('PAIRS', 'per-first-block good-pair list', '831 good pairs on average (g = 830.988), read from packed entry words in groups of four; heavy-tailed (SD 4.2 x mean); not materialised separately in the proof table', 'tables'),
        ('REGS', 'plane registers (64-register budget)', '64 x 32 B = 2,048 B, included in the last constants of proof 14.1; peak live planes 40 (nested version needs ~62 of 64)', 'tables'),
        ('PLANES', 'planes of the reps (8 batches x 14 + 42 batches x 16 planes)', '25,088 B resident (proof 14.1, lowm.py memory)', 'tables'),
        ('ENTRIES', 'packed entries of the reps (50 batches x 64 words)', '102,400 B resident', 'tables'),
        ('CUBE', 'cube entries D[c] and the spill area of the class sums', '256 + 7,168 B', 'tables'),
        ('C7PL', 'c7 planes', '32 words = 1,024 B', 'tables'),
        ('CHUNK', 'chunk tables LO and MID (row 16 without a mask table)', '2 x 4096 words = 262,144 B; two reads per lane give the l in L*', 'tables'),
        ('SCANT', 'lane-scan table', '2048 words = 65,536 B', 'tables'),
        ('PERL', 'per-l constants, L* rows, characteristic cells, S', '4,096 + 40,960 B (bound 1280 words for cells/L*/S)', 'tables'),
        ('SCAL', 'scalar planes, cv_pre constants, first-block buffer', '3,072 + 2,048 B', 'tables'),
        ('CODE', 'program code', 'bound: at most 8192 primitives of 8 bytes = 65,536 B', 'code'),
        ('PRE', 'working set of the preprocessing (PRE < 2^38 operations)', 'family discovery over 2^29 values of E4, grouping by c7 (12,103,680 members), ten lists, planes, tables; proof 14.1 total 607,744 B is the ONLINE resident set, the preprocessing peak is not stated', 'code'),
    ],
    'sha256-38': [
        ('SENT', '256-block sentinel pass table of the filed table line', '256 x 2^64 words in the D126 formula W = 256 2^64 + 3 (S_R 22 2^32) + 3 min(S_R 22 2^32, 256 2^64)', 'line'),
        ('HDR', 'header tables of the filed table line', '3 x S_R 22 2^32 words, S_R = 191,773,672,732 (D126)', 'line'),
        ('P6T', 'P6 table-build terms of the filed table line', '3 x min(S_R 22 2^32, 256 2^64) words; D126 shards them (best k = 19, S 130.17)', 'line'),
        ('FIX38', 'fixed non-table terms of the filed table line', '583,910,972,788 words = 18,685,151,129,216 B; ledger bound 2^80.955 B in total', 'line'),
        ('F7T', 'F7 decision tree (memory-free W7 test)', '52 instructions + 5 loop slots at 32 B = 1,824 B; 12.64 + 4 primitives per class (proof 5.1, 14)', 'sets'),
        ('PL90', 'batch planes of the 90 classes', '15 batches, one word per variable bit of a0: 675,840 B; classes re-optimised until the total sits 2,784 B under 2^20 (R38M 64 classes -> R38M3 90)', 'tables'),
        ('SHC', 'shared-constant words of the classes', '11,520 B', 'tables'),
        ('BCAST', 'per-first-block broadcast planes (7 x 32 words)', '7,168 B', 'tables'),
        ('SPILL', 'spill slots of the plane programs', '1,280 B (15 used of at most 40 words)', 'tables'),
        ('SCAL38', 'scalars, counters, hit list, F7 constants (64 words)', '2,048 B (a hit list of one word per class would add 832 B)', 'tables'),
        ('CTAB', 'class table (c7, base, mask, program number)', '90 x 3 words = 8,640 B', 'tables'),
        ('CODE7', 'code of the seven plane programs', '9,946 instructions x 32 B = 318,272 B; the model has no code size of its own', 'code'),
        ('CODEO', 'code of the W7 loop and the other routines', '57 + 600 instructions x 32 B = 1,824 + 19,200 B', 'code'),
        ('PRE38', 'working set of the precomputation', 'one class at a time: every subset of the mask (<= 2^17 candidates, 3840 survivors, 15 KB); 2^32 operations to generate the seven programs', 'code'),
    ],
    'sha3-r5': [
        ('PHALF', 'P one-core half tables (trail search)', '2 x 9^5 x 22 x 32 = 83,140,992 B, deleted before the next core (W.4)', 'P'),
        ('PARR', 'P sort / key / index arrays of one block', '2 x 9^5 x 8 = 944,784 B', 'P'),
        ('T1CORES', 'T1/T2 core list (467 kept of 1,741 cores) and the MINW / WT2 tables', 'cores.bin; not itemised in D161', 'P'),
        ('BPRIME', "B-prime candidate working set", '113.5 MiB stated by the v14 lineage (not measured by us); dominates the 2^27 phase peak (D152)', 'conn'),
        ('CONN', 'connector scratch', 'bound < 2^23 B', 'conn'),
        ('EM1', 'one accepted echelon system EM', '31/50 = 0.62 MiB stated', 'conn'),
        ('EM50', 'the K = 50 accepted echelon systems held before E', '31 MiB stated; streaming one at a time costs <= 2^31 + 16,252,928 primitives (D152: S 39.79188)', 'conn'),
        ('EVEC', 'E derivative vectors D1..D4', '(24 + 276 + 2,024 + 10,626) vectors x 24 words x 32 B = 9,945,600 B', 'E'),
        ('EANF', 'E ANF setup table (fes.c)', '41,449 x 768 B = 31,832,832 B', 'E'),
        ('EBUF', 'E pass buffer', '32,768 B', 'E'),
        ('EKEY', 'E stage-1 resident tables (29 tables, spill rule)', 'Z.3: 12 passes of 2 equation words, 29 resident tables; the R5-E1 stage-1 split (24 equations) is OPEN', 'E'),
        ('CODE5', 'straight-line code of the E block', '12 passes x 1,024 step bodies = 207,920 counted primitives, < 2^18 instructions', 'E'),
    ],
    'sha3-r6': [
        ('ARR', 'value-masked key array of the filed time line', '2^140 key words used, never initialised, memory below 2^144 words (D117, quoted from the f8867a5d proof)', 'line'),
        ('COSET', 'retained coset records / tagged table of the filed lines', 'tagged table 11Q/2 or sparse-set table 9Q (rivals); 2^146 B claimed on the board', 'line'),
        ('ONCE', 'generated code and ONCE preprocessing of the filed lines', 'ONCE <= 2^70 + 16 operations; generated code below 2^62 words', 'line'),
        ('FORMS8', '8 value-masked XOR-form table (8FORMS)', 'replaces 10 planes + 33 operations; filed 909b6453 121.8701', 'line'),
        ('BUF', 'P,Q plane buffers of the memory-rule line S6DB', '2 x 1,600 planes = 3,200 words = 102,400 B (D166)', 's6db'),
        ('INPL', 'input planes IN', '256 words = 8,192 B', 's6db'),
        ('RCT', 'round constants RCT', '5 words = 160 B', 's6db'),
        ('LIDLST', 'LID and LST', '512 words = 16,384 B', 's6db'),
        ('ENDP', 'endpoint table (123-bit records, S = U)', '5,000 words as claimed, 3,131 words in the exact-2^20 variant (D166)', 's6db'),
        ('SCR6', 'scratch', '64 words = 2,048 B', 's6db'),
        ('CODE6', 'code of S6DB', '25,600 words = 819,200 B; total 1,108,384 B = 2^20.0801', 's6db'),
        ('DPTAB', 'distinguished-point slot table of the generic S6R line', 'S = 10,200 slots x 96 B = 979,200 B, total 1,046,784 B (S6R audit item 6)', 's6r'),
        ('K13', 'K = 13 Gray-body table', 'OPEN: S 124.05 predicted vs 125.28 (S6D); needs a counted bit-slice', 's6r'),
        ('T35', '35-plane key table (round 6 on 35 planes x 4 lanes = 140 key bits)', 'planes of the final round kept per batch for the key; size follows the batch, not itemised in the S6DB layout', 's6r'),
        ('DPRHO', 'dense bit-sliced DP-rho unit (256 lanes)', '152.99 ops/step counted -> S 124.63; per 64-bit word 499-612 ops/step -> 126.3-126.6 (OPEN)', 's6r'),
    ],
    'blake3-r2': [
        ('T2G', "T2', T1 and gate-table band", '2^34 + 2^30 words = 18,253,611,008 words (B3S2 proof 12)', 'tables'),
        ('REPL', 'six lane replicas of T2, T1, gate', '6 (2^34 + 2^30) = 109,521,666,048 words; B3-replica cut OPEN', 'tables'),
        ('PXF', "PXF' table", '3 x 2^32 words', 'tables'),
        ('ROT', 'the three rotation tables', '3 x 2^32 words', 'tables'),
        ('BT', 'BT and its six lane copies', '7 x 2^32 words', 'tables'),
        ('SMALL', 'member lists, P, automata, solver arrays, names', '< 2,563,914 words (< 82,045,248 B)', 'tables'),
        ('CODE3', 'written-out code', '< 2^32 instructions = < 2^37 B', 'code'),
        ('OUT3', 'output F||A and F||B (1024 t + 55 / 63 bytes, t <= 2^32 - 1)', 'at most 2^43 - 1,930 B, the peak phase; release-before-write gives 43.0 instead of 43.752 (B3-RELEASE); B3-STREAM OPEN', 'out'),
        ('SEL3', 'preprocessing selection SEL', 'halts at 2^34 B, one program at a time; preprocessing 2^54 (b3m_maxphase)', 'out'),
        ('OMEGA', 'typed omega lists', '23,820,160 (t = 0) and 34,028,800 (t = 1) words; the filed B3V ships them as 5 bit-masks on omega bits 16-22', 'lists'),
    ],
}


def build_g02():
    cells = []
    for h, items in MEM_OBJS.items():
        cells += _expand(h, 'G02', 'mem', 'MEM', ('M1', 'M2', 'M3', 'M4'), items)
    return cells

# ------------------------------------------------------------------------------------------------------------------ G04 objects
def g04_items(h):
    chi = CHI[h]
    last = chi.last
    is37 = (h == 'sha256-37')
    n = 37 if is37 else 38
    cl = 'F7: |F7| = 68,157,440 (p7 = 2^-5.97763)' if is37 else 'F7 and its 52-instruction decision tree (hits38.c / fam38.c exact over all 2^32 values of A_-1)'
    cls = ('222 classes >= 3456 variants = 782,800 variants of 22,976 c7 classes' if is37 else '90 classes of 3840 variants (15 batches of 256), three program shapes')
    return [
        ('A-1', 'CV word A_-1 = x (class gate)', 'x = A_-1 must lie in the class gate: ' + cl + '; the attack gates on the real first-block chaining value, so this word is NOT free (UNIVERSE_GAPS S1)', 'gate'),
        ('A-2', 'CV word A_-2 (second gate cb = C6 - A_-2)', ('cb = C6 - A_-2 must lie in F6 (|F6| = 287,309,824, p6 = 2^-3.90197); r37 proof 12 H1: x and cb independent uniform' if is37 else 'second CV-dependent test of the 38-step program: the 12 tested bits of E16x per plane program (check what, if anything, is the F6 analogue)'), 'gate'),
        ('A-3', 'CV word A_-3', 'enters rows 0..3 (ATLAS cell D, direct state read); the proof states that nothing depends on cb or any other CV word except through H1', 'words'),
        ('A-4', 'CV word A_-4', 'enters rows 0..3 (direct state read)', 'words'),
        ('E-4', 'CV word E_-4', ('own test S37-J5-E4BUCKET: row-16 pass rate per E_-4 bucket (2^31 good pairs, real first blocks 2^29)' if is37 else 'direct state read; no bucket test recorded on the 38-step law'), 'words'),
        ('E-3', 'CV word E_-3', 'direct state read', 'words'),
        ('E-2', 'CV word E_-2', 'direct state read', 'words'),
        ('E-1', 'CV word E_-1', 'direct state read', 'words'),
        ('classes', 'class table of the first-block family', cls + '; larger families (a) 2^27.. (b) (c) and "all 128" are in C0016/C0018/C0019', 'family'),
        ('a0', 'a0 family and the bijection W0..W5 <-> a0 (Lemma 4.1)', 'rows 0..3 are NOT free in the attack: W0..W5 are the bijective image of a0 and are solved from the row 4/5 conditions; |G| = 12,103,680 A0-variants (r37), 345,600 selected variants (r38)', 'family'),
        ('H1', 'H1 uniform independent chaining values F_%d(IV, M0)' % n, 'evidence in the filed proofs: r37 2^21 and 2^23 real first blocks (inherited) + 50,000 simulated + own 2^29 real; r38 29,360,128 real first blocks; a bias would be a LEVER, not only a risk', 'prem'),
        ('diff', 'characteristics with a NONZERO chaining-value difference', 'first block leaves a near-collision, second block absorbs it; the universe fixes dCV = 0 at rows -4..-1; real SHA-2 attacks used this shape', 'prem'),
        ('BLKn', 'block count and layout of the colliding messages', 'M0||M1 and M0||M1\' (128 bytes) + one equal FIPS padding block = 3 compressions; alternatives: difference block as block 3 of a longer message, free extra block between', 'blk'),
        ('BLK3', 'third block / extra free block', 'cost model: padding block has equal CV in both members, one extra compression only on a hit', 'blk'),
        ('PADlen', 'padding and length words W14/W15', 'FIPS 180-4 padding of the 128-byte message sits in block 3 (W14, W15 = 0, 1024); supports with dW14 = dW15 = 0 could end in block 2 (support choice itself belongs to G03)', 'blk'),
        ('OUTfold', 'end of the chain: feed-forward and digest', 'CV_in is equal in both members, so the digests are equal iff A%d..A%d and E%d..E%d are equal; the profile forbids truncation (all eight digest words)' % (last - 3, last, last - 3, last), 'blk'),
    ]


def build_g04():
    cells = []
    for h in SHA256:
        cells += _expand(h, 'G04', 'cv', 'CV', ('Q1', 'Q2', 'Q3', 'Q4'), g04_items(h))
    return cells


# ------------------------------------------------------------------------------------------------------------------ G05 objects
B3_INIT = [
    ('v0', 'state word v0 = h[0] (chaining value)', 'IV[0] for the first block of a chunk; the multi-block chunk alternative has h = previous output (door 6 covers h = IV only; door 37 prices a fresh CV per context at 0.007-0.1 bit)', 'h'),
    ('v1', 'state word v1 = h[1]', 'IV[1]', 'h'),
    ('v2', 'state word v2 = h[2]', 'IV[2]; K = IV[2] + IV[6] enters the K2 length cancellation', 'h'),
    ('v3', 'state word v3 = h[3]', 'IV[3]', 'h'),
    ('v4', 'state word v4 = h[4]', 'IV[4]', 'h'),
    ('v5', 'state word v5 = h[5]', 'IV[5]', 'h'),
    ('v6', 'state word v6 = h[6]', 'IV[6]; K = IV[2] + IV[6]', 'h'),
    ('v7', 'state word v7 = h[7]', 'IV[7]', 'h'),
    ('v8', 'state word v8 = IV[0]', 'constant of every compression', 'iv'),
    ('v9', 'state word v9 = IV[1]', 'constant of every compression', 'iv'),
    ('v10', 'state word v10 = IV[2]', 'constant of every compression', 'iv'),
    ('v11', 'state word v11 = IV[3]', 'constant of every compression', 'iv'),
    ('v12', 'state word v12 = t_lo (chunk counter low)', 'root compression of a single chunk uses counter 0; counter classes / ctr_class transfer (r1 line R1C) and chunk index t >= 1 are the alternatives', 'ctr'),
    ('v13', 'state word v13 = t_hi (chunk counter high)', 'counter 0', 'ctr'),
    ('v14', 'state word v14 = block_len b', 'b = 55 or 63 (XOR 8) in the record; K2.q1 is the only round-0 call that reads v14 (Lemma L); other length pairs and their digest pins (door 24)', 'ctr'),
    ('v15', 'state word v15 = flags d', 'CHUNK_START | CHUNK_END | ROOT = 1 + 2 + 8 = 11; flags 11 vs 12 differs by delta 7 (door 21: re-enters round 1 as y-difference at column 0, 8 conditions = 256-bit residual, CLAIMED-UNTESTED)', 'ctr'),
]
B3_PIN = [
    ('X3', 'pin X3 = 29d4fa98 (state word 3 after round 0)', 'forced constant of D0-D3; input a of C3 (Fact P: equal d and b outputs for w4 = W4 vs W4\')', 'pin'),
    ('X7', 'pin X7 = bee3af28', 'input b of C3', 'pin'),
    ('X11', 'pin X11 = 44036000', 'input c of C3', 'pin'),
    ('X15', 'pin X15 = 40c58500', 'input d of C3', 'pin'),
    ('w4', 'pin w4 = W4 = 97475638 (and W4\' = W4 + 8 by the K2 rule)', 'pinned word, 32 of 32 bits fixed; the B3 record has these as map cells m4', 'pin'),
    ('w13', 'pin w13 = W13 = 0007c006', 'pinned word, exactly 1 of 2^32 values gives equal d and b at C3', 'pin'),
    ('K', 'cancellation constant K = IV[2] + IV[6] = 5bf2cd1d', 'w4\' = ((K + w4) XOR 8) - K and w5\' = w5 + w4 - w4\' make K2 leave the same four words for both messages', 'pin'),
]
B3_OUT = [('d%d' % i, 'digest word %d = Z[%d] ^ Z[%d]' % (i, i, i + 8),
           ('pinned by E0/E2 (identical inputs, Fact P); words 0,2,5,7' if i in (0, 2, 5, 7) else 'residual from E1/E3 (words 1,3,4,6; E1 key XOR E3 key, word by word)'), 'out') for i in range(8)]
B3_OUT.append(('hi', 'second root half v[i+8] ^ h[i] (not in the digest)', 'FACT profile: the digest is the first 32 bytes of the root output; the second half is not required; no longer output is in the profile', 'out'))
B3_MODE = [
    ('single', 'single-block root compression (current record)', 'chunk counter 0, flags 11, b <= 64; the record', 'mode'),
    ('first', 'first block of a multi-block chunk', 'CHUNK_START, h = IV; door 45 (224-bit near-collision first block ~2^64, CLAIMED-UNTESTED)', 'mode'),
    ('mid', 'middle block of a multi-block chunk', 'h = previous block output, free per block: redraws constants (door 37: fresh CV per context costs 0.007-0.1 bit, CLAIMED-UNTESTED)', 'mode'),
    ('last', 'last block of a multi-block chunk', 'CHUNK_END; the filed B3V uses a last-chunk half-collision with a counter search (tree lemma: the last chunk decides the digest)', 'mode'),
    ('ctr', 'chunk index t >= 1 (counter state words)', 'counter classes; r1 filings R1C; door 37/38 context', 'mode'),
    ('parent', 'parent compression (flags 4 + 8, b = 64, left||right CV)', 'door 3 (>= 8 word conditions = 256 bits for all 65,535 parent patterns, CLAIMED-UNTESTED), door 23 (CV/tree differences, none below 63.6), door 38 (separability bias, smoke only)', 'mode'),
    ('tree', 'tree shapes with more than one compression pair', 'Opus cloud job 2 gave no report on disk; door 3 scope excludes it', 'mode'),
    ('len', 'length pair (55, 63) and other legal pairs', 'XOR 8; legal 55/63 family has exactly 4 digest pins (door 24); other pairs open', 'mode'),
]
B3_DOORS = [
    ('d21', 'door 21: flag-word cancellation (delta 7 for flags 11 vs 12)', 'RELABEL test: word-level simulation of delta 7 through round 1, count the active G calls (claimed: touches all four diagonals, 8 conditions = 256-bit residual; Trail SAT cells UNKNOWN)', 'door'),
    ('d22', 'door 22: two structural differences cancelling each other in round 1', 'RELABEL test: own enumeration of in-call absorption on reachable clean states (claimed: smallest legal-meeting residual 256 bits, 0 solutions of full in-call absorption)', 'door'),
    ('d24', 'door 24: force more than 4 digest words by construction', 'RELABEL test: own bijection check on E1/E3 inputs over a sampled outer step (claimed: legal 55/63 family has exactly 4 digest pins, 2^243 pairs; k = 5/6 and cross-step product families OPEN)', 'door'),
    ('d37', 'door 37: fresh CV / prior block per context (mode lever)', 'RELABEL test: ledger arithmetic with all measured levers stacked (15 min); claimed cost 0.007 to 0.1 bit', 'door'),
    ('d38', 'door 38: parent/CV separability bias at 2 rounds', 'RELABEL test: RELAX 2/4 at N = 2^24 (smoke max bias 0.0018, 3.6 sigma, 1 of 256 bits)', 'door'),
    ('d45', 'door 45: chaining-value route via a 224-bit near-collision first block', 'RELABEL test: none given (low value); claimed ~2^64 (BLAKE3_2ROUND_MAP section 5)', 'door'),
]
B3_CALLS_RD = ['K0', 'K1', 'K2', 'K3', 'D0', 'D1', 'D2', 'D3', 'C0', 'C1', 'C2', 'C3', 'E0', 'E1', 'E2', 'E3']
# the two message reads of every G call: m_x is read at quarter-step q1, m_y at q3.  Words per call: GRID_BLAKE3 / BLAKE3 definition
# (round 0 reads m0..m15 in order, round 1 in the permuted order 2 6 3 10 7 0 4 13 1 11 12 5 9 14 15 8).
_PERM = [2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8]
_ORD = list(range(16))


def b3_reads():
    out = []
    for r, order in ((0, _ORD), (1, _PERM)):
        calls = B3_CALLS_RD[0:8] if r == 0 else B3_CALLS_RD[8:16]
        for gi, call in enumerate(calls):
            mx, my = order[2 * gi], order[2 * gi + 1]
            out.append((call, 'x', mx))
            out.append((call, 'y', my))
    return out


def build_g05():
    h = 'blake3-r2'
    cells = []
    cells += _expand(h, 'G05', 'b3init', 'INIT', ('Q1', 'Q2', 'Q3', 'Q4'), B3_INIT)
    cells += _expand(h, 'G05', 'b3pin', 'PIN', ('Q1', 'Q2', 'Q3', 'Q4'), B3_PIN)
    cells += _expand(h, 'G05', 'b3out', 'OUT', ('Q1', 'Q2', 'Q3', 'Q4'), B3_OUT)
    cells += _expand(h, 'G05', 'b3mode', 'MODE', ('Q1', 'Q2', 'Q3', 'Q4'), B3_MODE)
    cells += _expand(h, 'G05', 'b3door', 'DOOR', ('D1',), B3_DOORS)
    for call, xy, w in b3_reads():
        cells.append(gc(h, 'G05', 'b3msg', 'MSG.%s.%s' % (call, xy), 'MSG', 'Q1',
                        'read %s of call %s = message word m%d (%s)' % (xy, call, w, 'step q1 (mx)' if xy == 'x' else 'step q3 (my)'),
                        'one cell per (round, G, position) so a word\'s two uses are visible; the word cells m%d merge them' % w, 'msg', word=w, call=call))
    return cells


# ------------------------------------------------------------------------------------------------------------------ G06 objects
SHA3_MSG = [
    ('len', 'message length and padding byte', 'ONE 135-byte block, byte 135 = 0x86, pad10*1 with domain byte 0x06 (SHA3R6_MAP); alternatives: shorter message (more fixed padding bytes), 2 blocks', 'msg'),
    ('blocks', 'block count', '1 block; "obstruction 1 (PROVED): the first block breaks at r = 6" because the reduced permutation also runs on the first block, so a prepared capacity is impossible; 2-block routes (HR2) are recorded in sol_answer_HR2_r6_two_block.md', 'msg'),
    ('cap', 'capacity lanes at the input of round 0', 'capacity = 512 bits = 0 at the input of round 0 (first block absorbed into the zero state): structural help for r5 and r6', 'msg'),
    ('free', 'free message bits', '1,080 free bits in the 135-byte format (512 in the 64-byte format); the rate is 1,088 bits', 'msg'),
]
_DIGF = 'digest = lanes (x,y) = (0..3, 0) of the final state: 256 of 1600 bits; r5 "4 of 5 bits per plane-0 row", r6 key = digest lanes at z in KEEP (140 bits). Aggregate records over the four lanes exist (r5 ATLAS_SHA3 round-4 chi; r6 round4.chi Q1/Q2, cone of the 140-bit key): this cell asks the PER-LANE split'
SHA3_DIG = [
    ('l0', 'digest lane (0,0)', _DIGF, 'dig'),
    ('l1', 'digest lane (1,0)', 'as lane (0,0): per-lane split of the aggregate records', 'dig'),
    ('l2', 'digest lane (2,0)', 'as lane (0,0): per-lane split of the aggregate records', 'dig'),
    ('l3', 'digest lane (3,0)', 'as lane (0,0): per-lane split of the aggregate records', 'dig'),
    ('dc', 'don\'t-care final state (1,344 bits)', 'lanes outside (0..3,0) of the final state do not enter the digest', 'dig'),
]
SHA3_ROW = {
    'sha3-r5': [
        ('F520', 'round-0 chi connector: 520 fixed F bits', 'F fixed bits = 520 exactly (rank 520 in E_D and E_M); C0104', 'row'),
        ('EDzero', 'round-0 chi: E_D zero-difference rows', '2-13 (mean 6.9) inactive alpha1 rows, E_D rank gain 10-65', 'row'),
        ('M2M3', 'round-0 linearised row masks M2 / M3', 'M2 adds E_M rank 884-908, M3 linearisation 13-35; DF after F+M2+M3 = 157-173', 'row'),
        ('M4', 'round-1 linear conditions M4 (59 rows)', '127 conditions in all 7 beta1 candidates, independent rank gain 117-125 (so 2-10 of the 127 are dependent); C0107', 'row'),
        ('FES24', 'round-2 FES equations (24)', 'the 24 printed equations are what the event needs (ATLAS_SHA3); SHA3-D180-ANF-CONSTRUCTOR50: 1,200/1,200 equations nonconstant over 50 constructor spaces', 'row'),
        ('DF33', 'connector freedom DF: 33 needed vs 33-53 reached', 'final DF = 1600 - rank(E_M after M4): 33-53 (mean 42.9), min 33 = the threshold; C0108', 'row'),
        ('DIG45', 'round-4 digest rows (4 of 5 bits per plane-0 row)', 'DDT[q][0] + DDT[q][16], branching over the 10 allowed digest-row values; event-exact', 'row'),
        ('S1SPLIT', 'E stage-1 split (24 equations, degree 4, 32-dim window)', 'R5-E1 OPEN: safe online part 0.024 bit, G2 part 0.36 only if judges accept repricing', 'row'),
    ],
    'sha3-r6': [
        ('PRE128', 'round-1 prefix conditions (4 per z-bit, 128 in all)', '128 affine conditions, rank 128, on the message; C0112-C0115', 'row'),
        ('PRE312', 'prefix conditions through chi2 (312 independent affine conditions on 1080 bits)', 'lane16 msg bytes 56 + L8=0 64 + L5 64 + L15 64 + L12 64; rank 312, 768 free; C0117-C0120', 'row'),
        ('ZCOUNT', 'z counter (32 z-directions XORed into lanes 4 and 14)', 'E_j with disjoint supports, 22-word z-flip footprint; 2^32 z per group; C0114, C0124', 'row'),
        ('KEY140', '140-bit key = digest lanes 0..3 at z in KEEP', 'cone from the key: chi5 inputs 175, chi4 outputs needed 1505 (301 columns x 5)', 'row'),
        ('KEEP35', 'the KEEP set of 35 planes', 'the leader z-set is unpublished: z = 0..34 is a reading, contiguous 29 planes gives 1362 (leader 1363); R6-KEYW (key width b >= 141) OPEN', 'row'),
        ('FREE132', '132 free key bits (140-bit key minus the 8 filter bits)', 'reading to verify: the key keeps 140 digest bits, 8 of them are the filter; 132 free bits drive the Gray-order birthday', 'row'),
        ('FORMS8', 'r6 filter: 8 digest-determined bits (z = 0,1, lanes 0..3), 8 XOR-forms of degree 8', 'width ledger k = 7 21.25 / k = 8 20.80 / k = 9 23.77; deg6.py: all 8 forms have degree exactly 8', 'row'),
    ],
}
SHA3_STAGE = [
    ('PRE1', 'prefix chi1 affine (z-flip, 22-word footprint)', 'part of the prefix; no separate ops figure in the ledger', 'stage'),
    ('CHI2', 'chi2 patch + theta3', '7.30 ops/message (499 patched words)', 'stage'),
    ('CHI3', 'chi3 block (chi3 + theta4 parities)', '53.30 ops/message; 273 of 320 rows change per Gray step', 'stage'),
    ('CONE4', 'round-4 cone of the 140-bit key', '46.11 ops/message; 1363 of 1600 theta5 words', 'stage'),
    ('CONE5', 'round-5 cone', '2.19 ops/message (not reproduced in the round4.chi Q1 record)', 'stage'),
    ('R6L', 'round 6 on 35 planes', '3.12 ops/message', 'stage'),
    ('TRANS', 'transpose', '14.32 ops/message', 'stage'),
    ('PROBE', 'probes', '6.00 ops/message; the sum of the blocks 132.44 vs the stated 124.62 (SHA3R6_MAP lines 34-35 flag the mismatch)', 'stage'),
]


def build_g06():
    cells = []
    for h in ('sha3-r5', 'sha3-r6'):
        cells += _expand(h, 'G06', 'sha3msg', 'MSG', ('Q1', 'Q2', 'Q3', 'Q4'), SHA3_MSG)
        cells += _expand(h, 'G06', 'sha3dig', 'DIG', ('Q1', 'Q2', 'Q3', 'Q4'), SHA3_DIG)
        cells += _expand(h, 'G06', 'sha3row', 'ROW', ('Q1', 'Q2', 'Q3', 'Q4'), SHA3_ROW[h])
    cells += _expand('sha3-r6', 'G06', 'sha3stage', 'STAGE', ('Q1', 'Q2', 'Q4'), SHA3_STAGE)
    return cells

# ------------------------------------------------------------------------------------------------------------------ G07 objects
# PREM = the heuristics / premises each filed (or staged) proof declares; LEDGER = the exact op-ledger rows of the filed line;
# JUDGE = causes of NOT_EVALUABLE / REFUTED rulings seen on that line (FILINGS.md), one cell per cause so a package is checked first.
G07_PREM = {
    'sha256-37': [
        ('H1', 'H1 uniform independent chaining values (score-critical)', 'CV1 = F_37(IV, M0) uniform, x = A_-1 independent of cb; evidence 2^21 / 2^23 real first blocks (inherited) + own 2^29 + 50,000 simulated', 'prem'),
        ('H2', 'H2 q3 = 2^-71.47 for the four patterns + R16x event (score-critical)', 'prereg 128 + 128 reps NP 8192, 99% Student LB 2^-71.4629; one bit lower = 61.57158; inherits 7319bba estimator', 'prem'),
        ('H3', 'H3 multiplicity E[X_f - 1 | A_t] <= 2^-9.4 (score-critical)', 'part (a) other l with the same variant <= 2^-11, part (b) <= 2^35 x; thin margin (measured ~2^-9.68 per the critic); inherited replay of 19,620,436 successes', 'prem'),
        ('H4', 'H4 advice allowances A_C 2^60, A_S 2^50, DEV 2^40 (supporting)', 'A_C = 688,000 x the measured 35-step re-run; policy rows of the tightening audit', 'prem'),
        ('H5', 'H5 word-RAM plane-program pricing reading (score-critical)', 'plane programs executed and counted by lowm.py; 166 / 404-431 primitives', 'prem'),
        ('H7', 'H7 success floor: mu0 = 0.49558494, Pcap = 0.00056206 (supporting)', 'mu0 from -ln(0.61 - Pcap - 2^-60)/(1 - 2^-10.4); caps A_C 2^60, A_S 2^50, DEV 2^40; Bernstein cap lever S37-CAP', 'prem'),
        ('SMC', 'resampling correlation of the SMC q3 estimator', 'sequential Monte-Carlo with resampling: the reported SE assumes independent reps; correlation across particles unmeasured', 'prem'),
    ],
    'sha256-38': [
        ('H1', 'H1 uniform independent chaining values (score-critical)', 'exact distribution of passing classes over all 2^32 values of A_-1 + 29,360,128 real first blocks', 'prem'),
        ('H2', 'H2 q3_model = 2^-97.7838 (score-critical)', 'product of two Monte-Carlo lower bounds: base 2^-101.35 (own replicate -101.025) x preregistered gain +3.3216', 'prem'),
        ('H3', 'H3 few other row-16 passes, 2^-8.5 (score-critical)', 'own repetition: 33,222 successes, 8 runs, one-sided 99% bound 2^-9.85; not re-measured for the accepted event', 'prem'),
        ('H4', 'H4 advice allowances A_C 2^78, A_S 2^74, DEV 2^64 (supporting)', 'A_C = 2^84 gives 87.99563; H4a/H4b/H4c split', 'prem'),
        ('H4A', 'H4a characteristic-search allowance (the dense characteristic derivation)', 'dense characteristic NOT derived (4 solvers x 2 h UNKNOWN); judged NOT_EVALUABLE on R38N / R38E / R38C', 'prem'),
        ('H5', 'H5 bit-sliced pricing of the filter (score-critical)', 'programs generated and counted by a0lean38.py; scalar evaluation would be +2.79 bits; D7 delta7 0.293', 'prem'),
        ('H6', 'H6 memory 1,045,792 B (score-critical under the rule)', 'code counted at 32 B/instruction; 2,784 B under 2^20', 'prem'),
    ],
    'sha3-r5': [
        ('P', 'premise P: trail search (T1/T2/T3) finds the cores the proof states', 'premise P (2.1); mitm2.c certified at level 6; 1741 cores, 467 kept', 'prem'),
        ('R7', 'R7 selection charge (K-ladder)', 'R7 uncharged was REFUTED (lane_cost/F1-r7-selection-work-omitted); R7 now charged in the lineage', 'prem'),
        ('CAPS', 'outcome-informed caps X_MAX / A_MAX / B_TRUE / coin words', 'caps set from the largest value seen in the runs they bound are the refused class', 'prem'),
        ('PREPROC', 'preprocessing versus online split of the connector primitives', 'e1317b6a REFUTED: preprocessing bound deducted 23.2e9 online-connector primitives it does not contain', 'prem'),
        ('PAIR', 'H_pair(q) over distinct survivors replaces Hkey / H_M', 'F = 3 x 2^136 < M so every message could get its own key; replacement premise gives 101.5967 at q = 1/M, Htrail 2^-18.0069', 'prem'),
        ('SUCC', 'success probability 0.4 and the 16 certificates', 'success_probability 0.4 in the claim; R7 runs 39 labels', 'prem'),
    ],
    'sha3-r6': [
        ('HCOSET', 'H_coset probability space', 'generator random signatures; probability_space_defined / evidence_relevant were the NOT_EVALUABLE causes of f1346045', 'prem'),
        ('HK', 'H_K independence of the coset records', 'no organizer-run experiment for the independence; per-list H_K used for adaptively selected lists was REFUTED (3433434e)', 'prem'),
        ('SURV', 'survivor mean E[S_r | D] <= S', 'F-SURVIVOR-MEAN-MISSING (6c60fdf7 REFUTED); retried 32a0fc84 PASSED', 'prem'),
        ('FLOOR', 'success floor 0.39: Chernoff terms F1..F4, kappa = 17, U = 10,000', 'F1 + F3 + F2 + F4 failure terms; D166 variant F1 = 0.000352, F3 = 0.000746', 'prem'),
        ('CAPS6', 'trail caps Lc, ONCE 2^70, replay overcharge', 'checklist item 9: do not move a fifth decimal unless within 1e-5 of the rounding boundary', 'prem'),
    ],
    'blake3-r2': [
        ('H1P', "H1' dependence clause (ii) / rho <= 3,071", 'fa761365 and 1a92bf64 NOT_EVALUABLE on H1\'(ii); fallback with a proved bound passed (848bcd76)', 'prem'),
        ('H4P', "H4' advice record (68 bytes) and its construction SEL", 'S_old = 4.859e18 operations charged for 116 solver calls; one pair needed', 'prem'),
        ('H5E', 'H5_exec / H5_screen: U = U0 - 410 exactly', 'credit restated on U; 0.9734 of U0 charged', 'prem'),
        ('HG', 'H_G_cluster: fills F of the shipped walk', 'prereg b3m_F: mean F 7159.266 on 2^24 contexts vs the old-walk premise 12,433', 'prem'),
        ('HPF', 'H_PF class filter (prefilter factor)', 'B3V prereg run passed; B3W prereg 1.01361 SE 0.01033 missed the 6-SE rule at 16,384 contexts (PREREG6W2 at 2^18 running)', 'prem'),
        ('HCL', 'H_class: 16 member classes behave alike', 'only 2 of 15 class-toggle directions proved; D179 exhaustive audits of the residual toggles', 'prem'),
        ('MU', 'MU mean metered debit per step and the 0.974 factor', 'prereg_b3_MU_result: 4352 millionths measured, declared 4425; FACTOR 0.974', 'prem'),
    ],
}

G07_LEDGER = {
    'sha256-37': [
        ('AC', 'A_C characteristic-search allowance (2^60)', 'filed R37X ledger (xtab.py): policy row 1 of the leader audit, any value 2^52..2^58 as defensible; 44% of T', 'led'),
        ('AS', 'A_S + DEV allowances (2^50, 2^40)', 'A_S 2^8.7 x the paper; DEV exact', 'led'),
        ('NFB', 'N_FB first-block compressions, mu0 8-decimal rounding, ceil', 'filed R37X: cap target mu0 and the success floor', 'led'),
        ('FIXED', 'FIXED operations per first block (264 in the filed R37X ledger; 615 in the staged R37M3)', 'field extraction 28 of 30 first-block ops, control 16 vs 8 itemised, cv_pre kap0 16 vs 14', 'led'),
        ('W6T', 'W6 fibre test (230 ops in the filed ledger)', 'matches w6_batch (assert) in the leader audit', 'led'),
        ('GBODY', 'group body 31 ops and lookup 14 per group', 'recounted line by line against packed_u', 'led'),
        ('SEGOV', 'SEG_OVH 6, SCAN_LANE 6, chunk_fixed_ops, LOOP_SEG', 'executed counts', 'led'),
        ('BATCH', 'batch count bound ceil(F/256) with 333 per batch; z-plane reload 63 per batch', 'about 1,931 ops/fb charged vs E[ceil] = F/256 + 0.5; reload ~365 ops/fb', 'led'),
        ('RARE', 'rare path: ROWCHECK 53 re-check, tail rows past row 17, hit rate R16F', 'about 108 + 12 + 5 ops/fb', 'led'),
        ('VMAX', 'V_MAX, Pcap via Chebyshev and the slack s', 'E[v^2] about 1.5e11 vs the used 1.41e17; Bernstein cap lever S37-CAP', 'led'),
        ('THETA', 'THETA = 40 (parameter choice)', '56 gives 61.17737', 'led'),
        ('PRE37', 'PRE (2^58 in the audited ledger, section sums to 2^57.6) and FIN, +6, DEV rounding', 'each below 1e-9 relative except DEV', 'led'),
        ('LM3', 'staged R37M3 lowm.py ledger (615 fixed + 46,070.09 data-dependent ops)', 'class scans 21.14, passing classes 24,666.75, groups 16,269.77, survivors 4,879.12, row-16 hits 233.31; V_MAX, vmax_fb; NOT audited yet', 'led'),
    ],
    'sha256-38': [
        ('PRO38', 'prologue (91 -> 89 ops in the shaves)', 'filed R38E fdef4bab (vt38.py lineage): shares abx; nabx = abx ^ M', 'led'),
        ('GRP4', 'GROUP4 (76 -> 75)', 'folded -K1 + 2 and the 3<<32 bias into nsb; works only if the header index is Z0<<32 | Y', 'led'),
        ('A17I', 'A17 internal (60 -> 58)', 'equality pairs (9,20), (6,18), (8,17) compared with one bne', 'led'),
        ('DEEP', 'deep path (3148 -> 3142)', 'masks on S0A1, S0A2, E5 dropped; W7x = W7 & M', 'led'),
        ('EPI', 'epilogue (19 -> 13)', 'OR the four rsub results, one shr 255 and one bnz', 'led'),
        ('P6B', 'P6 table build (count / fill) and the header layout', 'header layout mismatch Y-major vs Z0-major: +0.00037 bit on the rival; the counted preprocessing writes HB + (Y << 32 | Z0)', 'led'),
        ('NG38', 'N_G pair budget at the measured 99% limit of the base and the D7 pairs-in-group', 'delta7 = 0.293 (99% CP 0.305), ledger -0.110', 'led'),
        ('PREP38', 'preprocessing executed counts', 'lean derivative with executed preprocessing counts', 'led'),
        ('ALLOW38', 'allowances A_C 2^78, A_S 2^74, DEV 2^64', '2^-13.1 of T together; A_C = 2^84 gives 87.99563 on R38M3', 'led'),
        ('CAP38', 'cap margin 2^-16 / Bernstein analogue', 'S38-CAPan: dead < 1e-5 bit', 'led'),
        ('LM3', 'staged R38M3 a0lean38 ledger (35 fixed + vbar 132,300.19)', 'W7 tests 1497.66, hit list 12.041, scalars and planes 278.94, plane programs 128,796.72, passing lanes 1714.34, row-16 passes 0.4873; V_MAX, vmax_class; NOT audited yet', 'led'),
    ],
    'sha3-r5': [
        ('CONNW', 'connector coin words', '4268 x 2^15 words x 2^9 prim charged vs 64 prim per draw (S5T)', 'led'),
        ('XMAX', 'connector X_MAX and A_MAX caps', '2^20 work units x 96 vs R7 largest attempt 197,334; outcome-informed', 'led'),
        ('BPT', 'B-prime B_TRUE and the true B-prime cost', '2^29 units; prereg_r5T_bprime_true (WK vs true)', 'led'),
        ('SETUP5', 'S, P setup, bases, E setup (2^31 / 2^32 / 2^24 / 2^23)', 'S 8.6e9 prim vs 5.86e7 measured', 'led'),
        ('EST1', 'E stage 1 block (207,920 / 410,392 counted primitives)', 'no unused op found', 'led'),
        ('EST2', 'E stage 2 (50 x 2^11 pairs)', 'S2CAP 2^11 vs R7 max 310', 'led'),
        ('MATCH', 'match step 49 + filter 31 (T3 half-sum match) and the T2 export', 'D19 / Z.4 charge 49 + 31 for every match; contig.c filter unverified', 'led'),
        ('SORT5', 'sort and merge 37 per half vector per block', 'stated bound with no counted program', 'led'),
        ('D20', 'D20 replay test (39 replays) and G2 attempts (2,176 at the 2^18 cap)', 'B-prime attempt at WK vs true cost; 751 attempts actually run', 'led'),
        ('KEYW5', 'key-words row (d): 17 vs 14 vs 19 key words', 'rival 6938d3fb prices 17 key words vs 14 / 19 built; sensitivities: row (d) with 17 and 21 words 32.83428, left out 32.83852', 'led'),
        ('PROC5', '2^31 per-process / module-load allowance (50+ processes)', 'D20, D22..D25, Z.8', 'led'),
    ],
    'sha3-r6': [
        ('PERM6', 'S6R generic line: permutation rounds (1626 = 6 x 271, rotation cost k = 5)', 'round 5 last returns only lanes 0..3 (-183 per eval); round 0 specialised (-46)', 'led'),
        ('ENC6', 'encoding: 21 constant sets + 4 moves', 'folds into immediates when round 0 is specialised', 'led'),
        ('CNT6', 'counter 3 ops per eval and the cap check', 'unrolled body: 3/u', 'led'),
        ('REPL6', 'replay of the stored trail (4 Lc vs 3 Lc)', 'storing the length: 96-byte slots, -0.00299', 'led'),
        ('FORMS6', '8 XOR-forms (10 planes + 33 ops)', 'R6-8FORMS: 121.8701; r6_8forms_verify HOLDS', 'led'),
        ('BATCH6', 'batch kernel row (44%) and the coset-specialised survivor kernel S6K', 'R6-COSET 0.148 after the survivor-mean fix', 'led'),
        ('FES6', 'FES key packing (4 slots in 3 words, T = 36)', 'R6-FESKEY KILLED: lower bound +0.0011, best packing T = 39', 'led'),
        ('KEY6', 'key width b = 140 and the parameter neighbourhood', 'R6-PARAM KILLED (elasticities < 0.01); R6-KEYW OPEN (b = 141..144 benefit side only)', 'led'),
        ('RARE6', 'rare path R (1.23e9, 2^-90 of N), DP prefilter 2 ops, ONCE 2^70 + 16', 'S6R audit item 9: no real slack', 'led'),
    ],
    'blake3-r2': [
        ('CTX', 'context rows: (436 + 7 + U_MEMBER 71 x 8 members) per context', 'B3-CTX436 (500 -> 436); fixed name store = 1 op', 'led'),
        ('BLK', 'block rows (u_block 9 x 16 blocks)', 'boundary words 186 -> 115 (B3-BND115)', 'led'),
        ('WORD', 'word row (u_word 45-48 across the lineage, 46 in B3V; test 3, prefilter 7) and boundary / partial words', 'WB 83% of N on the older ledger; scan 21 -> 12 (B3-SCAN12)', 'led'),
        ('LIVE', 'live-block setup, pieces, wrap, ranges', 'u_live = setup 21 + piece 10 x 16 + wrap 0 + 19 x 16', 'led'),
        ('PASSL', 'passing lane (u_pass 39 + 1 + 12)', 'shortcut 31 -> 27 in the older audit', 'led'),
        ('WCTX', 'per-context words and the descriptor table', 'descriptor table 48,896 -> ~5,760 in the older audit', 'led'),
        ('CREDIT', 'solver credit (MU millionths, capx, 14 L_C)', 'MU 4459 declared; credit 6.7% - 25.8% of N depending on line', 'led'),
        ('ONCE3', 'ONCE row (1.13e15) and BUILD of the 16 class lists (8.34e14)', 'exact event counts', 'led'),
        ('SOLD', 'S_old: 116 pinned solver calls charged at 5 x 2^53 + 2^51', 'B3-SOLD: charged at logged maxima 9010.5 s -> -0.012 bit', 'led'),
        ('FINAL3', 'final: (430 + 64) x 2 + final_per_chunk x 2^48 + 430 x 2^38', 'final_per_chunk 128', 'led'),
        ('SPREC', 'sample-size and rounding terms (RUN_CONTEXTS, S reserve, FACTOR 0.974)', 'B3-F974 0.97 -> 0.974', 'led'),
    ],
}

G07_JUDGE = {
    'sha256-37': [
        ('JH1H3', 'NOT_EVALUABLE: H1 uniform CV + H3 first-block dependence (b43280d0, b74a016c)', 'inherited premises of a passed parent; reviewer variance; "multiplier not stratified by kept-fibre W7 law, CP overdispersion"', 'judge'),
        ('JH2', 'NOT_EVALUABLE: H2 variant Step-3 probability, H9 table statistics', 'b74a016c', 'judge'),
        ('JSTALE', 'stale ledger values / stale sentences in a re-staged package', 'R37M3 "stale H5 sentence" fixed by hand', 'judge'),
        ('JMARGIN', 'evidence-size and experiment-time margins', 'B3V failed pre-judge on 84 B / 14.5 s of 20 s; R5T2 218 B and 12.06 s; limits 64 KiB sources, 10 s', 'judge'),
    ],
    'sha256-38': [
        ('JH4A', 'NOT_EVALUABLE: H4a allowance-characteristic-search (R38E 1393e83b, R38N, R38C)', 'A_C now 82.8% of T on R38N; dense characteristic derivation unmeasured; split H4a/b/c passed on winglock', 'judge'),
        ('JGAIN', 'gain transfer and delta far-variant premise (R38N cfeb996a)', 'stale values, gain transfer', 'judge'),
        ('JSTALE', 'selftest transcript GROUP4 = 84 vs claimed 80; ledger38.py common eps 2^-4', 'material of 1393e83b', 'judge'),
        ('JMARGIN', 'evidence-size and experiment-time margins', 'as r37', 'judge'),
    ],
    'sha3-r5': [
        ('JK', 'REFUTED: R7 selection work omitted (R5P 2b6ade9c)', 'lane_cost/F1-r7-selection-work-omitted', 'judge'),
        ('JPREPROC', 'REFUTED: F-PREPROCESSING-ONLINE-DEDUCTION (e1317b6a)', 'fatal; also 4,508 coin-word max not evidenced', 'judge'),
        ('JCAP', 'outcome-informed class of caps (refused)', 'GordoAR K = 36', 'judge'),
        ('JMARGIN', 'evidence-size and experiment-time margins (S5T2: 218 B, 12.06 s)', 'held until widened', 'judge'),
    ],
    'sha3-r6': [
        ('JANDNOT', 'REFUTED: F-ANDNOT-UNPRICED (S6N 84435675)', 'AND-NOT is not one primitive in collision-frontier-v5', 'judge'),
        ('JSURV', 'REFUTED: F-SURVIVOR-MEAN-MISSING (6c60fdf7)', 'Chebyshev around S without E[S_r | D] <= S', 'judge'),
        ('JHK', 'REFUTED: F-HK-ADAPTIVE-INFERENCE (3433434e)', 'per-list H_K used for adaptively selected lists', 'judge'),
        ('JPROB', 'NOT_EVALUABLE: probability_space_defined, evidence_relevant, H_K (f1346045)', 'generator random signatures; no organizer-run experiment for the independence', 'judge'),
    ],
    'blake3-r2': [
        ('JADV', 'REFUTED: lane_cost F1-unaccounted-advice-construction (5a08fffa)', 'SEL may return other constants / none; inherited lineage text', 'judge'),
        ('JDEP', 'NOT_EVALUABLE: H1\'(ii) dependence clause (fa761365, 1a92bf64)', 'fallback with a proved dependence bound passed', 'judge'),
        ('JMARGIN3', 'FAILED pre-judge: evidence margin 84 B and experiment 14.5 s of 20 s (B3V 896db2cb)', 'fixed to >= 8 KB and <= 9 s; PASSED on retry', 'judge'),
        ('JUNSUP', 'NOT_EVALUABLE: H1\', H4\', H5\' rated unsupported without an organizer-run statistic (b84873d8)', 'fix that worked: ship the scored search as the declared experiment', 'judge'),
    ],
}


def build_g07():
    cells = []
    for h in G07_PREM:
        cells += _expand(h, 'G07', 'prem', 'PREM', ('R1', 'R2', 'R3', 'R4'), G07_PREM[h])
        cells += _expand(h, 'G07', 'ledger', 'LEDGER', ('R1', 'R2', 'R3', 'R4'), G07_LEDGER[h])
        cells += _expand(h, 'G07', 'judge', 'JUDGE', ('R1', 'R2', 'R3', 'R4'), G07_JUDGE[h])
    return cells


def build_gap_universe():
    return build_g02() + build_g04() + build_g05() + build_g06() + build_g07()

# ------------------------------------------------------------------------------------------------------------------ mapping of existing records / files onto the new cells (critic step 1, no compute)
GMAP = {}


def _put(h, obj, loc, qs, spec):
    for q in qs.split():
        GMAP.setdefault((h, obj + '.' + loc), {})[q] = spec


def C(ids, why, files=''):
    """a record of ours in CELLS.jsonl (own_test, status in OWN_STATUS) answers the question; falls back to the files, else UNSCANNED"""
    return ('CELLS', ids.split(), why, files.split())


def F(files, why):
    """a result file / package section of our own code (pending ingest)"""
    return ('FILE', files.split(), why)


def ST(why):
    return ('STRUCT', why)


def EX(owner, why):
    return ('EXCL', owner, why)


def _many(h, obj, locs, qs, spec):
    for loc in locs.split():
        _put(h, obj, loc, qs, spec)


def _g02_map():
    # ---- sha256-37
    h = 'sha256-37'
    _many(h, 'MEM', 'T0 REC', 'M1', F(D126, 'D126 exact byte component of the filed table line (own exact arithmetic on the r37 table-line proof ledger)'))
    _many(h, 'MEM', 'T0 REC', 'M2 M3', F(D126, 'D126 shard model B = 2^k, exact n_FB and S at k = 0..32, best k = 5 (S 90.87 vs tight 91.46): exact price of cutting this region'))
    _put(h, 'MEM', 'R16T', 'M1', F(D126, 'D126 exact byte component 2^34 x 32 B'))
    _put(h, 'MEM', 'R16T', 'M2 M3', F(R37P + ' ' + D126, 'recompute instead = R37M3: two 4096-word chunk tables + 34-op exact test (proof 6.2), ledger 60.99099 at 607,744 B vs the table line S 91.46 (D126)'))
    for k in 'PLANES ENTRIES CUBE C7PL CHUNK SCANT PERL SCAL CODE REGS'.split():
        _put(h, 'MEM', k, 'M1', F(R37P, 'R37M3 proof 14.1 memory table, produced by lowm.py memory (607,744 B = 2^19.21)'))
    for k in 'F7 F6 G'.split():
        _put(h, 'MEM', k, 'M1', F(R37P, 'R37M3 proof 14.1 lists no resident table for it (straight-line test / plane program in the code, 222 descriptors 28,416 B)'))
    for k in 'F7 F6'.split():
        _put(h, 'MEM', k, 'M2', F(R37P, 'the shipped program IS the recompute: class test 166 primitives (F7), W6 plane test 404-431 per 256 reps (F6), priced in the ledger rows FIXED 397 / passing-class work'))
    # ---- sha256-38
    h = 'sha256-38'
    _many(h, 'MEM', 'SENT HDR P6T FIX38', 'M1', F(D126, 'D126 exact ledger bound of the r38d table line (formula W and fixed non-table terms)'))
    _many(h, 'MEM', 'HDR P6T', 'M2 M3', F(D126, 'D126 shard model, exact k = 0..45, best k = 19 (S 130.17 vs tight 132.39)'))
    for k in 'F7T PL90 SHC BCAST SPILL SCAL38 CTAB CODE7 CODEO PRE38'.split():
        _put(h, 'MEM', k, 'M1', F(R38P, 'R38M3 proof 14 memory table (1,045,792 B = 2^19.996)'))
    _put(h, 'MEM', 'F7T', 'M2', F(R38P, 'memory-free W7 test: the program recomputes it, 12.64 + 4 primitives per class (ledger W7 tests row)'))
    _put(h, 'MEM', 'PL90', 'M3', F(R38P + ' research/MERGE_FILING_PLAN.md', 'class count chosen against the 2^20 budget: R38M 91.20613 (64 classes) -> R38M3 87.90374 (90 classes), our builds'))
    # ---- sha3-r5
    h = 'sha3-r5'
    for k in 'PHALF PARR EVEC EANF EBUF'.split():
        _put(h, 'MEM', k, 'M1', F(D161, 'D161 exact allocation formula from the proof / program constants'))
    _many(h, 'MEM', 'EM1 EM50', 'M2', F(D152, 'D152: recompute the connector transcript instead of storing EM: <= 1067 x (2^20 x 96 + 2^15 x 512 + 2^22) = 129,784,348,672 primitives (S 39.81034, worse)'))
    _put(h, 'MEM', 'EM50', 'M3', F(D152, 'D152 best proved layout: stream one EM across a phase boundary, S 39.79188 (memory 27.0)'))
    # ---- sha3-r6
    h = 'sha3-r6'
    for k in 'BUF INPL RCT LIDLST ENDP SCR6 CODE6'.split():
        _put(h, 'MEM', k, 'M1', F(D166, 'D166 exact layout of S6DB: 25,600 code words + 7,168 data words = 1,108,384 B'))
    _put(h, 'MEM', 'ENDP', 'M2 M3 M4', C('R6-S6D', 'D166 exact repricing: S = U = 3,131 words brings memory to exactly 2^20 B at time 125.33206 (S 125.33206) vs S6DB 125.2774: the cut is 0.05466 bit worse; breakpoint priced on both sides', D166 + ' research/retest/s6d/d166_price.py'))
    _put(h, 'MEM', 'DPTAB', 'M1 M2 M3 M4', F(S6R, 'S6R audit item 6: store the trail length (96-byte slots, 979,200 B, total 1,046,784 B < 2^20) vs re-walk: -0.00299 bit; u = 4 unrolled code 211 KB borderline, declare 2^21 alternative'))
    # ---- blake3-r2
    h = 'blake3-r2'
    for k in 'T2G REPL PXF ROT BT SMALL CODE3 OUT3'.split():
        _put(h, 'MEM', k, 'M1', F(B3P, 'B3S2 proof 12 phase table (search phase < 2^42.45124, output phase < 2^43.00001), words of 32 B'))
    _put(h, 'MEM', 'SEL3', 'M1', F(B3MAX, 'b3m_maxphase: SEL peak 2^34 + 2^20 B, each program halts at 2^34 B, never co-resident with the search'))
    _put(h, 'MEM', 'OUT3', 'M3', C('B3-RELEASE', 'release the search tables before the output is written: S 86.19471 -> 85.43472 (BUILT pkgB3S2, skeptic CONFIRMED)', B3MAX))


def _g04_map():
    for h in SHA256:
        is37 = (h == 'sha256-37')
        if is37:
            _put(h, 'CV', 'A-1', 'Q1 Q3', C('S37-DB-P0FACTS', 'own recount: |F7| = 68,157,440, p7 = 2^-5.97763 (count of the gate and log2 of its size)'))
            _put(h, 'CV', 'A-2', 'Q1 Q3', C('S37-DB-P0FACTS', 'own recount: |F6| = 287,309,824, p6 = 2^-3.90197'))
            _put(h, 'CV', 'E-4', 'Q3', C('S37-J5-E4BUCKET', 'own test: row-16 pass rate per E_-4 bucket, 2^31 good pairs and 2^29 real first blocks, chi2 p = 0.035 / 0.91, bucket ratios 0.94..1.06 (steering of a CV word)'))
            _put(h, 'CV', 'classes', 'Q1 Q3', C('S37-DB-P0FACTS', 'own recount: 22,976 c7 classes (max 3600), 222 classes >= 3456 = 782,800 variants'))
            _put(h, 'CV', 'classes', 'Q4', C('C0016 C0018 C0019', 'own: dense-part families (a)/(b)/(c), enlarged family in the R37 ledgers, F8 set vs the W8 cell'))
            _put(h, 'CV', 'a0', 'Q1 Q3', C('S37-E17 S37-DB-P0FACTS', 'own: 12,103,680 A0-variants (cell + s0 F-set); |G| recount'))
            _put(h, 'CV', 'a0', 'Q4', C('C0015 C0016 C0019 C0023 S37-D183-W8UN', 'own: A1 family vs A0, other dense families, F8 set, W8 =un signing'))
            _put(h, 'CV', 'H1', 'Q1', C('S37-J5-E4BUCKET', 'own test on real first blocks: 2^29 real first blocks, good-pair rate 2^-9.8816 against the model; small N (2^29) - the 2^36 scale test is not done', R37P))
        else:
            _put(h, 'CV', 'A-1', 'Q1 Q3', F(R38P, 'R38M3 proof 5.1 / Appendix A.1-A.2 (fam38.c, hits38.c): exhaustive pass over all 2^32 values of A_-1: F7 count and the exact distribution of passing classes'))
            _put(h, 'CV', 'classes', 'Q1 Q3', F(R38P, 'R38M3 proof 5.3 / A.1: the c7 classes of G, 90 classes of 3840 variants, exact (fam38.c)'))
            _put(h, 'CV', 'H1', 'Q1 Q3', F(R38P, 'R38M3 proof 13.1 + A.2: 29,360,128 real first blocks (2^22 + 2^23 + 2^24) through the attack filters at 1.00 of the expectations; exact distribution over all 2^32 A_-1 (small N versus 2^86)'))
        _put(h, 'BLK', 'BLKn', 'Q1', ST('profile fact: two data blocks + one equal FIPS padding block = 3 compressions; recorded as the shape of the filed proofs'))
        _put(h, 'PAD', 'PADlen', 'Q1', ST('profile fact: FIPS 180-4 padding of a 128-byte message sits in block 3 with equal CV in both members'))
        _put(h, 'CV', 'OUTfold', 'Q1 Q2 Q3 Q4', ST('profile fact: CV_in is equal in both members, so the digests are equal iff the last four rows of A and E are equal (BEDROCK, S37-assign25 collision <=> equal after row 24 and dW26 = 0 on r37); no truncation is allowed, so no condition can be dropped and no alternative exists'))


def _g05_map():
    h = 'blake3-r2'
    for k in 'v0 v1 v2 v3 v4 v5 v6 v7'.split():
        _put(h, 'INIT', k, 'Q1 Q3', ST('profile fact: unkeyed BLAKE3-256, first block of a chunk: h = IV, fixed by the target, no freedom'))
    for k in 'v8 v9 v10 v11'.split():
        _put(h, 'INIT', k, 'Q1 Q2 Q3 Q4', ST('constant of every BLAKE3 compression (IV[0..3]): no difference, no condition, no freedom, no alternative'))
    for k in 'v12 v13'.split():
        _put(h, 'INIT', k, 'Q1 Q3', ST('profile fact: the root compression of a single-chunk message uses counter 0'))
    _put(h, 'INIT', 'v14', 'Q1', ST('value as used: b = 55 or 63 (XOR 8); stated by construction (BLAKE3_2ROUND_MAP 2.1, Lemma L)'))
    _put(h, 'INIT', 'v15', 'Q1 Q3', ST('profile fact: single chunk, single block, root: flags CHUNK_START | CHUNK_END | ROOT = 11'))
    # pins
    for k, qs_c, qs_d in (('X3', 'C0028', 'C0029'), ('X15', 'C0028', 'C0029'), ('X7', 'C0030', 'C0031'), ('X11', 'C0030', 'C0031')):
        _put(h, 'PIN', k, 'Q1 Q3', ST('pinned advice constant (Fact P): defined by construction, zero freedom (same reason as the C3 step cells)'))
        _put(h, 'PIN', k, 'Q2', C(qs_c, 'own: pin freedom per coordinate of C3 (all 2^32 values, others at the record): NECESSARY'))
        _put(h, 'PIN', k, 'Q4', C(qs_d, 'own: 64 (Y3, Y11) cells around the record, 8 realizable by Fact P'))
    _put(h, 'PIN', 'w4', 'Q1', C('C0056', 'own: w4 pinned, 32 of 32 bits fixed'))
    _put(h, 'PIN', 'w4', 'Q2', C('C0057', 'own: exhaustive 2^32 relaxation of w4 and w4p'))
    _put(h, 'PIN', 'w4', 'Q3', C('C0058', 'own: 0 bits of freedom; 2 values = one unordered pair'))
    _put(h, 'PIN', 'w4', 'Q4', C('C0059', 'own: carry pattern of the +/-8 step, exact'))
    _put(h, 'PIN', 'w13', 'Q1', C('C0084', 'own: one value of 2^32 passes the C3 condition set'))
    _put(h, 'PIN', 'w13', 'Q2', C('C0085', 'own: exact outcome mass over all 2^32 values of w13'))
    _put(h, 'PIN', 'w13', 'Q3', C('C0086', 'own: 0 bits'))
    _put(h, 'PIN', 'w13', 'Q4', C('C0087', 'own: no alternative; near misses 15 d-only, 29 b-only keep no digest word'))
    _put(h, 'PIN', 'K', 'Q1 Q3 Q4', ST('K = IV[2] + IV[6] is a function of the profile constants: nothing to count, no freedom, no alternative'))
    _put(h, 'PIN', 'K', 'Q2', C('C0057 C0061', 'own: the K2 rule gives w4p uniquely (C0057); exactly 1 of 2^32 w5p gives an equal K2 state (C0061, local)'))
    # output fold
    for i in (0, 2, 5, 7):
        _put(h, 'OUT', 'd%d' % i, 'Q1', C('C0040 C0042 C0044 C0046', 'own: relaxing E2 (E0 left zero) gives event mass 0 exactly; identical E0/E2 inputs give digest words 0,2,5,7 equal'))
        _put(h, 'OUT', 'd%d' % i, 'Q4', C('C0041 C0043 C0045 C0047', 'own (local): alternatives exist only crossed with E0, 2^384 input-pair configurations'))
    for i in (1, 3, 4, 6):
        _put(h, 'OUT', 'd%d' % i, 'Q1', F('research/sol_answer_D5_split.md research/pkg13/mitm/MITM.md', 'Luna local D5: the residual is exactly an E1 key XOR an E3 key, word by word (0 failures on 400 real points)'))
    _put(h, 'OUT', 'hi', 'Q1 Q2 Q3 Q4', ST('profile fact: the digest is the first 32 bytes of the root output; the second half v[i+8] ^ h[i] is not in the digest, no condition, no freedom, no alternative inside the profile'))
    # modes
    _put(h, 'MODE', 'single', 'Q1 Q3', ST('the record: single chunk, single block, root compression, counter 0'))
    # doors
    _put(h, 'DOOR', 'd22', 'D1', C('B3R2-E0q1-Q2-scan1 B3R2-E0q2-Q2-scan1 B3R2-E0q3-Q2-scan1 B3R2-E0q4-Q2-scan1 C0040 C0042 C0044 C0046',
                                   'own enumeration of in-call absorption on reachable clean states: q2..q4 forced equal in 100000/100000 absorbing members, relaxing E2 gives event mass 0 exactly (local: E0/E2 only, sampled states)'))


def _g06_map():
    for h in ('sha3-r5', 'sha3-r6'):
        _put(h, 'MSG', 'len', 'Q1', ST('profile fact: one 135-byte block, byte 135 = 0x86 (pad10* with domain byte 0x06)'))
        _put(h, 'MSG', 'cap', 'Q1 Q3', ST('the first block is absorbed into the zero state: capacity = 0 at the input of round 0'))
    h = 'sha3-r6'
    _put(h, 'MSG', 'free', 'Q3', C('C0114 C0119', 'own exact GF(2) rank: 1,080 free message bits, 768 after the 312 prefix conditions'))
    _put(h, 'MSG', 'len', 'Q4', C('C0114 C0116', 'own: 64-byte (512 bits) vs 135-byte (1,080 bits) formats: 2^352 vs 2^920 groups; column-parity kernel 760 dims'))
    # DIG: the don't-care cell is structural
    for h in ('sha3-r5', 'sha3-r6'):
        _put(h, 'DIG', 'dc', 'Q1 Q2 Q3 Q4', ST('profile fact: digest = lanes (0..3, 0) of the final state; the other 1,344 bits do not enter it (no condition, all free, no alternative within the profile)'))
    # ROW r5
    h = 'sha3-r5'
    _put(h, 'ROW', 'F520', 'Q1', C('C0104', 'own: F fixed bits = 520 exactly in every attempt'))
    _put(h, 'ROW', 'F520', 'Q3', C('C0105', 'own: DF after F + M2 + M3 = 157-173'))
    _put(h, 'ROW', 'F520', 'Q2 Q4', EX(OWN_JOBS['d180'], 'r5 connector relaxation (rounds 0-1 chi Q2/Q4) is assigned to Luna local D180'))
    _put(h, 'ROW', 'EDzero', 'Q1 Q3', C('C0104', 'own: E_D zero-difference rows 2-13 (mean 6.9), rank gain 10-65'))
    _put(h, 'ROW', 'EDzero', 'Q2 Q4', EX(OWN_JOBS['d180'], 'r5 connector relaxation (rounds 0-1 chi Q2/Q4) is assigned to Luna local D180'))
    _put(h, 'ROW', 'M2M3', 'Q1', C('C0104', 'own: M2 adds E_M rank 884-908, M3 13-35'))
    _put(h, 'ROW', 'M2M3', 'Q3', C('C0105', 'own: DF after F + M2 + M3'))
    _put(h, 'ROW', 'M2M3', 'Q2 Q4', EX(OWN_JOBS['d180'], 'r5 connector relaxation (rounds 0-1 chi Q2/Q4) is assigned to Luna local D180'))
    _put(h, 'ROW', 'M4', 'Q1', C('C0107', 'own: 127 conditions in all 7 beta1 candidates, rank gain 117-125'))
    _put(h, 'ROW', 'M4', 'Q3', C('C0108', 'own: final DF 33-53 over 158 accepted attempts'))
    _put(h, 'ROW', 'M4', 'Q2 Q4', EX(OWN_JOBS['d180'], 'r5 connector relaxation (rounds 0-1 chi Q2/Q4) is assigned to Luna local D180'))
    _put(h, 'ROW', 'FES24', 'Q1 Q2 Q3 Q4', C('SHA3-D180-ANF-CONSTRUCTOR50', 'own: 1,200/1,200 equations nonconstant, no linear dependence over 50 constructor spaces (Q2, Q3); ATLAS_SHA3 ex.py / clus2.py: the 24 printed equations are what the event needs, 511/512 in-kernel alternatives give P45 = 0 (Q1, Q4)', 'research/tools/traillab/ATLAS_SHA3.md research/tools/traillab/sha3_atlas/ex.py research/tools/traillab/sha3_atlas/clus2.py'))
    _put(h, 'ROW', 'DF33', 'Q1 Q3', C('C0108', 'own: DF needed 33, reached 33-53 (mean 42.9), min 33 = threshold'))
    _put(h, 'ROW', 'DIG45', 'Q2 Q4', F('research/tools/traillab/ATLAS_SHA3.md research/tools/traillab/sha3_atlas/ex.py', 'digest rows: DDT[q][0] + DDT[q][16], 4 of 5 bits per plane-0 row, branching over the 10 allowed digest-row values; event-exact (own ex.py reproduces 55/2^19)'))
    _put(h, 'ROW', 'DIG45', 'Q1 Q3', EX(OWN_JOBS['d180'], 'r5 rounds 3-4 Markov premise (chi Q1; round 4 Q3) is assigned to Luna local D180'))
    # ROW r6
    h = 'sha3-r6'
    _put(h, 'ROW', 'PRE128', 'Q1', C('C0112', 'own: 128 affine conditions, rank 128'))
    _put(h, 'ROW', 'PRE128', 'Q2', C('C0113', 'own: dropping any of the 128 conditions, a family of 32, or all'))
    _put(h, 'ROW', 'PRE128', 'Q3', C('C0114', 'own: 2^352 / 2^920 groups'))
    _put(h, 'ROW', 'PRE128', 'Q4', C('C0115', 'own: non-identity chi transitions over all 1,320 CP-kernel directions'))
    _put(h, 'ROW', 'PRE312', 'Q1', C('C0117', 'own: 312 independent affine conditions on the 1080 message bits'))
    _put(h, 'ROW', 'PRE312', 'Q2', C('C0118', 'own: dropping L5 / L15 / L8 / L12 groups'))
    _put(h, 'ROW', 'PRE312', 'Q3', C('C0119', 'own: 768 free bits'))
    _put(h, 'ROW', 'PRE312', 'Q4', C('C0120 C0121', 'own: z-subspaces affine through chi2/chi3, theta2 kernel membership of all 21 aligned lane pairs'))
    _put(h, 'ROW', 'ZCOUNT', 'Q1', C('C0114', 'own: 32 z-directions, 128 conditions'))
    _put(h, 'ROW', 'ZCOUNT', 'Q3', C('C0124', 'own: 32.0 bits per group, 262,137 distinct z in 2^18 samples'))
    _put(h, 'ROW', 'ZCOUNT', 'Q4', C('C0120 C0121', 'own: maximum coordinate clique 9 through chi2, kernel dimension 0 for all 21 aligned lane pairs'))
    _put(h, 'ROW', 'KEY140', 'Q1', C('sha3-r6|round4.chi|chi|Q1', 'own backward cone of the 140-bit key (z = 0..34 reading)'))
    _put(h, 'ROW', 'KEY140', 'Q2', C('sha3-r6|round4.chi|chi|Q2', 'own bit-flip test: all 1505 cone bits necessary'))
    _put(h, 'ROW', 'KEY140', 'Q3 Q4', EX(OWN_JOBS['d180'], 'r6 key / filter joint charge and alternative predicates are assigned to Luna local D180'))
    _put(h, 'ROW', 'FORMS8', 'Q1', F('research/tools/traillab/ATLAS_SHA3.md', 'r6 filter: 8 digest-determined bits, width ledger k = 7/8/9 (own exact ledger arithmetic)'))
    _put(h, 'ROW', 'FORMS8', 'Q2', F('research/tools/traillab/ATLAS_SHA3.md research/tools/traillab/sha3_atlas/deg6.py', 'k = 8 optimum by exact ledger arithmetic; all 8 forms have degree exactly 8 (deg6.py, 24 cosets x 8-dim subspaces)'))
    _put(h, 'ROW', 'FORMS8', 'Q3 Q4', EX(OWN_JOBS['d180'], 'r6 key / filter joint charge and alternative predicates are assigned to Luna local D180'))
    # STAGE r6 (only Q2 has a record: every block is needed; the ops/message figures were not reproduced)
    _put(h, 'STAGE', 'PRE1', 'Q2', C('C0113', 'own: no prefix condition can be dropped without losing affinity / rank'))
    _put(h, 'STAGE', 'CHI2', 'Q2', C('C0118', 'own: no prefix condition group can be dropped'))
    _put(h, 'STAGE', 'CHI3', 'Q2', C('C0123', 'own flip test: all 320 rows / 1600 outputs / 320 parities necessary (47 unchanged rows per step are a recomputation saving, not a droppable row)'))
    _put(h, 'STAGE', 'CONE4', 'Q2', C('C0126', 'own: all 320 chi4 rows and exactly 1363 of the 1600 theta5 words are necessary'))
    for k in 'PRE1 CHI2 CHI3 CONE4 CONE5 R6L TRANS PROBE'.split():
        for q in ('Q4',):
            if k in ('CHI3', 'CONE4'):
                _put(h, 'STAGE', k, q, EX(OWN_JOBS['d180'], 'r6 zero-digest 4-round cores (kernel class, parity sheets) Q4 at rounds 2..5 is assigned to Luna local D180'))


def _g07_map():
    # ---- sha256-37
    h = 'sha256-37'
    A37 = 'research/tighten/r37_leader_0db0eeb6.md research/tighten/th0rgal_03c12b41.md'
    _put(h, 'PREM', 'H1', 'R1', C('S37-DB-P0FACTS', 'own recount of p7 / p6 and the exact gate sizes'))
    _put(h, 'PREM', 'H1', 'R2', C('S37-J5-E4BUCKET', 'own run on 2^29 real first blocks (small N)'))
    _put(h, 'PREM', 'H2', 'R1 R2 R4', C('S37-R37M3-JOINT S37-DB-STAGES', 'own preregistered runs: J1/J2 128 + 128 reps, declared q3 2^-71.47; independent particle filter -73.994; sensitivity list in proof 11 (61.57158 for one bit lower)', R37P))
    _put(h, 'PREM', 'H2', 'R3', C('S37-R37M3-JOINT', 'own control: all 32 l hold row 16 (65,536 each, 2,097,152 pairs exhaustive); estimator validated against the registered study of 7319bba (proof 7.4b)', R37P))
    _put(h, 'PREM', 'H4', 'R1 R4', F(A37, 'tightening audits: A_C 2^60 -> 2^56 gives 60.40586, 2^52 60.3406; A_S 2^45 saves 0.0006'))
    _put(h, 'PREM', 'H5', 'R1 R2 R3', F(R37P, 'plane programs executed and counted by lowm.py; every lane of every class-test plane equals the definition (44,400 and 42,972 lanes in selftest)'))
    _put(h, 'PREM', 'H7', 'R1 R2', F(R37P, 'Appendix C computes mu0 and the bound with 60-digit decimals; lowm.py ledger() iterates Pcap and N_FB to a fixed point and asserts'))
    _put(h, 'PREM', 'H7', 'R4', C('S37-CAP', 'own: Bernstein cap -0.00211 bit (slack 2^-12.25)'))
    # ledger r37: rows covered by the leader / Th0rgal audits (older ledger lineage; class-scan and passing-class rows of R37M3 were re-derived in the package)
    for k in 'AC AS NFB FIXED W6T GBODY SEGOV BATCH RARE VMAX THETA PRE37'.split():
        _put(h, 'LEDGER', k, 'R1 R2 R4', F(A37, 'slack-row audits of the r37 leader (0db0eeb6) and of the rival shave 03c12b41 against our fcbc9c83: charged vs executed, bits per row'))
        _put(h, 'LEDGER', k, 'R3', F(A37, 'both audits reproduce the package T exactly with xtab.py ledger from a scratch copy before pricing any change'))
    # ---- sha256-38
    h = 'sha256-38'
    _put(h, 'PREM', 'H1', 'R1 R2 R3', F(R38P, 'exact distribution over all 2^32 A_-1 (hits38.c) + 29,360,128 real first blocks at 1.00 of expectation'))
    _put(h, 'PREM', 'H2', 'R1 R2', C('S38-STACK-A S38-STACK-B S38-STACK-JOINT', 'own preregistered runs: A +1.9762, B +1.3677, joint +3.3439 bit (32 seeds x 2^28)'))
    _put(h, 'PREM', 'H2', 'R3 R4', F(R38P, 'the shipped replica confirms the gain; proof 11 sensitivity list (q3_model 2^-98.0 -> 88.11971 ...)'))
    _put(h, 'PREM', 'H3', 'R1 R2 R3 R4', F(R38P, 'own repetition (13.5, A.8): 33,222 sampled successes, 8 runs, 21 other row-16 passes vs 18.15 under independence; H3 2^-7.5 -> 87.90973'))
    _put(h, 'PREM', 'H4', 'R1 R4', F('research/tighten/th0rgal_aed05522.md ' + R38P, 'A_C = 2^84 gives 87.99563; H4a/b/c split'))
    _put(h, 'PREM', 'H5', 'R1 R2 R3', F(R38P, 'programs generated and counted by a0lean38.py, equal to the scalar definition on every checked lane'))
    _put(h, 'PREM', 'H5', 'R4', C('S38-D7', 'own: delta7 = 0.293 (99% CP 0.305), ledger -0.110', R38P))
    _put(h, 'PREM', 'H6', 'R1 R2', F(R38P, 'Section 14 memory table, code counted at 32 B per instruction'))
    for k in 'PRO38 GRP4 A17I DEEP EPI P6B ALLOW38'.split():
        _put(h, 'LEDGER', k, 'R1 R2 R4', F('research/tighten/th0rgal_aed05522.md ' + R38P, 'audit of the rival shave aed05522 against our fdef4bab: every changed row recounted from the diff and re-priced with our ledger (prologue, GROUP4, A17, deep path, epilogue); sensitivity list in proof 11'))
        _put(h, 'LEDGER', k, 'R3', F('research/tighten/th0rgal_aed05522.md', 'our ledger reproduces both 71.07250 and 71.00164 exactly before pricing any change'))
    _put(h, 'LEDGER', 'NG38', 'R2 R4', C('S38-D7', 'own: delta7 = 0.293 (99% CP 0.305), ledger -0.110 (71.0725 -> 70.96278)'))
    _put(h, 'LEDGER', 'CAP38', 'R2 R4', C('S38-CAPan', 'own KILLED: the Bernstein cap analogue uses 3.4e-6 of the 0.39 budget, 70.96278 -> 70.96280 (dead < 1e-5 bit)'))
    # ---- sha3-r5
    h = 'sha3-r5'
    _put(h, 'PREM', 'CAPS', 'R1 R4', F(S5T, 'S5T section 3: X_MAX / A_MAX / B_TRUE caps priced (-0.044 / -0.019 / -0.023), flagged outcome-informed'))
    _put(h, 'LEDGER', 'KEYW5', 'R1 R2 R4', F('research/tighten/th0rgal_6938d3fb.md', 'audit of the rival shave 6938d3fb against our 39ff21c4: row (d) prices 17 key words vs 14 / 19 built, re-priced with our ledger'))
    for k in 'CONNW XMAX BPT SETUP5 EST1 EST2 MATCH SORT5 D20 PROC5'.split():
        _put(h, 'LEDGER', k, 'R1 R2 R4', F(S5T + ' research/tighten/r5_leader_b5632518.md', 'S5T / leader audits: charged vs executed per row, bits per row, instrumented copies of r5.py'))
        _put(h, 'LEDGER', k, 'R3', F(S5T, 'S5T reproduces N = 7.8731e9 units (log2 32.874286) and re-counts the match step op by op before pricing'))
    _put(h, 'LEDGER', 'BPT', 'R2', F('research/tighten/prereg_r5T_bprime_true.md', 'preregistered deterministic recomputation of the true B-prime cost of the 39 replays'))
    # ---- sha3-r6
    h = 'sha3-r6'
    for k in 'PERM6 ENC6 CNT6 REPL6'.split():
        _put(h, 'LEDGER', k, 'R1 R2 R4', F(S6R, 'S6R audit: charged vs executed per row (items 1-6), bits per row'))
        _put(h, 'LEDGER', k, 'R3', F(S6R, 'calibration: a Keccak round with rotation cost k costs 126 + 29 k, k = 5 reproduces 271 per round = 1626 (reference), N reproduced 128.031429'))
    _put(h, 'LEDGER', 'FORMS6', 'R1 R2 R3 R4', C('R6-8FORMS', 'own COMPUTED lever + skeptical check r6_8forms_verify.md HOLDS (four points tried to refute)', 'research/tighten/r6_8forms_verify.md'))
    _put(h, 'LEDGER', 'BATCH6', 'R1 R2 R4', C('R6-COSET R6-COSET-v0', 'own: f1346045 121.71644 -> fixed 121.72219, gain 0.148 over 8FORMS'))
    _put(h, 'LEDGER', 'FES6', 'R1 R2 R4', C('R6-FESKEY', 'own KILLED: T = 36 lower bound +0.0011, best packing T = 39'))
    _put(h, 'LEDGER', 'KEY6', 'R4', C('R6-PARAM', 'own KILLED: all elasticities < 0.01 at the coset ledger (t3_r6 reproduces 121.71644)'))
    _put(h, 'LEDGER', 'RARE6', 'R4', F(S6R, 'S6R audit item 9: DP prefilter 2 ops, R changes < 1e-30 bit, no real slack'))
    # ---- blake3-r2
    h = 'blake3-r2'
    _put(h, 'PREM', 'MU', 'R1 R2 R4', F('research/tighten/prereg_b3_MU_result.md research/tighten/prereg_b3T_MU.md', 'preregistered run: 2^19 contexts, mean metered debit 0.004352, declared MU 0.004425 (mean + 6 SE)'))
    _put(h, 'PREM', 'HG', 'R1 R2', F('research/tighten/b3m_F_result.md', 'preregistered 2^24-context count of the fills F of the shipped walk: mean 7159.266 (SE 0.65)'))
    _put(h, 'LEDGER', 'SPREC', 'R4', C('B3-F974', 'own: H1 prime factor 0.97 -> 0.974: -0.005487'))
    _put(h, 'LEDGER', 'BLK', 'R4', C('B3-BND115', 'own: boundary words 186 -> 115: -0.022315'))
    _put(h, 'LEDGER', 'WORD', 'R4', C('B3-SCAN12', 'own: scan 21 -> 12 per passing lane: -0.004248'))
    _put(h, 'LEDGER', 'CTX', 'R4', C('B3-CTX436', 'own: context 500 -> 436: -0.002591'))
    _put(h, 'LEDGER', 'SOLD', 'R4', C('B3-SOLD', 'own (local): S_old at the logged maxima: -0.012449'))
    for k in 'CTX BLK WORD LIVE PASSL WCTX CREDIT ONCE3 SOLD FINAL3 SPREC'.split():
        _put(h, 'LEDGER', k, 'R1 R2', F('research/tighten/th0rgal_blake3_b6a7681c.md research/tighten/th0rgal_37381922.md', 'audits of rival blake3 entries against the list-method ledger: rows recounted with the program\'s own constant block (R1 charged / R2 recount); our ledger run on their constants'))
        _put(h, 'LEDGER', k, 'R3', F('research/tighten/th0rgal_blake3_b6a7681c.md', 'the audits recompute N from the program\'s constant block and reproduce the stated figure before changing a row'))


_g02_map()
_g04_map()
_g05_map()
_g06_map()
_g07_map()

# ------------------------------------------------------------------------------------------------------------------ evaluation of the gap cells
_G_DEFAULT_WHY = {
    'G02': 'no record or ledger file of ours prices this memory question for this object',
    'G04': 'no own record answers this question for the CV / first-block / padding object (UNIVERSE_GAPS S1: the CV rows were wrongly closed as structural for the ordinary collision)',
    'G05': 'no own record or test answers this question for the BLAKE3 initial-state / pin / output / mode / door object',
    'G06': 'no own count of this SHA3 message / digest / condition-group / route-ledger object is recorded',
    'G07': 'no own measurement, recount or control is recorded for this premise / ledger row / judge cause',
}


def eval_gap(c):
    h, loc, q = c['hash'], c['loc'], c['q']
    spec = GMAP.get((h, loc), {}).get(q)
    if spec is None:
        return unscanned(_G_DEFAULT_WHY[c['group']])
    kind = spec[0]
    if kind == 'STRUCT':
        return scanned_struct(spec[1])
    if kind == 'EXCL':
        return excluded(spec[1], spec[2])
    if kind == 'CELLS':
        ids = ok_ids(spec[1])
        if ids and len(ids) == len(spec[1]):
            return scanned_cells(ids, spec[2])
        fl = [f for f in spec[3] if exists(f)]
        if ids:
            return scanned_cells(ids, spec[2] + ' [records missing from the store: %s]' % ', '.join(i for i in spec[1] if i not in ids))
        if fl and len(fl) == len(spec[3]):
            return scanned_file(fl, spec[2])
        return unscanned('mapped record(s) %s are not own-test records in CELLS.jsonl and no file backs them' % ' '.join(spec[1]))
    if kind == 'FILE':
        miss = [f for f in spec[1] if not exists(f)]
        if miss:
            return unscanned('mapped evidence file(s) missing: ' + ' '.join(miss))
        return scanned_file(spec[1], spec[2])
    return unscanned('bad rule')


_REPEAT_HALF = set(['DIG.l1', 'DIG.l2', 'DIG.l3', 'CV.A-3', 'CV.A-4', 'CV.E-3', 'CV.E-2', 'CV.E-1', 'INIT.v1', 'INIT.v3', 'INIT.v4', 'INIT.v5', 'INIT.v7',
                    'OUT.d1', 'OUT.d3', 'OUT.d4', 'OUT.d6', 'OUT.d2', 'OUT.d5', 'OUT.d7', 'PIN.X7', 'PIN.X11', 'PIN.X15'])
_DOOR_W = {'DOOR.d21': 25.0, 'DOOR.d22': 25.0, 'DOOR.d24': 20.0, 'DOOR.d37': 15.0, 'DOOR.d38': 25.0, 'DOOR.d45': 8.0}


def gap_weight(c):
    """estimated agent minutes for one cell (a fixed 8 minutes of setup per unit is added when units are built);
    cells of objects that repeat the method of a sibling (the other CV words, digest lanes, h words) count half"""
    loc = c['loc']
    if c['kind'] == 'b3msg':
        return 2.5
    if c['kind'] == 'b3door':
        return _DOOR_W[loc]
    if loc == 'CV.H1' and c['q'] == 'Q1':
        return 25.0
    if loc == 'CV.diff':
        return {'Q1': 5.0, 'Q2': 6.0, 'Q3': 8.0, 'Q4': 24.0}[c['q']]
    if c['kind'] == 'sha3stage':
        w = {'Q1': 12.0, 'Q2': 6.0, 'Q4': 8.0}[c['q']]
    elif c['kind'] == 'ledger':
        w = {'R1': 3.0, 'R2': 8.0, 'R3': 5.0, 'R4': 5.0}[c['q']]
    elif c['kind'] == 'judge':
        w = {'R1': 3.0, 'R2': 8.0, 'R3': 6.0, 'R4': 4.0}[c['q']]
    else:
        w = float(_G_WEIGHT[c['q']])
    return w * (0.5 if loc in _REPEAT_HALF else 1.0)


def attach_gap(universe):
    for c in build_gap_universe():
        r = eval_gap(c)
        if r['state'] != 'SCANNED' and c['id'] in NAMED:
            r = scanned_cells(NAMED[c['id']], 'own-test record(s) naming this universe cell')
        c.update(r)
        universe.append(c)
    for c in universe:
        c.setdefault('group', 'W1')
    return universe


# ------------------------------------------------------------------------------------------------------------------ units for the gap cells
G_METHOD = {
    'G02': ('G02 MEMORY AXIS (score = time_log2 + max(0, log2(bytes) - 20); Pareto live). Answer ONLY the listed M-questions for each object: '
            'M1 bytes held at its peak (exact allocation of the shipped program, say bound vs exact); M2 exact ledger time to recompute / stream / shard it instead of holding it; '
            'M3 the S-optimal hold-versus-recompute point for this object with the others fixed; M4 the breakpoint at 2^20 B (S on both sides, is crossing worth it). '
            'Use the package ledger program on a scratch copy (lowm.py memory/ledger, a0lean38.py ledger, the D126/D152/D161/D166 models) and first reproduce the stated time_log2 and byte total as the known-answer check. '
            'Code size follows each proof convention (r38: 32 B per instruction); name the convention.'),
    'G04': ('G04 CV / FIRST BLOCK / PADDING of the ORDINARY collision (the SFS pair has dCV = 0 by definition; the attack does not: CV = F(IV, M0) of a random first block and the program gates on it). '
            'Q1 count/size of the object as the attack uses it; Q2 necessity (drop or replace it, recompute the exact event or the expected counts); Q3 log2 freedom left (exact count or sample with interval); Q4 alternatives. '
            'Use the shipped lowm.py / a0lean38.py / traillab code and our own F_37 / F_38 hash; validate on the published pair first. Recompute the schedule from W0..W15 for any held-fixed word.'),
    'G05': ('G05 BLAKE3 INITIAL STATE / PINS / OUTPUT FOLD / MODE / MESSAGE READS / DOORS (blake3-r2). Q1 value or difference/condition count as used; Q2 necessity (relax or replace it, recount the exact outcome mass); Q3 degrees of freedom (exact count over carries); Q4 alternatives. '
            'Door cells (D1): run exactly the test written in the RELABEL column of research/CLOSED_DOORS.md on our own code; the door stays CLAIMED-UNTESTED until your own_test record exists. '
            'Message-read cells (Q1): which role (free / pinned / cancelling / forced) the word has at THIS use and whether the word\'s two uses agree. '
            'Use research/tools/traillab/b3atlas scripts (rows_dp.py, solo.py, typed_check.py ...) and a reference BLAKE3 validated first on known full 7-round vectors and against the organizer verifier (hash-smash/verifier/blake3.py), then run at 2 rounds.'),
    'G06': ('G06 SHA3 (r5 / r6): message format, digest lanes, condition groups (ROW) and the r6 route ledger (STAGE). Q1 count as used; Q2 necessity (drop one group/lane, recompute the exact rank or event); Q3 degrees of freedom (exact GF(2) rank / count); Q4 alternatives. '
            'STAGE cells: Q1 = reproduce the stated ops/message figure of the block with our own bit-sliced op count (and resolve the 132.44 vs 124.62 sum mismatch of SHA3R6_MAP lines 34-35), Q2 = is the block droppable/mergeable, Q4 = a cheaper implementation. '
            'Use the validated own Keccak (24 rounds vs hashlib sha3_256; 6-round prefix vs the organizer reference) of research/dig/incoming/sha3-r6-U02..U04/work and tools/traillab/sha3_atlas.'),
    'G07': ('G07 PREMISES / OP LEDGERS / JUDGE CAUSES per filed line. R1 value charged or stated (exact line); R2 own re-measurement or exact recount (fresh seeds, a rule written BEFORE the run, a control arm; for ledger rows the metered run of the shipped program, best case); '
            'R3 control (the same tool on a known answer or a negative control that must fail); R4 score sensitivity in bits per unit and slack candidates. '
            'Judge-cause cells read: R1 is the cause present in the current package, R2 the margin number measured on it (bytes, seconds, statistic), R3 the check fired on the known failing dossier and a passing one, R4 distance to the threshold. '
            'Rules: charge what the program executes (best case), no outcome-informed caps, Th0rgal-style shaves are ledger cells (checklist kinds 1-7, research/tighten/CHECKLIST.md, BUILD_RULES.md).'),
}
G_HINT = {
    'G02': 'research/sol_answer_D126_memory_rule.md, D152, D161, D166, D117; research/tighten/S5T_r5_memrule.md, S6R_r6_memrule.md; research/retest/b3m_maxphase/RESULT.md; the staged packages pkgR37M3, pkgR38M3, pkgR5T, pkgS6DB, pkgB3S2 under research/tools/build_pkg/scratch (read their proof memory sections first)',
    'G04': 'research/retest/dense_boring/RESULT.md (S37-DB-P0FACTS), research/retest/close37/job5/ (E_-4 bucket, real first blocks), pkgR37M3 proof Sections 4-5, 12, 14.2, pkgR38M3 proof 5, 13.1, A.1-A.3, tools/traillab/digs/zoneD, UNIVERSE_GAPS.md section 4',
    'G05': 'research/BLAKE3_2ROUND_MAP.md (sections 2, 5), tools/traillab/ATLAS_BLAKE3.md, CLOSED_DOORS.md section 1 (rows 21, 22, 24, 37, 38, 45 and their RELABEL tests), tighten/b3_parent_node_scout.md, tighten/b3_ctr_class_transfer.md, pkgB3V/pkgB3S2 proof Sections 2-3, 12; do not redo the m0..m15 word cells and the C3 pin cells (C0028-C0035, C0056-C0059, C0084-C0087)',
    'G06': 'research/SHA3R6_MAP.md, tools/traillab/ATLAS_SHA3.md, tools/traillab/sha3_atlas, research/sha3r6 (linstruct, linstruct3, isd), dig records C0104-C0127; do not redo them',
    'G07': 'research/tighten/*.md (S5T, S6R, B3M, r37_leader_0db0eeb6, th0rgal_*, prereg_*), research/retest/r38_stack, retest/t4, retest/s6d, research/FILINGS.md, JUDGE_FAILURE_REPORT.md, research/dossiers/<id8> for each ruling, the package proof Premises sections',
}
G_TRAP = ('Traps: UNKNOWN is not UNSAT; expanded words W16+ are never varied with later words held (recompute the schedule from W0..W15); the paper prints != as a combining slash; '
          'report every number with its label (exact / bound / sampled with interval); own code only (own_test true) - never run or import another participant\'s program.')


def gap_group_key(c):
    return (c['hash'], c['group'], c['cl'])


def build_gap_units(universe):
    units = []
    gaps = [c for c in universe if c.get('group', 'W1') != 'W1' and c['state'] == 'UNSCANNED']
    byhg = collections.OrderedDict()
    for c in gaps:
        byhg.setdefault((c['hash'], c['group']), []).append(c)
    order_h = ['sha256-37', 'sha256-38', 'sha3-r5', 'sha3-r6', 'blake3-r2']
    counters = collections.Counter()
    pending_small = collections.defaultdict(list)   # hash -> list of leftover atoms-lists < 20 minutes
    for h in order_h:
        for g in ('G02', 'G04', 'G05', 'G06', 'G07'):
            cs = byhg.get((h, g))
            if not cs:
                continue
            # atoms: all unscanned cells of one object (location), clusters keep their order
            atoms = collections.OrderedDict()
            for c in cs:
                atoms.setdefault((c['cl'], c['loc']), []).append(c)
            clusters = collections.OrderedDict()
            for (cl, loc), a in atoms.items():
                clusters.setdefault(cl, []).append(a)
            chunks = []
            cur, curw = [], 0.0
            for cl, alist in clusters.items():
                for a in alist:
                    w = sum(gap_weight(c) for c in a)
                    if cur and curw + w > 52.0:
                        chunks.append(cur)
                        cur, curw = [], 0.0
                    cur += a
                    curw += w
                # close the chunk at a cluster boundary if it is already substantial
                if curw >= 28.0:
                    chunks.append(cur)
                    cur, curw = [], 0.0
            if cur:
                chunks.append(cur)
            # merge a small trailing chunk into its predecessor when it fits in 65 minutes
            if len(chunks) > 1 and sum(gap_weight(c) for c in chunks[-1]) < 16 and sum(gap_weight(c) for c in chunks[-2]) + sum(gap_weight(c) for c in chunks[-1]) <= 54:
                last_ = chunks.pop()
                chunks[-1] = chunks[-1] + last_
            for ch in chunks:
                w = sum(gap_weight(c) for c in ch)
                counters[(h, g)] += 1
                uid = '%s-%s-U%02d' % (h, g, counters[(h, g)])
                units.append(dict(id=uid, hash=h, group=g, scope=gap_scope(g, ch), cells=[c['id'] for c in ch],
                                  est_minutes=max(10, int(round(w)) + 8), questions=gap_questions(h, g, ch)))
                for c in ch:
                    c['unit'] = uid
    return units


def gap_scope(g, ch):
    labels = []
    for c in ch:
        if c['label'] not in labels:
            labels.append(c['label'])
    head = {'G02': 'memory objects', 'G04': 'CV / first block / padding', 'G05': 'BLAKE3 init / pins / output / mode / reads / doors',
            'G06': 'SHA3 message / digest / condition groups / route ledger', 'G07': 'premises / op ledgers / judge causes'}[g]
    s = head + ': ' + '; '.join(l[:70] for l in labels[:6]) + (' ... (%d objects)' % len(labels) if len(labels) > 6 else '')
    return s


def gap_questions(h, g, ch):
    qs = sorted({c['q'] for c in ch})
    qt = G_METHOD[g]
    objs = collections.OrderedDict()
    for c in ch:
        objs.setdefault(c['loc'], []).append(c)
    lines = []
    for loc, cl in objs.items():
        lines.append('- %s [%s] (%s): %s' % (cl[0]['label'], ' '.join(c['q'] for c in cl), loc, cl[0]['facts']))
    why = sorted({c['reason'] for c in ch})
    txt = qt + ' Cells of this unit (only the listed questions are open for each object): ' + ' '.join(lines) + ' Why open: ' + ' / '.join(w[:240] for w in why[:3]) + ' Existing material (read first, do not redo): ' + G_HINT[g] + ' ' + G_TRAP
    return txt


G_TITLE = {'G02': 'memory objects (M1 bytes held, M2 time to recompute instead, M3 S-optimal point, M4 breakpoint at 2^20)',
           'G04': 'CV / first block / block count / padding objects (sha256-37/38)',
           'G05': 'BLAKE3 INIT v0..v15, pins, OUT fold, MODE, message reads, doors 21 22 24 37 38 45',
           'G06': 'SHA3 MSG format, DIG lanes, ROW condition groups, STAGE route ledger',
           'G07': 'statistical premises, op ledgers, judge causes per filed line'}


def write_gap_md(full, L):
    gaps = [c for c in full if c.get('group', 'W1') != 'W1']
    L.append('\n## Gap dimensions G02, G04, G05, G06, G07 (added 2026-10-12)\n')
    L.append('Source: UNIVERSE_GAPS.md sections 4-7 and 9 (critic pass). NOT added here because owned elsewhere: G01 Poseidon (running elsewhere), G03 characteristic family (Luna 2 and dense-dig), G08, G09. '
             'Cell id = `hash|loc|object|question`; `loc` is `MEM.<key>`, `CV.<key>`, `INIT.v0`, `PIN.w4`, `OUT.d0`, `MODE.<key>`, `DOOR.d21`, `MSG.<call>.<x|y>`, `DIG.l0`, `ROW.<key>`, `STAGE.<key>`, `PREM.<key>`, `LEDGER.<key>`, `JUDGE.<key>`. '
             'Question tokens: M1-M4 (G02), Q1-Q4 as for SHA3/BLAKE3 (G04, G05, G06; MSG reads and STAGE use Q1 / Q1 Q2 Q4 only), D1 (the RELABEL test of one door), R1-R4 (G07). '
             'A record naming `universe cell <id>` in its notes counts (full id); the wave-1 short form `universe cell round2.chi|Q1` is now read too (hash and object come from the record).\n')
    L.append('Question meanings:\n')
    for g in ('G02', 'G07', 'D1'):
        for q, t in GQ[g].items():
            L.append('- %s (%s): %s' % (q, g if g != 'D1' else 'G05 doors', t))
    L.append('')
    # totals per group and hash
    hs = ['sha256-37', 'sha256-38', 'sha3-r5', 'sha3-r6', 'blake3-r2']
    rows = []
    for g in ('G02', 'G04', 'G05', 'G06', 'G07'):
        for h in hs:
            sub = [c for c in gaps if c['group'] == g and c['hash'] == h]
            if not sub:
                continue
            sc = [c for c in sub if c['state'] == 'SCANNED']
            rows.append([g, h, len(sub), len(sc), sum(c['basis'] == 'STRUCTURAL' for c in sc), sum(c['basis'] == 'CELLS' for c in sc), sum(c['basis'] == 'FILE' for c in sc),
                         sum(c['state'] == 'EXCLUDED' for c in sub), sum(c['state'] == 'UNSCANNED' for c in sub)])
    tot = [sum(r[i] for r in rows) for i in range(2, 9)]
    rows.append(['**all**', ''] + tot)
    L.extend(md_table(rows, ['group', 'hash', 'cells', 'scanned', 'structural', 'CELLS record', 'FILE (pending ingest)', 'excluded (running jobs)', 'unscanned']))
    for g in ('G02', 'G04', 'G05', 'G06', 'G07'):
        sub = [c for c in gaps if c['group'] == g]
        L.append('\n### %s - %s\n' % (g, G_TITLE[g]))
        objs = collections.OrderedDict()
        for c in sub:
            objs.setdefault((c['hash'], c['loc']), []).append(c)
        rows = []
        for (h, loc), cl in objs.items():
            rows.append([h, loc, cl[0]['label'][:62], ' '.join(c['q'] for c in cl),
                         ''.join({'SCANNED': 'S', 'EXCLUDED': 'X', 'UNSCANNED': '.'}[c['state']] for c in cl)])
        L.extend(md_table(rows, ['hash', 'loc', 'object', 'questions', 'state (S scanned, X excluded, . unscanned)']))
    L.append('\n### Mapping of existing records onto the new cells (critic step 1, no compute)\n')
    mp = collections.Counter()
    for c in gaps:
        if c['state'] == 'SCANNED' and c['basis'] == 'CELLS':
            for e in c['evidence']:
                mp[e] += 1
    L.extend(md_table([[k, v] for k, v in mp.most_common(60)], ['CELLS record', 'new cells it scans']))
    L.append('\nReading rules used: STRUCTURAL = fixed by the target profile (reason in the cell); FILE = an exact computation of ours that is not yet a CELLS record (Luna local D126/D152/D161/D166, package proof tables produced by the package ledger programs, tightening audits, preregistered runs); '
             'a mapped file that does not exist, or a mapped record that is not an own test, leaves the cell UNSCANNED. Rival and outside numbers (QUOTED in D117, participant measurements quoted in D152/D161: B-prime 113.5 MiB, EM 31 MiB) do NOT scan M1.')
    L.append('\nFindings of the mapping that change the plan:\n')
    L.append('- The six wave-1 sha3-r6 chi cells (rounds 2-3, Q1-Q3) were UNSCANNED only because their scan records C0122-C0127 name the cell in the short form `round2.chi|Q1` (no hash prefix); they are now credited and no wave-1 unit is left.')
    L.append('- sha256-37 `MEM.PRE`: the 607,744 B of R37M3 is the ONLINE resident set; the preprocessing working set (family discovery over 2^29 E4 values, 12.1M members grouped by c7) is not stated and may not be inside the memory claim.')
    L.append('- sha3-r6 `ROW.KEEP35`: the leader\'s z-set is unpublished; z = 0..34 is a reading (29 contiguous planes gives 1362, the leader 1363); the ops/message figure of the round-5 cone (2.19) was not reproduced.')
    L.append('- sha3-r6 `STAGE`: the block ops/message figures were never reproduced by our own count (Q1 open for all eight blocks); only Q2 (every cone/prefix row is needed) is answered by records.')
    L.append('- blake3-r2 DOOR cells: only door 22 has an own test (the E0/E2 in-call absorption records, local); doors 21, 24, 37, 38, 45 stay CLAIMED-UNTESTED.')
    L.append('- G07 JUDGE cells: no record exists for any of the 20 causes; every cell is open by construction.')
    L.append('- G07 LEDGER: the staged table-free ledgers (R37M3 lowm.py, R38M3 a0lean38.py) have no audit yet; the audits cover the filed xtab.py / vt38.py lineages.')


def selfcheck(universe, units):
    """known-answer checks of the extension: wave-1 universe size, unique ids, every unscanned cell in exactly one unit, no scanned cell in a unit, unit sizes"""
    w1 = [c for c in universe if c.get('group', 'W1') == 'W1']
    assert len(w1) == 2100, 'wave-1 universe changed: %d' % len(w1)
    ids = [c['id'] for c in universe]
    assert len(ids) == len(set(ids)), 'duplicate cell ids'
    by = {c['id']: c for c in universe}
    seen = collections.Counter(i for u in units for i in u['cells'])
    assert all(n == 1 for n in seen.values()), 'cell in two units'
    assert all(by[i]['state'] == 'UNSCANNED' for i in seen), 'scanned or excluded cell in a unit'
    assert set(seen) == {c['id'] for c in universe if c['state'] == 'UNSCANNED'}, 'unscanned cell without a unit'
    assert all(10 <= u['est_minutes'] <= 60 for u in units), 'unit size outside 10..60 minutes'
    assert not any(c['state'] == 'SCANNED' and not c['evidence'] and c['basis'] != 'STRUCTURAL' for c in universe), 'scanned without evidence'
    print('selfcheck ok: wave-1 2100 cells, %d gap cells, %d units, %d cells in units' % (len(universe) - len(w1), len(units), len(seen)))


_old_write_gap_md = write_gap_md


def write_gap_md(full, L):
    _old_write_gap_md(full, L)
    ex = collections.Counter((c['hash'], c['group'], c['owner']) for c in full if c.get('group', 'W1') != 'W1' and c['state'] == 'EXCLUDED')
    L.append('\nExcluded gap cells (a running job owns them): ' + '; '.join('%s %s %s x%d' % (h, g, o, n) for (h, g, o), n in sorted(ex.items())) +
             '. They are the r5 connector relaxation (ROW F520 / EDzero / M2M3 / M4 Q2, Q4), the r5 rounds 3-4 Markov premise (ROW DIG45 Q1, Q3), the r6 key/filter joint charge and alternative predicates (ROW KEY140 / FORMS8 Q3, Q4) and the r6 zero-digest 4-round cores (STAGE CHI3 / CONE4 Q4), the same areas wave 1 gave to Luna local D180.\n')


# ----------------------------------------------------------------------------------------------------------- build
def owned_override(h, c, r):
    """a result that exists only as a file of a running job, inside the area that job owns, stays with the owner (not final until ingested)"""
    if r['state'] != 'SCANNED' or r['basis'] != 'FILE':
        return r
    q = c['q']
    if h == 'sha256-38':
        if q == 'Q5' and c['row_j'] >= 17:
            return excluded(OWN_JOBS['rows38'], 'owned by rows38-full-dig (Q5, reader row >= 17); its pending file evidence: ' + '; '.join(r['evidence'][:2]))
        if q in ('Q2', 'Q3') and c.get('row') is not None and c['kind'] == 'row' and c['row'] <= 16:
            return excluded(OWN_JOBS['luna2'], 'owned by Luna 2 (rows -4..16 Q2/Q3); pending file evidence: ' + '; '.join(r['evidence'][:2]))
        if q == 'Q4' and c['kind'] == 'row' and c['row'] <= 16:
            return excluded(OWN_JOBS['dense'], 'dense rows <= 16 Q4 owned by dense-dig; pending file evidence: ' + '; '.join(r['evidence'][:2]))
    return r


def evaluate_all():
    cells = []
    q2c = {}
    for h in SHA256:
        chi = CHI[h]
        q2c[h] = build_q2_cover(h, chi)
        for c in build_sha256_universe(h):
            cells.append((c, h))
    for h in ('sha3-r5', 'sha3-r6'):
        for c in build_sha3_universe(h):
            cells.append((c, h))
    for c in build_blake3_universe():
        cells.append((c, 'blake3-r2'))
    out = []
    for c, h in cells:
        if h in SHA256:
            chi = CHI[h]
            qc, rc = q2c[h]
            if c['kind'] == 'row':
                c['_obj_conds'] = r37_obj_info(chi, c['row'], c['object'])['conds'] if c['row'] >= 0 else []
            r = eval_sha256(h, c, chi, qc, rc)
        elif h.startswith('sha3'):
            r = eval_sha3(c)
        else:
            r = eval_blake3(c)
        c.pop('_q2_partial', None)
        if r['state'] != 'SCANNED' and c['id'] in NAMED:
            r = scanned_cells(NAMED[c['id']], 'own-test record(s) naming this universe cell')
        r = owned_override(h, c, r)
        c.update(r)
        out.append(c)
    return attach_gap(out)


# ----------------------------------------------------------------------------------------------------------- units
def weight(c):
    h, q, k = c['hash'], c['q'], c['kind']
    if h in SHA256:
        if k in ('pair', 'sched'):
            return 4.0
        if q == 'Q1':
            return 0.5
        if q == 'Q2':
            return 2.0 + 1.5 * len(c.get('missing') or [1])
        if q == 'Q3':
            return 8.0
        return 8.0
    if h.startswith('sha3'):
        return {'Q1': 8.0, 'Q2': 10.0, 'Q3': 10.0, 'Q4': 15.0}[q] if c['object'] == 'chi' else 8.0
    if k == 'b3word':
        return 6.0
    if c.get('code') in ('0', 'P'):
        return {'Q1': 3.0, 'Q2': 5.0, 'Q3': 3.0, 'Q4': 6.0}[q]
    return {'Q1': 5.0, 'Q2': 8.0, 'Q3': 8.0, 'Q4': 10.0}[q]


def group_key(c):
    h = c['hash']
    if h in SHA256:
        if c['kind'] == 'row':
            return (0, c['row'])
        return (1, c['row'])
    if h.startswith('sha3'):
        return (0, c['round'])
    if c['kind'] == 'b3word':
        return (1, c['word'] // 2)
    return (0, B3_CALLS.index(c['call']))


QTEXT = {
    'sha256': {
        'Q1': 'Q1: does every printed cell of this object hold on the published pair? (traillab check mode on the pair of the REFERENCE_CARD / check38.py conventions)',
        'Q2': 'Q2: drop each printed condition of this object singly (traillab window/exact with dropv/dropx/dropx2 and violator tagging) - does the event still occur on the full path? Report dropped/required with a rule-of-three bound; for dense rows report the row\'s local solution count instead (traillab exact/backward/varcount)',
        'Q3': 'Q3: log2 of the number of values of the row consistent with its conditions given the earlier rows of the pair (traillab exact --enum, varcount)',
        'Q4': 'Q4: other signed patterns with the same modular difference: do they propagate to the same later differences? (traillab sdiff / backward signed-pattern list, then window to the event)',
        'Q5': 'Q5: joint drop of one condition in each of the two rows against the two singles (traillab window with two drops, same seeds); for a schedule link also the exact set of the source word for the required modular difference (traillab sdiff/exact)',
    },
    'sha3': {
        'Q1': 'Q1: count the differences/conditions the attack uses at this map (own Keccak, exact DDT/ANF on the path)',
        'Q2': 'Q2: necessity of each condition group at this map (drop one, recompute the event / rank)',
        'Q3': 'Q3: log2 degrees of freedom left at this map (exact GF(2) rank / count)',
        'Q4': 'Q4: alternative output differences / patterns at this map and whether they reach the same later differences (exhaust the 5-bit chi S-box transitions, theta kernel membership)',
    },
    'blake3': {
        'Q1': 'Q1: difference/condition count as used at this quarter-step or word (own DP over the printed definitions, pkgB3U proof.md)',
        'Q2': 'Q2: necessity of each condition group here (relax one, recount the exact outcome mass)',
        'Q3': 'Q3: degrees of freedom here (exact count over carries)',
        'Q4': 'Q4: alternative outcomes / carry patterns (the 75/32 effect) here and whether they reach the same later differences',
    },
}


def fam(h):
    return 'sha256' if h in SHA256 else ('sha3' if h.startswith('sha3') else 'blake3')


HINTS = {
    'sha256-37': 'REFERENCE_CARD.md (conventions, erratum A15[29]=A17[29]); row card research/tools/traillab/row_cards/row_NN.md; atlas_runs/*/RESULT.md for the nearest rows; do not re-run S37-ZDOWN-04..13, S37-SWEEP-*, S37-PAIR-*',
    'sha256-38': 'check38.py conventions (W25[4]=W25[6]); research/tools/traillab/atlas_runs38/*/ (running job outputs: A-dense, R-rows, H-drops, S-sched, C-controls) and research/retest/backward38/, r38_stack/, r38_w16_relax/ are existing results: read before running',
    'sha3-r5': 'ATLAS_SHA3.md, OTHER_HASH_DIG.md, tools/traillab/sha3_atlas/ (own Keccak, validated: P45 = 55/2^19)',
    'sha3-r6': 'SHA3R6_MAP.md (leader route, rounds 1-6 in its 1-based numbering = rounds 0-5 here), ATLAS_SHA3.md r6 filter atlas, research/sha3r6/ (linstruct, linstruct3, isd results)',
    'blake3-r2': 'ATLAS_BLAKE3.md, GRID_BLAKE3.md, BLAKE3_2ROUND_MAP.md, tools/traillab/b3atlas/ (rows_dp.py, solo.py, typed_check.py ...), pkgB3U proof.md Sections 1-10',
}


R6_NOTE = {
    0: 'leader route round 1 (SHA3R6_MAP.md section 2, 1-based naming): rounds 1 is affine in the group and the prefix conditions keep its chi linear (each z-flip moves 2 round-1 bits, 22-word footprint); count those prefix conditions, drop each (does the affine property / rank fail?), the freedom (1,080 free message bits, 24/35-dim spaces of linstruct), and whether non-identity chi transitions give another route (section 4 remaining lead).',
    1: 'leader route round 2: chi is not affine, each z-step computes the change over 21 rows and patches 554 words of the stored round-3 input (chi2 patch + theta3 = 7.30 ops/message); count the conditions/rows used, necessity, freedom, alternatives (rank <= 2 of linstruct3 for 3-round affine structures).',
    2: 'leader route round 3: the chi3 block (chi3 + theta4 parities, 53.30 ops/message); count the conditions/rows used, necessity, freedom, alternatives (chi3 adjacency rule of linstruct3, max clique 2).',
    3: 'leader route round 4: the round-4 cone of the 140-bit key (46.11 ops/message); count the cone rows/bits the key keeps, which are necessary, the freedom, alternatives.',
    4: 'leader route round 5: the round-5 cone (2.19 ops/message); the same questions on the cone rows.',
}
R5_NOTE = ('r5 rounds 0/1 chi: count the connector conditions as used (520 fixed F bits, E_D zero rows, linearised row masks M2/M3; 127 linear round-1 conditions M4) and the connector freedom DF (33 needed, 45-60 typical) from the package constructor (fes_setup, sha3_atlas); '
           'theta Q4 at rounds 0,1,2,4: is the round input/output difference in the column-parity kernel, and what do the non-kernel alternatives do (exact, small).')
B3_NOTE = {
    'C1': 'necessity of filter (1) on Y9 and of the exact prefilter PF: relax each (accept more Y9 values), recount the exact outcome mass through E1/E3 (rows_dp.py/typed_check.py), report loss or gain per filter word.',
    'C3': 'necessity of the C3 pin (w4 advice, DY3/DY11 constants) and alternative constant pairs: recompute the Fact P outputs for the 64 (Y3,Y11) cells with the current ledger; own enumeration only.',
    'E0': 'relax the zero difference of E0 (give its inputs a difference): enumerate in-call absorption on reachable clean states and report which further calls activate and whether any residual-0 solution exists (CLOSED_DOORS BLAKE3 doors 22/24 were relabelled CLAIMED-UNTESTED).',
    'E2': 'relax the zero difference of E2 (same test as E0).',
    'E1': 'q1 zero difference of E1 (same relaxation test); q2 the 11-bit cube Q*: its dimension, necessity of each cube bit, effect on beta (exact over carries).',
    'W': 'message words: from pkgB3U proof.md Sections 1-3 and ATLAS_BLAKE3.md, state for each word whether it is free, pinned (w4), cancelling (w5 + w4 - w4'') or part of a forced constant (X3, X7, X11, X15), then count Q1-Q4 for it with the b3atlas scripts.',
}


def scope_text(h, cells):
    if h in SHA256:
        rows = sorted({c['row'] for c in cells if c['kind'] == 'row'})
        pairs = [c for c in cells if c['kind'] in ('pair', 'sched')]
        parts = []
        if rows:
            parts.append('row%s %s (%s)' % ('s' if len(rows) > 1 else '', ','.join(map(str, rows)), ','.join(sorted({c['object'] for c in cells if c['kind'] == 'row'}))))
        if pairs:
            js = sorted({c['row'] for c in pairs})
            parts.append('Q5 interactions/schedule links into row%s %s' % ('s' if len(js) > 1 else '', ','.join(map(str, js))))
        return '; '.join(parts)
    if h.startswith('sha3'):
        rd = sorted({c['round'] for c in cells})
        return 'round%s %s: %s' % ('s' if len(rd) > 1 else '', ','.join(map(str, rd)), ','.join(sorted({c['object'] for c in cells})))
    if any(c['kind'] == 'b3word' for c in cells):
        return 'message words ' + ','.join('m%d' % w for w in sorted({c['word'] for c in cells if c['kind'] == 'b3word'}))
    return 'G calls ' + ','.join(sorted({c['call'] for c in cells}, key=B3_CALLS.index)) + ' (quarter-steps ' + ','.join(sorted({c['loc'] for c in cells})[:8]) + ('...' if len({c['loc'] for c in cells}) > 8 else '') + ')'


def build_units(universe):
    units = []
    for h in ['sha256-37', 'sha256-38', 'sha3-r5', 'sha3-r6', 'blake3-r2']:
        un = [c for c in universe if c['hash'] == h and c['state'] == 'UNSCANNED' and c.get('group', 'W1') == 'W1']
        if not un:
            continue
        groups = collections.OrderedDict()
        for c in sorted(un, key=lambda c: (group_key(c), c['q'], c['loc'])):
            groups.setdefault(group_key(c), []).append(c)
        chunks = []
        for k, cs in groups.items():
            tot = sum(weight(c) for c in cs)
            if tot <= 60:
                chunks.append(cs)
                continue
            n = int(math.ceil(tot / 60.0))
            target = tot / n
            part, cur, acc = [], [], 0.0
            for c in cs:
                w = weight(c)
                if cur and len(part) < n - 1 and acc + w / 2.0 > target:
                    part.append(cur)
                    cur, acc = [], 0.0
                cur.append(c)
                acc += w
            if cur:
                part.append(cur)
            chunks.extend(part)
        # merge small neighbours (< 30 min) into units of at most 60 min, same kind of work only
        merged = []
        for ch in chunks:
            w = sum(weight(c) for c in ch)
            if merged:
                pw = sum(weight(c) for c in merged[-1])
                same = fam(h) != 'sha256' or (merged[-1][0]['kind'] in ('pair', 'sched')) == (ch[0]['kind'] in ('pair', 'sched'))
                if same and (pw < 30 or w < 20) and pw + w <= 60:
                    merged[-1] = merged[-1] + ch
                    continue
            merged.append(list(ch))
        # a leftover tiny last unit joins the previous one if it fits in 75 minutes
        if len(merged) > 1 and sum(weight(c) for c in merged[-1]) < 15 and sum(weight(c) for c in merged[-2]) + sum(weight(c) for c in merged[-1]) <= 75:
            last_ = merged.pop()
            merged[-1] += last_
        for n, ch in enumerate(merged, 1):
            mins = int(round(sum(weight(c) for c in ch)))
            mins = max(mins, 10)
            qs = sorted({c['q'] for c in ch})
            qt = QTEXT[fam(h)]
            meth = ' | '.join(qt[q] for q in qs)
            extra = ''
            miss = sorted({m for c in ch for m in (c.get('missing') or [])})
            if miss and fam(h) == 'sha256':
                extra = ' Remaining conditions to drop singly (the rest of this object already has an own record): ' + ', '.join(miss[:60]) + ('...' if len(miss) > 60 else '') + '.'
            why = sorted({c['reason'] for c in ch})
            note = ''
            if h == 'sha3-r6':
                note = ' Specific: ' + ' '.join(R6_NOTE[rd] for rd in sorted({c['round'] for c in ch}))
            elif h == 'sha3-r5':
                note = ' Specific: ' + R5_NOTE
            elif h == 'blake3-r2':
                keys = sorted({('W' if c['kind'] == 'b3word' else c['call']) for c in ch})
                note = ' Specific: ' + ' '.join(B3_NOTE[k] for k in keys)
            elif h in SHA256:
                note = ''
            if h == 'sha256-37' and any(c['row'] in (14, 15) and c['q'] == 'Q2' for c in ch if c['kind'] == 'row'):
                note += (' Specific (Q2 rows 14/15): the dense-row method of research/tools/traillab/row_cards/zoneD_row_08.md (Test A: flip bit b of the word in both members, hold every other value, first row <= 15 whose modular difference breaks; '
                        'Test B on consistent messages through tl_build) with the tool research/tools/traillab/digs/zoneD/zoneD.c; rows 14 and 15 are held by the anchor (atlas_runs/derive-anchor-row14-and-row16, hot-H1-row15-and-W15-per-l), so report the row-local solution count per dropped condition.')
            if h in SHA256 and any(c['q'] == 'Q4' for c in ch):
                note += (' Specific (Q4): list the signed patterns of the modular difference of the object (traillab backward: weight <= 6, see atlas_runs38/R-rows/backward_16_21.txt for the format), '
                        'then run each alternative pattern as the cell through traillab window to the event (relax / dropsign options) and report whether it reaches the same later differences; relations: test the opposite relation (= vs !=) the same way.')
            uid = '%s-U%02d' % (h, n)
            units.append(dict(id=uid, hash=h, scope=scope_text(h, ch), cells=[c['id'] for c in ch], est_minutes=mins,
                              questions=meth + extra + note + ' Why these cells are unscanned: ' + ' / '.join(why)[:700] + ' Existing material (read first, do not redo): ' + HINTS[h]))
            for c in ch:
                c['unit'] = uid
    units += build_gap_units(universe)
    return units


# ----------------------------------------------------------------------------------------------------------- output
def write_outputs(universe, units):
    with open(os.path.join(HERE, 'UNIVERSE.jsonl'), 'w', encoding='utf-8', newline='\n') as f:
        for c in universe:
            d = {k: v for k, v in c.items() if not k.startswith('_')}
            f.write(json.dumps(d, ensure_ascii=False, sort_keys=True) + '\n')
    with open(os.path.join(HERE, 'UNITS.jsonl'), 'w', encoding='utf-8', newline='\n') as f:
        for u in units:
            f.write(json.dumps(u, ensure_ascii=False) + '\n')


def tally(universe):
    T = collections.OrderedDict()
    for h in ['sha256-37', 'sha256-38', 'sha3-r5', 'sha3-r6', 'blake3-r2']:
        cs = [c for c in universe if c['hash'] == h and c.get('group', 'W1') == 'W1']
        d = collections.Counter()
        for c in cs:
            d['universe'] += 1
            if c['state'] == 'SCANNED':
                d['scanned'] += 1
                d['scanned_' + c['basis']] += 1
            elif c['state'] == 'EXCLUDED':
                d['excluded'] += 1
            else:
                d['unscanned'] += 1
        T[h] = d
    return T


def md_table(rows, head):
    out = ['| ' + ' | '.join(head) + ' |', '|' + '---|' * len(head)]
    for r in rows:
        out.append('| ' + ' | '.join(str(x) for x in r) + ' |')
    return out


def write_md(universe, units):
    full = universe
    universe = [c for c in full if c.get('group', 'W1') == 'W1']
    T = tally(universe)
    L = []
    L.append('# COVERAGE - what the row dig has scanned once, and what is left\n')
    L.append('Generated by `research/dig/coverage.py` (pure Python, re-runnable, reads `CELLS.jsonl`, the characteristic files, ATLAS37.md, atlas38_gen.py evidence, row cards and a few result files; writes only `UNIVERSE.jsonl`, `COVERAGE.md`, `UNITS.jsonl`). Do not edit by hand.\n')
    L.append('Rule of this wave: **scan once**. A cell is SCANNED when our own code produced a number or verdict for its question, or when the question is structurally empty (reason recorded in `UNIVERSE.jsonl`). Outside-model claims do not count. When unsure the cell is UNSCANNED. A cell scanned by a result file of a running job that is not yet in CELLS.jsonl is counted SCANNED with basis FILE (pending ingest); the file is named in the cell.\n')
    L.append('## Questions\n')
    L.extend(md_table([[k, v] for k, v in QNAME_SHA256.items()], ['id', 'SHA-256 meaning']))
    L.append('')
    L.extend(md_table([[k, v] for k, v in QNAME_OTHER.items()], ['id', 'SHA3 / BLAKE3 meaning']))
    L.append('\nObjects: SHA-256 rows -4..last, A, E, W and REL (the two-bit relations x2 lines assigned to the row of their earlier endpoint, plus unmatched plus links); rows -4..-1 have A and E only. Interaction cells (i,j) with j-i in 1..4 and every schedule link W_j <- W_i (s1 at j-2, add at j-7, s0 at j-15, add at j-16) carry Q5 only. SHA3: round x {theta, rho, pi, chi, iota}, rounds 0..4 (r5) and 0..5 (r6). BLAKE3: the 64 quarter-steps of GRID_BLAKE3.md (16 G calls K0-3, D0-3, C0-3, E0-3 x q1..q4; the grid prints rounds 0 for K/D/C and 1 for E, kept here as call names) and the 16 message words.\n')
    L.append('## Totals per hash\n')
    rows = []
    for h, d in T.items():
        rows.append([h, d['universe'], d['scanned'], d['scanned_STRUCTURAL'], d['scanned_CELLS'], d['scanned_FILE'], d['excluded'], d['unscanned']])
    L.extend(md_table(rows, ['hash', 'universe', 'scanned', 'of which structural', 'of which CELLS record', 'of which FILE (pending ingest)', 'excluded (running jobs)', 'unscanned']))
    tot = collections.Counter()
    for d in T.values():
        tot.update(d)
    L.append('| **all** | %d | %d | %d | %d | %d | %d | %d |' % (tot['universe'], tot['scanned'], tot['scanned_STRUCTURAL'], tot['scanned_CELLS'], tot['scanned_FILE'], tot['excluded'], tot['unscanned']))
    # per question
    for h in T:
        L.append('\n## %s\n' % h)
        cs = [c for c in universe if c['hash'] == h]
        qs = sorted({c['q'] for c in cs})
        rows = []
        for q in qs:
            sub = [c for c in cs if c['q'] == q]
            rows.append([q, len(sub), sum(c['state'] == 'SCANNED' for c in sub), sum(c['state'] == 'EXCLUDED' for c in sub), sum(c['state'] == 'UNSCANNED' for c in sub)])
        L.extend(md_table(rows, ['question', 'universe', 'scanned', 'excluded', 'unscanned']))
        ex = collections.Counter((c['owner'], c['q']) for c in cs if c['state'] == 'EXCLUDED')
        if ex:
            L.append('\nExcluded (owner, question): ' + '; '.join('%s %s x%d' % (o, q, n) for (o, q), n in sorted(ex.items())) + '.')
        if h in SHA256:
            # per-row grid: state letters per object and question
            L.append('\nPer-row state (S scanned, X excluded, . unscanned; order Q1 Q2 Q3 Q4 for A | E | W | REL):\n')
            chi = CHI[h]
            rows = []
            for r in range(-4, chi.last + 1):
                cellsr = [c for c in cs if c['kind'] == 'row' and c['row'] == r]
                if not cellsr:
                    continue
                parts = []
                for o in ('A', 'E', 'W', 'REL'):
                    sub = {c['q']: c for c in cellsr if c['object'] == o}
                    if not sub:
                        parts.append('-')
                    else:
                        parts.append(''.join({'SCANNED': 'S', 'EXCLUDED': 'X', 'UNSCANNED': '.'}[sub[q]['state']] for q in ('Q1', 'Q2', 'Q3', 'Q4')))
                rows.append([r] + parts)
            L.extend(md_table(rows, ['row', 'A', 'E', 'W', 'REL']))
            q5 = [c for c in cs if c['kind'] in ('pair', 'sched')]
            L.append('\nQ5 (interaction pairs and schedule links): %d cells, %d scanned, %d excluded, %d unscanned.' % (len(q5), sum(c['state'] == 'SCANNED' for c in q5), sum(c['state'] == 'EXCLUDED' for c in q5), sum(c['state'] == 'UNSCANNED' for c in q5)))
        else:
            rows = []
            if h.startswith('sha3'):
                for rd in sorted({c['round'] for c in cs}):
                    row = [rd]
                    for st in ('theta', 'rho', 'pi', 'chi', 'iota'):
                        sub = {c['q']: c for c in cs if c['round'] == rd and c['object'] == st}
                        row.append(''.join({'SCANNED': 'S', 'EXCLUDED': 'X', 'UNSCANNED': '.'}[sub[q]['state']] for q in ('Q1', 'Q2', 'Q3', 'Q4')))
                    rows.append(row)
                L.append('\nPer-round state (Q1 Q2 Q3 Q4; S scanned, X excluded, . unscanned):\n')
                L.extend(md_table(rows, ['round', 'theta', 'rho', 'pi', 'chi', 'iota']))
            else:
                for cl in B3_CALLS:
                    row = [cl]
                    for qi in range(1, 5):
                        sub = {c['q']: c for c in cs if c['kind'] == 'b3step' and c['call'] == cl and c['quarter'] == qi}
                        row.append(B3_CODE[cl][qi - 1] + ' ' + ''.join({'SCANNED': 'S', 'EXCLUDED': 'X', 'UNSCANNED': '.'}[sub[q]['state']] for q in ('Q1', 'Q2', 'Q3', 'Q4')))
                    rows.append(row)
                L.append('\nPer-step state (grid code, then Q1 Q2 Q3 Q4; S scanned, X excluded, . unscanned):\n')
                L.extend(md_table(rows, ['call', 'q1', 'q2', 'q3', 'q4']))
                rows = []
                for w in range(16):
                    sub = {c['q']: c for c in cs if c['kind'] == 'b3word' and c['word'] == w}
                    rows.append(['m%d' % w, ''.join({'SCANNED': 'S', 'EXCLUDED': 'X', 'UNSCANNED': '.'}[sub[q]['state']] for q in ('Q1', 'Q2', 'Q3', 'Q4'))])
                L.append('\nMessage words:\n')
                L.extend(md_table(rows, ['word', 'state']))
    write_gap_md(full, L)
    # units
    L.append('\n## Work units (unscanned cells, grouped; each independent, 1 heavy process, own time limit)\n')
    rows = [[u['id'], u['hash'], u['scope'][:110], len(u['cells']), u['est_minutes']] for u in units]
    L.extend(md_table(rows, ['unit', 'hash', 'scope', 'cells', 'est. min']))
    L.append('\nFull question text and cell ids per unit are in `UNITS.jsonl`; every cell id is in `UNIVERSE.jsonl` with its reason.\n')
    # exclusions
    L.append('## Excluded because a running job owns them\n')
    L.append('Mapping used. A cell already answered by a CELLS.jsonl record of ours, or structurally empty, stays SCANNED even inside an owned area. A result that exists only as a file of the owning running job is NOT counted: the cell stays EXCLUDED with that file named in its reason (not final until the job ingests it).\n')
    L.append('- workflow rows38-full-dig: sha256-38 rows 17..37 Q2, and Q5 (interaction pairs and schedule links) with reader row >= 17. The ATLAS38 evidence table of atlas38_gen.py already decides most of those Q5 cells from atlas_runs38 files; the files are named in the cell reasons.')
    L.append('- workflow close-open-rows-37: sha256-37 W8 signings (row 8 W Q4), E20 signing (row 20 E Q4), per-pattern survival rows 18/19 and 20/21 (Q4 of E and REL rows 18..21), rows 22/24 matrix (W and REL of rows 22 and 24, all of Q2-Q4, Q5 for pairs (22,23), (22,24), (23,24) and the W24<-W22 link), R16x per l (Q4 of E16 and the row-16 relations).')
    L.append('- workflow dense-dig: Q4 of every object of the dense rows (sha256-37 rows <= 15, sha256-38 rows <= 16). Assumption: dense characteristic derivation = alternative dense characteristics = Q4.')
    L.append('- Luna 2 (2nd_openai_workspace): sha256-38 rows -4..16 Q2 and Q3.')
    L.append('- Luna local D180 (SHA3): reading of the assignment as the OPEN/CLAIMED items of GRID_SHA3.md: r5 connector relaxation (chi rounds 0-1 Q2/Q4), r5 rounds 3-4 Markov premise (chi Q1; round 4 Q3), r6 filter (round-5 chi Q3 key/filter joint, Q4 alternative predicates), r6 zero-digest 4-round cores (Q4 of theta and chi in rounds 2..5).')
    L.append('- Luna local D181 (BLAKE3): beta2 other 18 taus and the third-beta row (E1 q2/q3 Q4), carry-pattern alternatives on every probabilistic stage (C1 Q4, E1 q2 Q4, E3 q2-q4 Q4), the coupled omega list (E3 q2-q4 Q2-Q4).')
    L.append('- D182 only keeps the grids current: nothing excluded.\n')
    L.append('## Judgement calls to confirm\n')
    L.append('- The exclusion mapping above is my reading of the owner lists; if a job owns less, the matching cells move to units.')
    L.append('- sha256-37 Q1 is one record (S37-DB-BASIC, pair replay of rows -4..36); sha256-38 Q1 rests on atlas_runs38/A-dense/check.txt (running job, not yet in CELLS).')
    L.append('- sha256-37 Q3 for rows 16..24 rests on row-level numbers (S37-E8-OWN, S37-O10, S37-DB-STAGES): the joint pass cost of the row is attributed to each object of the row that carries a condition.')
    L.append('- Q5 is scanned when the ATLAS cell (i,j) is decided (our measured/proved result for how row i acts on row j); the finer pair-drop records (PAIR-B0..B4) are cited where they have the same coordinates.')
    L.append('- SHA3 rho, pi, iota and the Q1-Q3 of theta are structural (fixed permutation / constant XOR / linear bijection). Round 0 and 1 chi of r5 Q1/Q3 are credited to the connector records C0104-C0108. The r6 round 2-3 chi Q1-Q3 cells are credited to C0122-C0127, which name their cell in the short form `round2.chi|Q1` (read since 2026-10-12, see the gap section).')
    L.append('- BLAKE3 I-coded quarter-steps (K0-K3, D0-D3, C0, C2) are structural (exact inversion, no characteristic layer). C1 conditions sit on Y9 only. Message words are unscanned.')
    L.append('- Known traps respected: the paper prints != as `=` + U+0338 (chi files used, not the PDF); no expanded word W16+ is varied with later words held; UNKNOWN is not UNSAT.\n')
    L.append('## File evidence not yet in CELLS.jsonl (pending ingest)\n')
    files = collections.Counter()
    for c in full:
        if c['basis'] == 'FILE':
            for e in c['evidence']:
                files[e] += 1
    L.extend(md_table([[f, n] for f, n in files.most_common(40)], ['file', 'cells it scans']))
    with open(os.path.join(HERE, 'COVERAGE.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(L) + '\n')


def main():
    universe = evaluate_all()
    units = build_units(universe)
    for c in universe:
        c.setdefault('unit', None)
    write_outputs(universe, units)
    write_md(universe, units)
    T = tally(universe)
    for h, d in T.items():
        print(h, dict(d))
    GT = collections.OrderedDict()
    for c in universe:
        if c.get('group', 'W1') != 'W1':
            GT.setdefault(c['group'], collections.Counter()).update(['universe', c['state'].lower() + ('' if c['state'] != 'SCANNED' else '_' + c['basis'])])
    for g, d in GT.items():
        print(g, dict(d))
    selfcheck(universe, units)
    print('units', len(units), 'minutes', sum(u['est_minutes'] for u in units))


# ===================================================================================================== blake3-r3 (added 2026-10-12)
# 3 rounds = 24 G calls (per round: 4 column calls R<r>C0..3, then 4 diagonal calls R<r>D0..3), 4 quarter-steps x Q1..Q4, the 16 message
# words, the r2 families INIT OUT MODE MSG PIN PREM LEDGER MEM JUDGE DOOR, and three families for the Pareto challenge (score =
# time_log2 + max(0, log2(memory bytes) - 20)): MACHINE, GENERIC, ALT.  Group R3 (not W1: the wave-1 universe of the other targets is unchanged).
# Scanned only through R3MAP below (existing evidence: proposed_cells.jsonl records, submission-note.md, the first ruling); default UNSCANNED.
R3 = 'blake3-r3'
R3_PROP = 'research/blake3_r3/proposed_cells.jsonl'
R3_NOTE = 'research/blake3_r3/submission-note.md'
R3_RULING = 'research/blake3_r3/ruling_77715f8b/reports/tracks/blake3-pareto/aggregate.json'
R3_SWAR = 'research/blake3_r3/swar_count.py'
_R3_ORD = [list(range(16)), list(_PERM), [_PERM[x] for x in _PERM]]   # message order of round r = BLAKE3 permutation applied r times

R3_MACHINE = [
    ('WIDTH', 'word width (bits per register operation)', '256-bit words, seven 36-bit lanes per word (SWAR); the organizer count 638 is per 32-bit-word operation', 'machine'),
    ('REGS', 'register count', '64 registers; the note says fewer than about 40 would force loads and stores in the main loop (not tested)', 'machine'),
    ('IMM', 'immediates', '256-bit immediates; constants folded at build time', 'machine'),
    ('ROT', 'rotation cost', 'rotations built from shifts and two masks that also remove guard-bit garbage; charged as ordinary operations', 'machine'),
    ('CMPBR', 'compare and branch', 'distinguished-point filter 4 operations per batch, loop control 3 per 16 batches; every compare and branch counted', 'machine'),
    ('MEMTRAF', 'memory traffic (loads / stores)', 'main loop has none (16 state + 8 message words + temporaries in registers, no register moves charged); table accesses and recovery charged with their loads and stores', 'machine'),
]
R3_GENERIC = [
    ('DPFRAC', 'distinguished-point fraction', 'low 114 bits zero (fraction 2^-114) on the 256-bit chain; DP bits 4 in the n = 22 experiment', 'generic'),
    ('CHAINLEN', 'trail (chain) length', 'mean length near 2^114, 2^14 trails started from r + t; halts at the stated limits', 'generic'),
    ('SUCC', 'success probability', 'at least 0.39 per attempt (single attempt, 0.99885 * 2^128 evaluations); losses about 1.2e-4 of 1.5e-3', 'generic'),
    ('ATT', 'attempts / restarts / amplification', 'single attempt, one fresh 256-bit word, no restart, no stored collision; other attempt counts change time_log2 and the success factor', 'generic'),
    ('RECOV', 'recovery of the colliding pair', 'aligns the two stored trail lengths and walks to the merge; charged at most 12 * 2^114 + 2^48 batches; judged UNDERCHARGED (lane_cost/F1-recovery-undercharge)', 'generic'),
    ('SETUP', 'setup / table build', '18,432 table keys halt; setup charged at its limit; no advice, preprocessing 2^2', 'generic'),
]
R3_ALT = [
    ('DIFF', 'differential (message-difference sets, word-level checks left in the digest)', 'our word-level model: for message-difference sets of size <= 3 at best 6 of 8 digest words silenced after round 3; D={4,5} line gives 8 checks (all 256 bits)', 'alt'),
    ('ROTAT', 'rotational / rotation-invariant relations', 'no own test; BLAKE3 rotates words by 16,12,8,7 and adds constants, rotational pairs survive only with constant corrections', 'alt'),
    ('ALGDEG', 'algebraic degree / higher-order structure of 3 rounds', 'no own test; degree growth of the digest bits after 3 rounds, cube / zero-sum style distinguishers', 'alt'),
    ('NEUTRAL', 'neutral bits / message modification', 'no own test at 3 rounds; the 2-round line used inversion of the first quarter-steps (free words give a bijection)', 'alt'),
    ('NEAR', 'near-collision of first-block chaining values plus a free final block', 'B3R3-C1: stage A 2^112 x 0.14 = 2^109.1 for a 224-bit near-collision, stage B word-level model gives 8 checks (generic 2^128) unless pins exist; OPEN, not tested', 'alt'),
    ('MULTI', 'multi-block chunk (h = previous block output, CHUNK_START / middle / CHUNK_END)', 'no own test at 3 rounds', 'alt'),
    ('CHUNK', 'chunk and tree structure (parent compressions, several chunks)', 'no own test at 3 rounds; the pairing closure P1 is for the single-block message words only', 'alt'),
    ('FLAGS', 'flag choices (CHUNK_START / END / ROOT / KEYED / PARENT)', 'record uses flags 11; other flag words move a state word v15 difference or constant', 'alt'),
    ('COUNTER', 'counter modes (chunk counter t_lo, t_hi, block length)', 'record uses counter 0 and block length 64; counters are free state words for a multi-chunk message', 'alt'),
]
R3_PIN = [
    ('K', 'key words m0..m7 = 0 (message prefix 0^32)', 'the filed target fixes the first 32 message bytes to zero; no advice (m0..m7 = 0)', 'pin'),
    ('X', 'chain input words m8..m15 = x (identity embedding)', 'the 256-bit chain x -> digest(0^32 || x); all 256 bits are the free input', 'pin'),
    ('BLEN', 'block length 64', 'two 64-byte messages 0^32 || x and 0^32 || y, one chunk, one block', 'pin'),
    ('FLG', 'flags 11 (CHUNK_START | CHUNK_END | ROOT)', 'single block root compression, unkeyed, standard IV', 'pin'),
]
R3_OUT = [('d%d' % i, 'digest word %d = Z[%d] ^ Z[%d] after 3 rounds' % (i, i, i + 8),
           'complete 256-bit digest, all eight words required equal; no pinned word in the generic line', 'out') for i in range(8)]
R3_OUT.append(('hi', 'second root half v[i+8] ^ h[i] (not in the digest)', 'the digest is the first 32 bytes of the root output', 'out'))
R3_MODE = list(B3_MODE)
R3_DOORS = [(k, l, 'RE-ASK AT 3 ROUNDS of the r2 door: ' + f, c) for (k, l, f, c) in B3_DOORS]
R3_MEM = [
    ('DPTAB', 'distinguished-point table', '18,432 entries x 32 B = 589,824 B', 'mem'),
    ('CODE', 'written-out code', 'at most 374,400 B (unrolled body of 595 operations x copies)', 'mem'),
    ('CNT', 'counters and working words', 'below 2,048 B; total 966,272 B = 2^19.88, claimed as 2^20 so the memory term of the score is 0', 'mem'),
]
R3_PREM = [
    ('H1', 'H1-random-mapping (score-critical): f(x) = digest(0^32 || x) behaves as a random mapping on 2^256 points', 'T1 fresh-key chains at widths 32/40, T2 fixed target projections, T3 shipped search on target vs ideal function; extrapolation to 256 bit is by the premise only', 'prem'),
    ('H2', 'H2-loss-terms: losses of Section 4 (unfinished and cut trails, repeats, key false matches, aborts)', 'about 1.2e-4 spent of 1.5e-3 available; success >= 0.39 holds for eps <= 0.0047', 'prem'),
    ('H3', 'H3-machine-convention: ledger counted in the convention of the organizer count C(r3) = 638', 'data-path operations on 256-bit words, no charge for register moves, loads and stores in the main loop', 'prem'),
]
R3_LEDGER = [
    ('LOOP', 'main loop: 595 operations per batch of 7 chain steps (85 per step, 0.133 compression)', 'per-round totals 116 + 232 + 235 + 12; 99.44 percent of the total (2.9258e40 operations = 4.586e37 units); note 125.1087, claim 125.1081, proposed cell B3R3-G1 88.0 ops/evaluation and 125.134', 'led'),
    ('DPF', 'distinguished-point filter (4 operations per batch)', 'charged per batch', 'led'),
    ('CTRL', 'loop control (3 operations per 16 batches)', 'charged per 16 batches', 'led'),
    ('EVALS', 'evaluations: 0.99885 * 2^128 points', 'note; B3R3-G1 states q = 0.9943 * 2^128 for plain birthday', 'led'),
    ('RECOV', 'recovery: at most 12 * 2^114 + 2^48 batches, one recovery', 'judged undercharged (ruling 77715f8b)', 'led'),
    ('SETUP', 'setup, halt budgets (B batches, E2 events, 18,432 keys)', 'every halt budget charged at its limit', 'led'),
]
R3_JUDGE = [
    ('JRECOV', 'REFUTED: lane_cost/F1-recovery-undercharge (ruling 77715f8b, blake3-pareto, exploratory lane, policy paired-lanes-v1)', 'recovery step charged below what the program can execute; claim 125.1081 at that ruling', 'judge'),
]


def build_blake3_r3_universe():
    cells = []
    for r in range(3):
        for k in 'CD':
            for i in range(4):
                call = 'R%d%s%d' % (r, k, i)
                for qi in range(1, 5):
                    for q in ('Q1', 'Q2', 'Q3', 'Q4'):
                        cells.append(mk(R3, 'b3step', '%s.q%d' % (call, qi), 'step', q, call=call, quarter=qi, code='U', round=r, group='R3',
                                        label='G call %s quarter-step q%d (round %d, %s)' % (call, qi, r, 'column' if k == 'C' else 'diagonal'),
                                        facts='3-round BLAKE3, no inversion shortcut assumed: the cell asks the question for this quarter-step', cl='step'))
    for w in range(16):
        for q in ('Q1', 'Q2', 'Q3', 'Q4'):
            cells.append(mk(R3, 'b3word', 'm%d' % w, 'msgword', q, word=w, group='R3', label='message word m%d' % w,
                            facts='used at three G-call positions (rounds 0..2); zero key word / chain word in the filed target', cl='word'))
    for r in range(3):
        for gi in range(8):
            call = 'R%d%s%d' % (r, 'C' if gi < 4 else 'D', gi % 4)
            for xy, w in (('x', _R3_ORD[r][2 * gi]), ('y', _R3_ORD[r][2 * gi + 1])):
                cells.append(gc(R3, 'R3', 'b3msg', 'MSG.%s.%s' % (call, xy), 'MSG', 'Q1',
                                'read %s of call %s = message word m%d' % (xy, call, w),
                                'one cell per (round, G, position); the word cells m%d merge the uses' % w, 'msg', word=w, call=call))
    Q4s = ('Q1', 'Q2', 'Q3', 'Q4')
    cells += _expand(R3, 'R3', 'b3init', 'INIT', Q4s, B3_INIT)
    cells += _expand(R3, 'R3', 'b3pin', 'PIN', Q4s, R3_PIN)
    cells += _expand(R3, 'R3', 'b3out', 'OUT', Q4s, R3_OUT)
    cells += _expand(R3, 'R3', 'b3mode', 'MODE', Q4s, R3_MODE)
    cells += _expand(R3, 'R3', 'b3door', 'DOOR', ('D1',), R3_DOORS)
    cells += _expand(R3, 'R3', 'prem', 'PREM', ('R1', 'R2', 'R3', 'R4'), R3_PREM)
    cells += _expand(R3, 'R3', 'ledger', 'LEDGER', ('R1', 'R2', 'R3', 'R4'), R3_LEDGER)
    cells += _expand(R3, 'R3', 'judge', 'JUDGE', ('R1', 'R2', 'R3', 'R4'), R3_JUDGE)
    cells += _expand(R3, 'R3', 'mem', 'MEM', ('M1', 'M2', 'M3', 'M4'), R3_MEM)
    cells += _expand(R3, 'R3', 'machine', 'MACHINE', Q4s, R3_MACHINE)
    cells += _expand(R3, 'R3', 'generic', 'GENERIC', Q4s, R3_GENERIC)
    cells += _expand(R3, 'R3', 'alt', 'ALT', Q4s, R3_ALT)
    return cells


# --- evidence map: object.loc -> {question: (files, why)}; everything not listed is UNSCANNED
R3MAP = {}


def _r3(obj_loc, qs, files, why):
    for q in qs.split():
        R3MAP.setdefault(obj_loc, {})[q] = (files.split(), why)


for _v in range(16):
    _r3('INIT.v%d' % _v, 'Q1', R3_NOTE, 'value as used: standard IV (v0..v11), counter 0 (v12, v13), block length 64 (v14), flags 11 (v15), unkeyed (submission note)')
for _k in 'K X BLEN FLG'.split():
    _r3('PIN.' + _k, 'Q1', R3_NOTE, 'value as used: 0^32 || x, 64-byte block, flags 11 (submission note)')
for _i in range(8):
    _r3('OUT.d%d' % _i, 'Q1', R3_NOTE, 'complete 256-bit digest, all eight words compared (submission note)')
_r3('OUT.hi', 'Q1', R3_NOTE, 'not in the digest: the digest is the first 32 bytes (submission note)')
_r3('MODE.single', 'Q1', R3_NOTE, 'single-block root compression, one chunk, counter 0, flags 11 is the filed mode (submission note)')
_r3('MODE.len', 'Q1', R3_NOTE, 'length 64 used (submission note); other lengths untested')
for _k in 'WIDTH REGS IMM ROT CMPBR MEMTRAF'.split():
    _r3('MACHINE.' + _k, 'Q1', R3_NOTE, 'machine convention (H3) of the filed program as stated in the note section "Machine convention (H3)"')
_r3('GENERIC.DPFRAC', 'Q1', R3_NOTE, 'DP rule: low 114 bits zero (note)')
_r3('GENERIC.CHAINLEN', 'Q1', R3_NOTE + ' ' + R3_RULING, 'mean trail length near 2^114, 2^14 trails (ruling claim, H1 scope)')
_r3('GENERIC.CHAINLEN', 'Q2', R3_PROP, 'B3R3-T1 (SAMPLED, own rho_tag.c): first-repeat time of the genuine chain at n = 32/40 within a few percent of the random-mapping law; 2 rounds n = 32 too')
_r3('GENERIC.SUCC', 'Q1 Q2', R3_NOTE, 'success >= 0.39 single attempt; loss terms 1.2e-4 of 1.5e-3 and the eps <= 0.0047 margin (note, Numbers and Limits)')
_r3('GENERIC.ATT', 'Q1', R3_NOTE, 'single attempt, no amplification (note)')
_r3('GENERIC.RECOV', 'Q1', R3_NOTE + ' ' + R3_RULING, 'charged at most 12 * 2^114 + 2^48 batches; the first ruling refuted it as undercharged (lane_cost/F1-recovery-undercharge)')
_r3('GENERIC.SETUP', 'Q1', R3_NOTE, 'setup and halt budgets charged at their limits (note)')
_r3('ALT.DIFF', 'Q1', R3_PROP, 'B3R3-X1 (COMPUTED, word-level model): size <= 3 sets leave at most 6 silenced words at round 3, D={4,5} gives 8 checks; vacuous for |D| >= 4')
_r3('ALT.DIFF', 'Q3', R3_PROP, 'B3R3-P1 (BEDROCK, union-find on the permutation): no pair-closed message-difference set below the full 16 words after 3 rounds')
_r3('PREM.H1', 'R1', R3_NOTE + ' ' + R3_RULING, 'premise text and evidence ids stated in the package and in the ruling claim')
_r3('PREM.H1', 'R2', R3_NOTE + ' ' + R3_PROP, 'own re-measurements T1/T2/T3 (note) and B3R3-T1 (SAMPLED): fresh-key chains n = 32/40, target projections, shipped search vs ideal function')
_r3('PREM.H1', 'R3', R3_NOTE, 'T3 control: the shipped search on an ideal function of the same width (note)')
_r3('PREM.H2', 'R1', R3_NOTE + ' ' + R3_RULING, 'about 1.2e-4 spent of 1.5e-3 (ruling claim)')
_r3('PREM.H3', 'R1', R3_NOTE + ' ' + R3_RULING, 'machine convention stated (note, ruling claim)')
_r3('LEDGER.LOOP', 'R1', R3_NOTE, '595 operations per 7 steps, 99.44 percent of the total (note)')
_r3('LEDGER.LOOP', 'R2', R3_PROP + ' ' + R3_SWAR, 'B3R3-G1 (COMPUTED): own SWAR count 88.0 word ops per evaluation; differs from the filed 85 per step')
_r3('LEDGER.LOOP', 'R3', R3_PROP + ' ' + R3_SWAR, 'B3R3-G1: lanes checked against verifier/blake3.py on 64-byte messages (known answer)')
for _k in 'DPF CTRL EVALS RECOV SETUP'.split():
    _r3('LEDGER.' + _k, 'R1', R3_NOTE, 'value charged as stated in the note')
_r3('LEDGER.EVALS', 'R2', R3_PROP, 'B3R3-G1 (COMPUTED): q = 0.9943 * 2^128 for plain birthday on the complete digest; differs from the filed 0.99885')
_r3('JUDGE.JRECOV', 'R1', R3_RULING, 'cause present in the first package: reasons = [lane_cost/F1-recovery-undercharge], status refuted')
for _k in 'DPTAB CODE CNT'.split():
    _r3('MEM.' + _k, 'M1', R3_NOTE + ' ' + R3_RULING, 'bytes held: 589,824 + at most 374,400 + below 2,048 = 966,272 B = 2^19.88 (stated bound; ruling claim)')


def eval_r3(c):
    spec = R3MAP.get(c['loc'], {}).get(c['q'])
    if spec is None:
        if c['loc'] == 'ALT.NEAR':
            return unscanned('B3R3-C1 (status OPEN, own_test false, estimates only: 2^109.1 for stage A) is not a test')
        return unscanned('no existing evidence answers this question for this blake3-r3 object')
    files, why = spec
    miss = [f for f in files if not exists(f)]
    if miss:
        return unscanned('mapped evidence file(s) missing: ' + ' '.join(miss))
    return scanned_file(files, why)


def r3_weight(c):
    if c['kind'] in ('machine', 'generic', 'alt'):
        return 10.0
    if c['kind'] == 'b3step':
        return {'Q1': 4.0, 'Q2': 6.0, 'Q3': 6.0, 'Q4': 8.0}[c['q']]
    if c['kind'] == 'b3word':
        return 5.0
    if c['kind'] == 'b3door':
        return 20.0
    if c['kind'] in ('ledger', 'judge', 'prem'):
        return 6.0
    return 4.0


def build_r3_cells():
    out = []
    for c in build_blake3_r3_universe():
        r = eval_r3(c)
        if r['state'] != 'SCANNED' and c['id'] in NAMED:
            r = scanned_cells(NAMED[c['id']], 'own-test record(s) naming this universe cell')
        c.update(r)
        out.append(c)
    return out


R3_METHOD = ('BLAKE3 3 ROUNDS (blake3-r3, target blake3-r3-prefix-v1: 0^32 || x, one block, flags 11, complete 256-bit digest; score = time_log2 + max(0, log2(memory bytes) - 20)). '
             'Answer only the listed questions per object. Q1 value/count as used; Q2 necessity (change it, recount the exact outcome); Q3 degrees of freedom or score-optimal value; Q4 alternatives; '
             'R1-R4 premise/ledger/judge (value charged, own recount, control, score sensitivity); M1-M4 memory; D1 the RELABEL test of the r2 door run at 3 rounds. '
             'Validate any BLAKE3 code first on full 7-round vectors and against hash-smash/verifier/blake3.py, then run at 3 rounds. Own code only (own_test true).')
R3_HINT = ('research/blake3_r3/ (ANALYSIS.md, proposed_cells.jsonl, submission-note.md, swar_count.py, rho_tag.c, ruling_77715f8b/); research/dig/CELLS.jsonl; for the structure of the G-step cells the 2-round material '
           'research/tools/traillab/ATLAS_BLAKE3.md and b3atlas/. Do not redo B3R3-G1, X1, P1, T1.')


def build_r3_units(universe):
    cs = [c for c in universe if c['hash'] == R3 and c['state'] == 'UNSCANNED']
    units = []
    state = {'cur': [], 'w': 0.0}

    def flush():
        cur = state['cur']
        if not cur:
            return
        uid = '%s-U%02d' % (R3, len(units) + 1)
        for c in cur:
            c['unit'] = uid
        lines = collections.OrderedDict()
        for c in cur:
            lines.setdefault(c['loc'], []).append(c['q'])
        txt = R3_METHOD + ' Cells: ' + ' '.join('%s [%s]' % (k, ' '.join(v)) for k, v in lines.items()) + ' Existing material (read first, do not redo): ' + R3_HINT
        units.append(dict(id=uid, hash=R3, group='R3', scope='%s: %s' % (cur[0]['cl'], ', '.join(list(lines)[:6]) + (' ...' if len(lines) > 6 else '')),
                          cells=[c['id'] for c in cur], est_minutes=max(10, min(60, int(round(sum(r3_weight(c) for c in cur)) + 8))), questions=txt))
        state['cur'], state['w'] = [], 0.0

    atoms = collections.OrderedDict()
    for c in cs:
        atoms.setdefault(c['loc'], []).append(c)
    for loc, a in atoms.items():
        aw = sum(r3_weight(c) for c in a)
        if state['cur'] and (state['w'] + aw > 48.0 or state['cur'][0]['cl'] != a[0]['cl']):
            flush()
        state['cur'] = state['cur'] + a
        state['w'] += aw
    flush()
    return units


_evaluate_all_w1 = evaluate_all


def evaluate_all():
    return _evaluate_all_w1() + build_r3_cells()


_build_units_w1 = build_units


def build_units(universe):
    return _build_units_w1(universe) + build_r3_units(universe)


_write_md_w1 = write_md


def write_md(universe, units):
    _write_md_w1(universe, units)
    r3 = [c for c in universe if c['hash'] == R3]
    L = ['\n## blake3-r3 (3 rounds; group R3, added 2026-10-12)\n',
         'The BLAKE3 3-round line, walked like the other targets. 24 G calls (R<round>C0..3 columns, R<round>D0..3 diagonals; message order of round r is the BLAKE3 permutation applied r times) x 4 quarter-steps x Q1..Q4, 16 message words x Q1..Q4, '
         'the r2 families INIT OUT MODE MSG PIN PREM LEDGER MEM JUDGE DOOR, and for the Pareto score (time_log2 + max(0, log2(memory bytes) - 20)) MACHINE, GENERIC, ALT. '
         'Scanned only from existing evidence: B3R3-G1/X1/P1/T1 of research/blake3_r3/proposed_cells.jsonl (basis FILE, pending ingest; B3R3-C1 is OPEN and scans nothing), research/blake3_r3/submission-note.md and the first ruling 77715f8b (refuted: lane_cost/F1-recovery-undercharge). '
         'No CELLS.jsonl record exists for blake3-r3 yet. Wave-1 universe and all other targets are unchanged.\n']
    fams = collections.OrderedDict()
    for c in r3:
        k = {'b3step': 'STEP', 'b3word': 'WORD'}.get(c['kind'], c['object'])
        fams.setdefault(k, []).append(c)
    rows = [[k, len(cs), sum(c['state'] == 'SCANNED' for c in cs), sum(c['state'] == 'UNSCANNED' for c in cs)] for k, cs in fams.items()]
    rows.append(['**all**', len(r3), sum(c['state'] == 'SCANNED' for c in r3), sum(c['state'] == 'UNSCANNED' for c in r3)])
    L.extend(md_table(rows, ['family', 'cells', 'scanned', 'unscanned']))
    L.append('\nScanned cells and their evidence:\n')
    L.extend(md_table([[c['id'].split('|', 1)[1], c['reason'][:150]] for c in r3 if c['state'] == 'SCANNED'], ['cell', 'reason']))
    with open(os.path.join(HERE, 'COVERAGE.md'), 'a', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(L) + '\n')


_main_w1 = main


def main():
    _main_w1()
    T = collections.Counter()
    for l in open(os.path.join(HERE, 'UNIVERSE.jsonl'), encoding='utf-8'):
        d = json.loads(l)
        if d['hash'] == R3:
            T['universe'] += 1
            T[d['state'].lower()] += 1
    print('blake3-r3', dict(T))



# ===================================================================================================== poseidon-r1 / poseidon-r2 (added 2026-10-12)
# Orchard Poseidon P128Pow5T3 over Pallas, t = 3, x^5.  r1: full rounds 0-3, ONE partial round (P1), full rounds 60-63 (9 rounds);
# r2: two partial rounds (P1, P2) (10 rounds).  Digest = lane 0 of the final state; ordinary collision; score = time_log2 + max(0, log2(bytes) - 20).
# Cells: round x lane x layer (ARC, SBOX, MDS) x Q1..Q4, plus families LINE POLY ROOT LEDGER MEM PREM JUDGE MACHINE ALT DOOR.
# Group PO (not W1; no other target's universe changes).  Scanned only through POMAP (existing evidence); default UNSCANNED.
PO1, PO2 = 'poseidon-r1', 'poseidon-r2'
PO_HASHES = (PO1, PO2)
_PD = 'research/poseidon/'
PO_ATLAS = _PD + 'levels/atlas/ATLAS_POSEIDON.md'
PO_FDEG = _PD + 'levels/atlas/facts_degree_output.txt'
PO_LEVELS = _PD + 'levels/LEVELS.md'
PO_LLED = _PD + 'orchard/lean_r1/logs/final_ledger.txt'
PO_LNOTE = _PD + 'orchard/lean_r1/submission-note.md'
PO_LPROOF = _PD + 'orchard/lean_r1/pkg_stage/proof.md'
PO_D189 = 'research/sol_answer_D189_poseidon_learning.md'
PO_D189R = _PD + 'd189_gpu_results.jsonl'


def _l3(n):
    return '3rd_openai_workspace/luna3/' + n


PO_L3A = _l3('ANSWER.md')

PO_LAYERS = ('ARC', 'SBOX', 'MDS')


def po_rounds(r):
    return ['R0', 'R1', 'R2', 'R3'] + ['P%d' % i for i in range(1, r + 1)] + ['R60', 'R61', 'R62', 'R63']


def po_degrees(r):
    """generic (nk,rho)-degree per lane after ARC, SBOX, MDS of every round (ATLAS section 5 rule: S-box multiplies by 5, dense M takes the maximum; lane 2 starts constant)"""
    d, out = [1, 1, 0], {}
    for rl in po_rounds(r):
        full = not rl.startswith('P')
        after_c = list(d)
        after_s = [5 * x for x in d] if full else [5 * d[0], d[1], d[2]]
        m = max(after_s)
        d = [m, m, m]
        out[rl] = (after_c, after_s, list(d))
    return out


def build_poseidon_universe(h):
    r = 1 if h == PO1 else 2
    degs = po_degrees(r)
    cells = []
    for rl in po_rounds(r):
        full = not rl.startswith('P')
        for lane in range(3):
            for li, layer in enumerate(PO_LAYERS):
                if layer == 'ARC':
                    f = 'adds the round constant to lane %d; affine' % lane
                elif layer == 'SBOX':
                    f = ('x^5 on lane %d' % lane) if (full or lane == 0) else 'identity on lane %d (partial round: S-box on lane 0 only)' % lane
                else:
                    f = 'dense MDS row %d (M is the same in every round); linear' % lane
                f += '; generic (nk,rho)-degree after this layer %d (ATLAS section 5)' % degs[rl][li][lane]
                for q in ('Q1', 'Q2', 'Q3', 'Q4'):
                    cells.append(gc(h, 'PO', 'posrnd', '%s.L%d.%s' % (rl, lane, layer), 'RND', q,
                                    '%s %s lane %d %s' % ('round' if full else 'partial round', rl, lane, layer), f, rl))
    Q4s = ('Q1', 'Q2', 'Q3', 'Q4')
    R4s = ('R1', 'R2', 'R3', 'R4')
    M4s = ('M1', 'M2', 'M3', 'M4')
    n = 5 ** (6 + r)
    cells += _expand(h, 'PO', 'poline', 'LINE', Q4s, [
        ('SKIP', 'two-free-round skip: on the line j = 0 the state after round 1 is affine in W = tau^5', 'rounds 0 and 1 cost no degree on the line; digest polynomial F(W) of degree 5^%d = %d' % (6 + r, n), 'line'),
        ('LINEJ', 'choice of the line (j = 0, 1, 2; the three canonical lines)', 'identity checked for every j on the pinned constants; which line is score-best is a separate question', 'line'),
        ('CENTRE', 'uniform centre c and the symmetric difference h(s) = F(c+s) - F(c-s) = s g(s^2)', 'odd part g, one nonzero-square root S of g gives the collision W = c +- sqrt(S)', 'line'),
        ('BACKMAP', 'map back from the line parameter W to the two inputs (nk, rho)', 'sqrt, then the line parametrisation; the two inputs are rehashed with the reference', 'line'),
        ('BYPASS', 'other rational curves that skip round 2 as well', 'P3.2 plane-relation proof for curves preserving the round-1 affine trail; outside that condition open', 'line'),
        ('LANE0', 'aim lane 0 after round 3 (the pair set with equal lane 0 at the R3-R4 interface)', 'the pair set is a curve; the first partial round keeps equality only on a hinge subset', 'line'),
    ])
    cells += _expand(h, 'PO', 'popoly', 'POLY', Q4s, [
        ('DEG', 'degree of the digest polynomial F on the line', 'exactly 5^%d = %d (no cancellation seen on random lines)' % (6 + r, n), 'poly'),
        ('ODD', 'odd part g(S), S = s^2: degree and shape', 'degree (5^%d - 1)/2 = %d, monic' % (6 + r, (n - 1) // 2), 'poly'),
        ('MONIC', 'leading coefficient of g and the monic normalisation', 'nonzero leading coefficient (leading-coefficient tracker)', 'poly'),
        ('SQFREE', 'squarefreeness of g and the repeated-factor degree', 'D189: 20 of 20 odd parts squarefree at r = 1', 'poly'),
        ('COEF', 'coefficient vector of g: how it is built (evaluations + inverse NTT)', 'dense vector of %d field elements (32 B each)' % ((n - 1) // 2), 'poly'),
        ('SHIFT', 'Taylor shift of F to the centre (factorial convolution)', 'one shift per centre; streamed (truncated) variant priced by Luna 3', 'poly'),
        ('EVALN', 'number of line evaluations and their price as target-compression units', 'filed r = 1 line: 98,304 evaluations for an inverse NTT of size 49,152', 'poly'),
    ])
    cells += _expand(h, 'PO', 'poroot', 'ROOT', Q4s, [
        ('POWER', 'power map S^((p-1)/2) mod g (nonzero-square test)', 'about 253 squarings of a degree-%d polynomial modulo g' % ((n - 1) // 2), 'root'),
        ('NTT', 'NTT schedule of the power map (in-place, no stored spectra, row-wise operand transforms)', 'size 2^k transforms, cached reciprocal for the reduction', 'root'),
        ('HGCD', 'gcd(g, S^h - 1) by half-gcd (or classical Euclid)', 'half-gcd recurrence vs in-place Euclid', 'root'),
        ('SPLIT', 'root splitting of the gcd (degree 1, 2, ... fibre sizes)', 'a gcd of degree d needs a split; D189 saw gcd degrees 1 and 2 with witnesses', 'root'),
        ('NEWTON', 'Newton inverse (reciprocal of the modulus) for the reduction', 'one reciprocal per modulus', 'root'),
    ])
    cells += _expand(h, 'PO', 'poledger', 'LEDGER', R4s, [
        ('INIT', 'init: twiddle table and roots of unity (once per run)', 'filed r = 1: 17,359 arith + 20,480 other = 37,839', 'led'),
        ('SETUP', 'line setup (constants of the line, one inversion)', 'filed r = 1: 391 arith + 1,564 other', 'led'),
        ('BUILDG', 'build g: line evaluations, inverse NTT', 'filed r = 1: 1,436,260 arith + 24,567,311 other per centre (evaluations charged as units)', 'led'),
        ('POWER', 'S^((p-1)/2) mod g', 'filed r = 1: 3.5368e9 arith + 2.7048e9 other per centre', 'led'),
        ('GCD', 'half-gcd', 'filed r = 1: 3.5577e8 arith + 4.345e8 other per centre', 'led'),
        ('ROOTS', 'root finding, sqrt, map back', 'filed r = 1: a few tens of thousands of operations', 'led'),
        ('VERIFY', 'verification: two reference hashes', 'filed r = 1: 474 arith + 1,896 other', 'led'),
        ('TOTAL', 'total in target-compression units and time_log2', 'filed r = 1: 14,115,800,161 operations = 59,560,338 units (C(1) = 237), log2 25.8278; time_log2 25.837 in the note', 'led'),
        ('CENTRES', 'number of independent centres charged (worst case)', 'filed r = 1: at most two centres, 25.837; one centre 24.838', 'led'),
    ])
    cells += _expand(h, 'PO', 'pomem', 'MEM', M4s, [
        ('GBUF', 'coefficient buffer of g', 'one dense vector: %s B' % ('1,250,016' if r == 1 else '6,250,016'), 'mem'),
        ('PEAK', 'peak of the whole pipeline', 'filed r = 1: heap peak 8,468,640 B, total 8,636,079 B = 2^23.042', 'mem'),
        ('TWID', 'twiddle table and constants', 'filed r = 1: 16384 entries', 'mem'),
        ('RULE', 'memory term of the score: max(0, log2 bytes - 20)', 'filed r = 1: 3.042 bits of the 28.879', 'mem'),
        ('SHRINK', 'smaller-memory variants (streamed shift, in-place Euclid, tableless NTT)', 'priced by Luna 3; lean_r1_mem is a running job', 'mem'),
    ])
    cells += _expand(h, 'PO', 'poprem', 'PREM', R4s, [
        ('HPOIS', 'H1 Poisson root-count premise: success 1 - exp(-1) = 0.632 for the fixed-value method', 'the one score-critical heuristic of the filed note (claims 0.60)', 'prem'),
        ('HSQ', 'odd-part method: P(g has a nonzero square root) = 1 - exp(-1/2) = 0.3935 per centre', 'D189: 8 of 20 real centres', 'prem'),
        ('HSQFREE', 'g is squarefree', 'D189: 20 of 20', 'prem'),
        ('HCENT', 'number of centres the success claim relies on (one or two)', 'filed r = 1 charges two centres in the worst case', 'prem'),
        ('HUNIF', 'random-coefficient model of g (uniform coefficients)', 'toy p = 257 one-centre success 0.367-0.404', 'prem'),
    ])
    cells += _expand(h, 'PO', 'pojudge', 'JUDGE', R4s, [
        ('JFILED', 'the ruling on the filed entry (651c0ca6 at r = 1)', 'filed 2026-10-12, under validation when the universe was built', 'judge'),
        ('JRUNNER', 'experiment runner cannot size the Orchard digest (digest(b"") rejected): no Python experiment declared', 'stated in the filed note', 'judge'),
        ('JHEUR', 'score-critical heuristic H1 accepted or flagged by the judge', 'note declares H1 as the one heuristic', 'judge'),
    ])
    cells += _expand(h, 'PO', 'pomachine', 'MACHINE', Q4s, [
        ('FMUL', 'field multiplication and squaring: operations charged per product', 'filed r = 1 instrumented: mul 2,470,953,120, sqr 66,646,268', 'machine'),
        ('FADD', 'field addition and subtraction', 'filed r = 1: add 2,715,539,688, sub 2,534,837,889', 'machine'),
        ('LDST', 'loads and stores', 'filed r = 1: ld 2,997,163,555, st 1,663,304,782 charged as other operations', 'machine'),
        ('ADDR', 'addressing arithmetic and index computation', 'not itemised separately in the ledger', 'machine'),
        ('CTL', 'loop control and branches', 'filed r = 1: ctl 1,620,758,761', 'machine'),
        ('REGS', 'register budget and spills', 'not stated', 'machine'),
    ])
    cells += _expand(h, 'PO', 'poalt', 'ALT', Q4s, [
        ('FUNCDEC', 'functional decomposition of the permutation', 'wall to test', 'alt'),
        ('FREELUNCH', 'FreeLunch (algebraic attack on reduced-round Poseidon)', 'wall to test', 'alt'),
        ('CHEAPLUNCH', 'CheapLunch (cheaper variant of the free-round attack)', 'wall to test', 'alt'),
        ('GKR', 'GKR / subspace trail', 'wall to test', 'alt'),
        ('BACKSKIP', 'backward skip (inverse x^5, output lines affine after inverse)', 'P3.12 toy exhaustive q = 23/43', 'alt'),
        ('ZEROSUM', 'zero-sum / additive-fibre structure', 'P3.14: centred sums vanish, digests stay distinct', 'alt'),
        ('INTERP', 'interpolation of the full polynomial in (nk, rho)', 'support sizes in (A, B)', 'alt'),
        ('GROEBNER', 'Groebner / resultant elimination of the round equations', 'P3.9 Macaulay route priced; regularity unproved', 'alt'),
    ])
    cells += _expand(h, 'PO', 'podoor', 'DOOR', ('D1',), [
        ('t30', 'door T30: all rounds bijective, collision is one equation on a 2-dim domain', 'RELABEL re-ask at this round count', 'door'),
        ('t31', 'door T31: meet in the middle at a level boundary (R3-R4, R60)', 'RELABEL re-ask', 'door'),
        ('t32', 'door T32: alternative parametrisations and host curves', 'RELABEL re-ask', 'door'),
        ('t33', 'door T33: symmetries (i-symmetry, mu4 scaling, Frobenius twist of M)', 'RELABEL re-ask', 'door'),
        ('t34', 'door T34: forcing S-box inputs to chosen values by root-finding', 'RELABEL re-ask', 'door'),
        ('t35', 'door T35: S-box difference spectrum of x^5', 'RELABEL re-ask', 'door'),
        ('t36', 'door T36: branch number / minimal active S-boxes in R60-R63', 'RELABEL re-ask', 'door'),
        ('t37', 'door T37: output bits forced across a family (top byte)', 'RELABEL re-ask', 'door'),
        ('t38', 'door T38: balance of the partial block on the real surface', 'RELABEL re-ask', 'door'),
        ('t40', 'door T40: which S-box evaluations are live (constant / dead values)', 'RELABEL re-ask', 'door'),
    ])
    return cells


# --- evidence map: (loc, q) -> [(hash set, files, why)]; anything not listed is UNSCANNED
POMAP = {}
_B = (PO1, PO2)
_R1 = (PO1,)


def _po(loc, qs, hs, files, why):
    for q in qs.split():
        POMAP.setdefault((loc, q), []).append((tuple(hs), files.split(), why))


for _rl in ['R0', 'R1', 'R2', 'R3', 'P1', 'P2', 'R60', 'R61', 'R62', 'R63']:
    for _lane in range(3):
        for _ly in PO_LAYERS:
            _loc = '%s.L%d.%s' % (_rl, _lane, _ly)
            _po(_loc, 'Q1', _B, PO_ATLAS + ' ' + PO_FDEG, 'generic (nk,rho)-degree after this layer from the exact degree tracker (ATLAS section 5, OBSERVED, no cancellation on random lines)')
            _po(_loc, 'Q3', _B, PO_ATLAS + ' ' + PO_FDEG, 'influence set per lane and Jacobian rank 2 at 28 (r=1) / 31 (r=2) recorded points (ATLAS cards, OBSERVED); zero loci of the lane are NOT covered by this answer')
for _rl in ('P1', 'P2'):
    for _lane in (1, 2):
        _po('%s.L%d.SBOX' % (_rl, _lane), 'Q2', _B, PO_ATLAS, 'PROVED: the partial-round S-box acts on lane 0 only; lanes 1 and 2 pass unchanged (R4/R5 card)')
    _po('%s.L0.SBOX' % _rl, 'Q4', _B, PO_ATLAS + ' ' + _l3('P3_11_toylab.md'),
        'difference avoiding the S-box iff d_0 = 0 (X6, PROVED); real-Pallas two-partial hinge: c = h*B*v is nonzero, so a pair equal in lane 0 before P1 and after P1 splits at P2 (P3.11, DERIVED); toy tabulations q = 23/43')
_po('R0.L2.ARC', 'Q2', _B, PO_LEVELS, 'R0 lane 2 is a constant (K = (2^65 + c0,2)^5): one of the only two constant values in the pipeline (LEVELS 4.11, OBSERVED)')
_po('R0.L2.SBOX', 'Q2', _B, PO_LEVELS, 'R0 lane 2 S-box output is a constant: the only constant values in the pipeline are R0.C and R0.S lane 2 (LEVELS 4.11, OBSERVED)')
for _lane in (1, 2):
    _po('R63.L%d.MDS' % _lane, 'Q2', _B, PO_LEVELS, 'rows 1 and 2 of the last M are dead: changing them never changes y (100/100 points; LEVELS 4.11, OBSERVED)')
for _lane in range(3):
    _po('R63.L%d.SBOX' % _lane, 'Q4', _B, PO_LEVELS, 'a lane-0 collision needs M00 dT0 + M01 dT1 + M02 dT2 = 0 with dT != 0: at least two of the three S-boxes of R63 are active (LEVELS 4.11, PROVED)')

# LINE
_po('LINE.SKIP', 'Q1', _B, _l3('P3_1.md') + ' ' + PO_L3A, 'P3.1 COMPUTED: reduced loop agrees across two implementations for r = 0, 1, 2, 56; the round-1 S-box output is affine in tau^5 on the pinned Orchard constants')
_po('LINE.SKIP', 'Q2', _B, PO_ATLAS + ' ' + _l3('P3_2_skip.md'), 'without the line the (nk,rho) degree of the digest is 5^9 / 5^10 (ATLAS section 5, exact tracker); on the line 5^(6+r) (P3.2): the skip removes two factors of 5')
_po('LINE.LINEJ', 'Q1', _B, _l3('P3_1.md'), 'P3.1: the affine-in-tau^5 identity holds numerically for every j choice')
_po('LINE.LINEJ', 'Q4', _B, _l3('P3_2_skip.md'), 'P3.2 (BOUNDED): the three canonical lines exhaust the rational curves preserving the round-1 affine trail')
_po('LINE.BYPASS', 'Q1 Q4', _B, _l3('P3_2_skip.md'), 'P3.2 (BOUNDED): all three canonical lines fail to bypass round 2; 5^(6+r) stays the best established degree; trails outside that condition open')
_po('LINE.CENTRE', 'Q1 Q3', _R1, PO_D189 + ' ' + PO_D189R, 'D189 COMPUTED: 20 deterministic uniform centres, h(s) = s g(s^2), monic deg g = 39,062; 8 of 20 had a nonzero-square root (fraction 0.4, Wilson interval broad)')
_po('LINE.CENTRE', 'Q4', _R1, _l3('P3_15.md') + ' ' + _l3('P3_5_prob.md'), 'fixed-value (input-sampled) fibre method on real r = 1: fibre sizes 3, 2, 1, 5 in four fresh centres (P3.15, SAMPLED); bound 0.632 under uniform coefficients (P3.5)')
_po('LINE.CENTRE', 'Q4', (PO2,), _l3('P3_7_variants.md'), 'fixed-value method priced for r = 2 (scores 35.2-37.1), not run on the real r = 2 target (P3.7, projection)')
_po('LINE.BACKMAP', 'Q1', _R1, PO_LLED + ' ' + PO_D189R, 'sqrt + map back 15,970 operations (ledger); every D189 witness mapped back and rehashed with the reference hash (8 verified)')
_po('LINE.LANE0', 'Q1', _B, _l3('P3_12_outsider.md'), 'P3.12 COMPUTED: on real constants no affine-line trade in the round-1 plane keeps the first partial input lane 0 fixed')
_po('LINE.LANE0', 'Q3', _B, PO_LEVELS, 'LEVELS 4.6: the R3-R4 interface pair set (equal lane 0 after R3) is a curve; counted RT in the coverage matrix')

# POLY
_po('POLY.DEG', 'Q1', _B, PO_ATLAS + ' ' + _l3('P3_3_memory.md'), 'degree 5^(6+r): 78,125 (r=1) / 390,625 (r=2); D189 builds the reduced r=1 target and matches 5 direct evaluations')
_po('POLY.DEG', 'Q4', _B, _l3('P3_2_skip.md'), 'P3.2 (BOUNDED): no canonical line lowers the degree below 5^(6+r)')
_po('POLY.ODD', 'Q1', _B, PO_D189 + ' ' + _l3('P3_4_ops.md'), 'odd part monic of degree 39,062 (r=1, D189) / n = 195,312 (r=2, P3.4)')
_po('POLY.MONIC', 'Q1', _R1, PO_D189, 'D189: monic deg g = 39,062')
_po('POLY.SQFREE', 'Q1', _R1, PO_D189 + ' ' + PO_D189R, 'D189 SAMPLED: all 20 odd parts squarefree (gcd(g, g\') tested); r=0 pilot 12 of 12 (P3.8)')
_po('POLY.COEF', 'Q1', _B, _l3('P3_3_memory.md'), 'one dense odd-part coefficient vector is exactly 1,250,016 B (r=1) / 6,250,016 B (r=2)')
_po('POLY.COEF', 'Q1', _R1, PO_LNOTE, 'filed line: 98,304 line evaluations and one inverse NTT of size 49,152')
_po('POLY.SHIFT', 'Q1', _B, _l3('P3_7_variants.md') + ' ' + PO_L3A, 'truncated streamed Taylor shift: 8,089,888 B (r=1) / 56,374,432 B (r=2) (P3.7, priced)')
_po('POLY.EVALN', 'Q1', _R1, PO_LNOTE, 'filed: 98,304 line evaluations charged as target-compression units')

# ROOT
_po('ROOT.POWER', 'Q1', _R1, PO_LLED, 'instrumented run: S^((p-1)/2) mod g 3,536,768,307 arith + 2,704,810,640 other per centre (final_ledger)')
_po('ROOT.POWER', 'Q1', (PO2,), _l3('P3_4_ops.md'), 'explicit schedule: 22,731,687,198 modular-square operations at n = 195,312 for 253 squares, before shifts, setup, gcd, splitting (P3.4, formula)')
_po('ROOT.POWER', 'Q4', _B, _l3('P3_7_variants.md') + ' ' + _l3('P3_10_bignt.md'), 'no-cache blocked powering 56.48B / 58.51B operations (P3.7), blocked B=2^31 NTT priced for r=8..12 (P3.10)')
_po('ROOT.NTT', 'Q1', _R1, PO_LLED, 'in-place NTT with no stored spectra inside the power loop: 238 loop steps, 26,055,226 operations per step (final_ledger)')
_po('ROOT.NTT', 'Q1', (PO2,), _l3('P3_4_ops.md'), 'cached-reciprocal NTT schedule counted at n = 195,312 (P3.4)')
_po('ROOT.HGCD', 'Q1', _R1, PO_LLED, 'half-gcd 355,770,535 arith + 434,514,494 other per centre (final_ledger)')
_po('ROOT.HGCD', 'Q1', (PO2,), _l3('P3_7_variants.md'), 'padded recursive half-gcd recurrence 9.655B GCD operations (r=2, A/B variants), uninstrumented (P3.7)')
_po('ROOT.HGCD', 'Q4', _B, _l3('P3_7_variants.md'), 'in-place Euclid with finite bound 3N^2 + 338N + 664 and two-vector memory; scores 32.969 (r=1) / 36.560 (r=2) (P3.7)')
_po('ROOT.SPLIT', 'Q1', _R1, PO_D189 + ' ' + PO_D189R, 'D189: gcds of degree 1 and 2 occurred (centre 1 had two nonzero-square roots); every nonzero-square root mapped back and rehashed (8 witnesses)')
_po('ROOT.NEWTON', 'Q1', _R1, PO_LLED, 'newton total 40,263,761 (21,679,385 arith) per centre (final_ledger)')

# LEDGER
for _k, _t in (('INIT', 'init 17,359 arith + 20,480 other = 37,839'), ('SETUP', 'line_setup 391 arith + 1,564 other'),
               ('BUILDG', 'build g 1,436,260 arith + 24,567,311 other'), ('POWER', 'S^((p-1)/2) mod g as in ROOT.POWER'),
               ('GCD', 'half-gcd 355,770,535 arith + 434,514,494 other'), ('ROOTS', 'root finding 7 + sqrt/map back 15,970'),
               ('VERIFY', 'verification (2 reference hashes) 474 arith + 1,896 other'),
               ('TOTAL', 'total 14,115,800,161 = 59,560,338.2 units, log2 25.8278; note time_log2 25.837')):
    _po('LEDGER.' + _k, 'R1', _R1, PO_LLED + ' ' + PO_LNOTE, 'value charged: ' + _t + ' (final_ledger, instrumented run)')
_po('LEDGER.CENTRES', 'R1 R4', _R1, PO_LNOTE, 'at most two centres charged: time_log2 25.837 worst case, 24.838 with one centre (note)')

# MEM
_po('MEM.GBUF', 'M1', _B, _l3('P3_3_memory.md'), 'exactly 1,250,016 B (r=1) / 6,250,016 B (r=2) for one dense coefficient vector')
_po('MEM.PEAK', 'M1', _R1, PO_LNOTE + ' ' + PO_LLED, 'heap peak 8,468,640 B; total 8,636,079 B = 2^23.042 (note, ledger)')
_po('MEM.PEAK', 'M1', (PO2,), _l3('P3_7_variants.md'), 'full-attack peak of the existing composition schedule 157,832,000 B at r=2 (P3.7, projection)')
_po('MEM.RULE', 'M1', _R1, PO_LNOTE, 'memory term 23.042 - 20 = 3.042 bits of the 28.879 normalised cost')
_po('MEM.TWID', 'M1', _R1, PO_LLED, 'init builds the twiddle table of 16,384 entries (final_ledger INIT)')
_po('MEM.SHRINK', 'M2 M4', _B, _l3('P3_9_lowmem.md') + ' ' + _l3('P3_13_lowmem_routes.md'), 'constant-memory scan priced at about 253.65 / 253.68 (P3.9); sequential tableless in-place NTT + two-vector Euclid peak 7,944,800 / 35,527,776 B (P3.13)')

# PREM
_po('PREM.HPOIS', 'R1', _B, _l3('P3_5_prob.md'), 'six-term Bonferroni lower bound 0.63194444 for the fixed-value method under uniform random coefficients (P3.5)')
_po('PREM.HPOIS', 'R1 R4', _R1, PO_LNOTE, 'note: claimed success 0.60, 0.632 under the Poisson root-count heuristic H1 (the one score-critical heuristic)')
_po('PREM.HPOIS', 'R2', _R1, _l3('P3_15.md'), 'fresh r=1 fibre-size trials 3 of 4 successes (sizes 3, 2, 1, 5), exact one-sided 95% lower bound 0.2486 (P3.15, SAMPLED, small n)')
_po('PREM.HPOIS', 'R3', _B, _l3('P3_5_prob.md'), 'toy p = 257 two-centre success 0.606-0.643 (control on a random-coefficient polynomial)')
_po('PREM.HSQ', 'R1', _B, _l3('P3_5_prob.md'), 'lower bound 0.39346788 for odd-part square roots under uniform coefficients (P3.5)')
_po('PREM.HSQ', 'R2', _R1, PO_D189, 'D189: 8 of 20 real centres had a nonzero-square root (0.4 vs 0.3935; Wilson interval broad)')
_po('PREM.HSQ', 'R3', _B, _l3('P3_5_prob.md'), 'toy p = 257 one-centre success 0.367-0.404 (control)')
_po('PREM.HSQFREE', 'R1 R2', _R1, PO_D189, 'D189: all 20 odd parts squarefree')
_po('PREM.HUNIF', 'R1 R3', _B, _l3('P3_5_prob.md'), 'uniform-coefficient model and its toy control (P3.5)')
_po('PREM.HCENT', 'R1', _R1, PO_LNOTE, 'worst-case budget of at most two independent centres (note)')

# JUDGE
_po('JUDGE.JRUNNER', 'R1', _R1, PO_LNOTE, 'note: the experiment runner sizes the digest with digest(b""), which the Orchard digest rejects; no Python experiment declared')
_po('JUDGE.JHEUR', 'R1', _R1, PO_LNOTE, 'note declares H1 as the one score-critical heuristic')

# MACHINE
_po('MACHINE.FMUL', 'Q1', _R1, PO_LLED, 'TYPES line of the instrumented run: mul 2,470,953,120, sqr 66,646,268')
_po('MACHINE.FADD', 'Q1', _R1, PO_LLED, 'TYPES line: add 2,715,539,688, sub 2,534,837,889')
_po('MACHINE.LDST', 'Q1', _R1, PO_LLED, 'TYPES line: ld 2,997,163,555, st 1,663,304,782 (all charged at full price inside the 14.1e9 total)')
_po('MACHINE.CTL', 'Q1', _R1, PO_LLED, 'TYPES line: ctl 1,620,758,761')

# ALT
_po('ALT.BACKSKIP', 'Q1', _B, _l3('P3_12_outsider.md'), 'P3.12: backward output lines are affine after inverse x^5; exhausted on q = 23/43; on real constants no affine-line trade; two-sided intersections capture only a small fraction of toy collisions')
_po('ALT.ZEROSUM', 'Q1', _R1, _l3('P3_14.md'), 'P3.14: real r=1 centred lane-0 sum over 2^21 inputs is zero but all digests distinct; toy q = 23/43 fixed relation keeps about 1/q of collision pairs')
_po('ALT.GROEBNER', 'Q1', _B, _l3('P3_9_lowmem.md'), 'P3.9: conditional regular-sequence Macaulay route scores 960 / 1,039 with enormous memory; regularity and nontrivial-root success unproved (priced, not run)')
_po('ALT.INTERP', 'Q1', _B, PO_ATLAS + ' ' + PO_FDEG, 'exact bivariate monomial counts in (A, B) and the degree table (ATLAS section 5; 4,887,501 A,B-monomials at R60 for r=1)')

# DOOR (D1): only the doors LEVELS section 3.2 marks as done with a result
_po('DOOR.t30', 'D1', _B, PO_LEVELS, 'T30: all rounds bijective, collision = one equation on a 2-dim domain (PROVED X1; toy exhaustive q <= 257)')
_po('DOOR.t35', 'D1', _B, PO_LEVELS, 'T35: S-box difference spectrum of x^5 (closed form, uniformity 4; 365 toy primes, 0 misses)')
_po('DOOR.t37', 'D1', _B, PO_LEVELS, 'T37: output top two bits 00, byte 0x40 unreachable (U4 s1.5)')
_po('DOOR.t40', 'D1', _B, PO_LEVELS, 'T40: only 2 constant values (R0.C/R0.S lane 2) and 2 dead values (R63.M lanes 1, 2) in the pipeline (U4 s1.7-8, U3 s8)')


def eval_po(c):
    h = c['hash']
    hits = [(f, w) for (hs, f, w) in POMAP.get((c['loc'], c['q']), []) if h in hs]
    if not hits:
        return unscanned('no existing evidence answers this question for this %s object' % h)
    files, why = [], []
    for f, w in hits:
        files += [x for x in f if x not in files]
        why.append(w)
    miss = [f for f in files if not exists(f)]
    if miss:
        return unscanned('mapped evidence file(s) missing: ' + ' '.join(miss))
    return scanned_file(files, ' | '.join(why))


def po_weight(c):
    if c['kind'] == 'posrnd':
        return {'Q1': 3.0, 'Q2': 4.0, 'Q3': 4.0, 'Q4': 5.0}[c['q']]
    if c['kind'] == 'podoor':
        return 20.0
    if c['kind'] in ('poledger', 'pojudge', 'poprem', 'pomem'):
        return 6.0
    return 10.0


def build_po_cells():
    out = []
    for h in PO_HASHES:
        for c in build_poseidon_universe(h):
            c.update(eval_po(c))
            if c['state'] != 'SCANNED' and c['id'] in NAMED:
                c.update(scanned_cells(NAMED[c['id']], 'own-test record(s) naming this universe cell'))
            out.append(c)
    return out


PO_METHOD = ('ORCHARD POSEIDON (%s: P128Pow5T3 over Pallas, t = 3, x^5, full rounds 0-3, %s, full rounds 60-63, digest lane 0, ordinary collision; score = time_log2 + max(0, log2(bytes) - 20)). '
             'Round cells (loc R<n>.L<lane>.<ARC|SBOX|MDS>, partial rounds P1[,P2], lane 0 only is S-boxed there): Q1 exact value or degree as used; Q2 necessity (change or drop it, recount the exact outcome); '
             'Q3 degrees of freedom (influence, rank, zero locus) or score-optimal value; Q4 alternatives (other patterns / differences / backward walk). Family cells: Q1..Q4 the same; R1..R4 premise/ledger/judge (value charged, own recount, control, score sensitivity); '
             'M1..M4 memory (bytes held, necessity, time cost of shrinking, alternatives); D1 the RELABEL re-ask of the door at this round count. '
             'Rules: our own code only (never run or import other participants\' code); validate tools on known answers first (poseidon_ref.py vs the pinned vectors, toy fields); at most ONE heavy process, nice 10 / BelowNormal, each run under 5 minutes; stop only your own PIDs; '
             'never read workspace\\.key, never run yukon submit or yukon run. One honest test or exact count per cell; a timeout or unfinished search is OPEN, never KILLED; KILLED needs our own test and a number. '
             'Labels BEDROCK / COMPUTED / SAMPLED / LOCAL_ONLY / OPEN. Write each result with research/dig/add_cell.py and FILL held_fixed AND reopen_if ON EVERY RECORD; '
             'put "universe cell <hash>|<loc>|<object>|<Q>" for each answered cell into notes so the coverage run marks it scanned.')
PO_HINT = ('research/poseidon/levels/ (ATLAS_POSEIDON.md, LEVELS.md, atlas/facts_*.py outputs), research/poseidon/orchard/lean_r1/ (filed entry 651c0ca6: logs/final_ledger.txt, submission-note.md, pkg_stage/proof.md), '
           'research/sol_answer_D189_poseidon_learning.md, research/poseidon/d189_gpu_results.jsonl, 3rd_openai_workspace/luna3/ (ANSWER.md, P3_*.md); for ALT also research/poseidon/levels/decomp, freelunch, cheaplunch (outside the scan evidence: read, then decide). Do not redo what is cited as answered in the cell reason.')


def build_po_units(universe):
    units = []
    for h in PO_HASHES:
        cs = [c for c in universe if c['hash'] == h and c['state'] == 'UNSCANNED']
        r = 1 if h == PO1 else 2
        meth = PO_METHOD % (h, 'one partial round (S-box on lane 0 only)' if r == 1 else 'two partial rounds (S-box on lane 0 only)')
        state = {'cur': [], 'w': 0.0}
        n0 = len(units)

        def flush():
            cur = state['cur']
            if not cur:
                return
            uid = '%s-U%02d' % (h, len(units) - n0 + 1)
            for c in cur:
                c['unit'] = uid
            lines = collections.OrderedDict()
            for c in cur:
                lines.setdefault(c['loc'], []).append(c['q'])
            txt = meth + ' Cells: ' + ' '.join('%s [%s]' % (k, ' '.join(v)) for k, v in lines.items()) + ' Existing material (read first): ' + PO_HINT
            units.append(dict(id=uid, hash=h, group='PO', scope='%s: %s' % (cur[0]['cl'], ', '.join(list(lines)[:6]) + (' ...' if len(lines) > 6 else '')),
                              cells=[c['id'] for c in cur], est_minutes=max(10, min(60, int(round(sum(po_weight(c) for c in cur)) + 8))), questions=txt))
            state['cur'], state['w'] = [], 0.0

        atoms = collections.OrderedDict()
        for c in cs:
            atoms.setdefault(c['loc'], []).append(c)
        for loc, a in atoms.items():
            aw = sum(po_weight(c) for c in a)
            if state['cur'] and (state['w'] + aw > 48.0 or state['cur'][0]['cl'] != a[0]['cl']):
                flush()
            state['cur'] = state['cur'] + a
            state['w'] += aw
        flush()
    return units


_evaluate_all_w2 = evaluate_all


def evaluate_all():
    return _evaluate_all_w2() + build_po_cells()


_build_units_w2 = build_units


def build_units(universe):
    return _build_units_w2(universe) + build_po_units(universe)


_write_md_w2 = write_md


def write_md(universe, units):
    _write_md_w2(universe, units)
    L = ['\n## poseidon-r1 / poseidon-r2 (Orchard Poseidon; group PO, added 2026-10-12)\n',
         'The Poseidon line walked square by square: per round (R0-R3, P1[, P2], R60-R63) x lane (0-2) x layer (ARC, SBOX, MDS) x Q1..Q4, plus the families LINE POLY ROOT LEDGER MEM PREM JUDGE MACHINE ALT DOOR. '
         'Scanned only from existing evidence: the atlas and LEVELS, the filed r=1 entry 651c0ca6 (lean_r1 ledger and note), D189 and its GPU results, and the Luna 3 answers (P3_*.md). No CELLS.jsonl record exists for either hash yet; '
         'the ALT walls FUNCDEC FREELUNCH CHEAPLUNCH GKR stay UNSCANNED even though levels/decomp, freelunch, cheaplunch exist (outside the scan evidence). Wave-1 universe and all other targets are unchanged.\n']
    for h in PO_HASHES:
        po = [c for c in universe if c['hash'] == h]
        fams = collections.OrderedDict()
        for c in po:
            k = ('ROUND:' + c['loc'].split('.')[-1]) if c['kind'] == 'posrnd' else c['object']
            fams.setdefault(k, []).append(c)
        rows = [[k, len(cs), sum(c['state'] == 'SCANNED' for c in cs), sum(c['state'] == 'UNSCANNED' for c in cs)] for k, cs in fams.items()]
        rows.append(['**all**', len(po), sum(c['state'] == 'SCANNED' for c in po), sum(c['state'] == 'UNSCANNED' for c in po)])
        L.append('\n### %s\n' % h)
        L.extend(md_table(rows, ['family', 'cells', 'scanned', 'unscanned']))
    with open(os.path.join(HERE, 'COVERAGE.md'), 'a', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(L) + '\n')


_main_w2 = main


def main():
    _main_w2()
    T = collections.Counter()
    for l in open(os.path.join(HERE, 'UNIVERSE.jsonl'), encoding='utf-8'):
        d = json.loads(l)
        if d['hash'] in PO_HASHES:
            T[(d['hash'], d['state'].lower())] += 1
    print('poseidon', dict(T))



if __name__ == '__main__':
    main()
