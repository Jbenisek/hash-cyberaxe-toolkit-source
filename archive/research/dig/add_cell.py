#!/usr/bin/env python3
"""Append one validated record to CELLS.jsonl. Refuses KILLED without own_test.
Usage: add_cell.py --json '{...}' | --file rec.json
Library: load(), validate(rec, existing), append(rec)"""
import json, os, re, sys, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
STORE = os.path.join(HERE, 'CELLS.jsonl')
HASHES = {'sha256-37', 'sha256-38', 'sha256-39', 'sha256-64', 'sha3-r5', 'sha3-r6', 'sha3-r7', 'blake3-r2', 'blake3-r3', 'blake3-r4', 'poseidon-r1', 'poseidon-r2', 'poseidon-r3', 'poseidon-r4', 'poseidon-r5', 'poseidon-r6'}
STATUS = {'BEDROCK', 'COMPUTED', 'SAMPLED', 'LOCAL_ONLY', 'CLAIMED-UNTESTED', 'KILLED', 'OPEN'}
LABELS = set('NDXCSIBPKEZ0')
OUTSIDE = ('luna cloud', 'grok', 'gpt', 'astra', 'sol cloud')
REQ = ['hash', 'row_i', 'row_j', 'object', 'question', 'labels', 'status', 'number', 'source',
       'own_test', 'evidence', 'date', 'lever', 'gain_bits', 'notes']
OPT = ['id', 'topic', 'gain_basis', 'potential_bits', 'prior', 'confirmed_by', 'held_fixed', 'reopen_if', 'supersedes', 'kind', 'peak_mem']


def load(path=STORE):
    out = []
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            for ln in f:
                ln = ln.strip()
                if ln:
                    out.append(json.loads(ln))
    return out


def supersession_map(recs):
    """{old id: id of the (first) record that supersedes it}. Append-only store: closure is a later record's `supersedes` list."""
    m = {}
    for r in recs:
        for o in r.get('supersedes') or []:
            by = r.get('id') or ''
            if r.get('kind') == 'supersession' and by.endswith('-SUP'):
                by = by[:-4]   # bookkeeping record <id>-SUP: show the substantive record <id>
            m.setdefault(o, by)
    return m


def is_outside(src):
    s = src.lower()
    return any(s.startswith(p) for p in OUTSIDE)


def hash_ok(h):
    return h in HASHES or bool(re.fullmatch(r'poseidon-r\d+|blake3-r\d+|sha256-r?\d+|sha3-r\d+', h))


def validate(r, existing):
    e = []
    for k in REQ:
        if k not in r:
            e.append('missing field ' + k)
    for k in r:
        if k not in REQ and k not in OPT:
            e.append('unknown field ' + k)
    if e:
        return e
    if not hash_ok(r['hash']):
        e.append('hash must be one of %s' % sorted(HASHES))
    for k in ('row_i', 'row_j'):
        if r[k] is not None and (not isinstance(r[k], int) or isinstance(r[k], bool)):
            e.append(k + ' must be int or null')
    if not isinstance(r['labels'], list) or not all(isinstance(x, str) and x in LABELS for x in r['labels']):
        e.append('labels must be a list drawn from N D X C S I B P K E Z 0')
    if r['status'] not in STATUS:
        e.append('status must be one of %s' % sorted(STATUS))
    for k in ('object', 'question', 'number', 'source', 'evidence', 'notes'):
        if not isinstance(r[k], str):
            e.append(k + ' must be str')
    for k in ('object', 'source', 'evidence'):
        if isinstance(r[k], str) and not r[k].strip():
            e.append(k + ' must not be empty')
    for k in ('own_test', 'lever'):
        if not isinstance(r[k], bool):
            e.append(k + ' must be true/false')
    if not (isinstance(r['date'], str) and re.fullmatch(r'\d{4}-\d\d-\d\d', r['date'])):
        e.append('date must be YYYY-MM-DD')
    g = r['gain_bits']
    if g is not None and (isinstance(g, bool) or not isinstance(g, (int, float))):
        e.append('gain_bits must be number or null')
    for k in ('potential_bits', 'prior'):
        v = r.get(k)
        if v is not None and (isinstance(v, bool) or not isinstance(v, (int, float))):
            e.append(k + ' must be number or null')
    if isinstance(r.get('prior'), (int, float)) and not (0 <= r['prior'] <= 1):
        e.append('prior must be in 0..1')
    ids = {x.get('id') for x in existing}
    if r.get('id') and r['id'] in ids:
        e.append('duplicate id ' + r['id'])
    sup = r.get('supersedes')
    if sup is not None:
        if not isinstance(sup, list) or not sup or not all(isinstance(x, str) for x in sup):
            e.append('supersedes must be a non-empty list of record ids')
        else:
            for x in sup:
                if x not in ids:
                    e.append('supersedes names unknown id ' + x)
                if x == r.get('id'):
                    e.append('a record cannot supersede itself')
    if r.get('kind') not in (None, 'supersession'):
        e.append("kind must be 'supersession' when present")
    if r.get('kind') == 'supersession' and not sup:
        e.append("kind 'supersession' requires supersedes")
    if e:
        return e
    if r['status'] == 'KILLED' and not r['own_test']:
        e.append('REFUSED: KILLED requires own_test=true (outside claims of "closed" enter as CLAIMED-UNTESTED)')
    if is_outside(r['source']) and not r['own_test'] and r['status'] not in ('CLAIMED-UNTESTED', 'OPEN'):
        conf = r.get('confirmed_by') or []
        own = {x.get('id') for x in existing if x.get('own_test')}
        if not conf or not all(c in own for c in conf):
            e.append('REFUSED: outside source with own_test=false must be CLAIMED-UNTESTED/OPEN '
                     'unless confirmed_by names existing own_test=true records')
    return e


def append(r, path=STORE):
    existing = load(path)
    errs = validate(r, existing)
    if errs:
        raise ValueError('; '.join(errs))
    if not r.get('id'):
        nums = [int(x['id'][1:]) for x in existing if re.fullmatch(r'C\d{4,}', x.get('id', ''))]
        r = dict(r, id='C%04d' % (1 + max(nums or [0])))
    with open(path, 'a', encoding='utf-8', newline='\n') as f:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')
    return r['id']


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--json')
    g.add_argument('--file')
    a = ap.parse_args()
    rec = json.loads(a.json) if a.json else json.load(open(a.file, encoding='utf-8'))
    try:
        print('added', append(rec))
    except ValueError as ex:
        print(str(ex), file=sys.stderr)
        sys.exit(2)
