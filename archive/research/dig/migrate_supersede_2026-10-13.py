#!/usr/bin/env python3
"""2026-10-13 backfill: APPEND one kind=supersession record per superseding record whose notes name the ids it closes.
Store stays append-only; idempotent (skips ids already present). Partial closes (S38-D1013-prefix: cell counts only) are NOT included."""
import add_cell

MAP = {
    'C1964': ['C1868'], 'C1965': ['C1875'], 'C1966': ['C1864'], 'C1969': ['C1952', 'C1954'],
    'C1970': ['C1930', 'C1931', 'C1932', 'C1933', 'C1934', 'C1935', 'C1936', 'C1937'],
    'C1971': ['C1929'], 'C1972': ['C1944'],
    'S38-D1013-plus': ['S38-LC-plus-open'],
    'S38-D1013-gates19_37': ['S38-LC-open-gates19_37', 'S38-FU-stack-transfer'],
    'S38-D1013-front': ['S38-LC-open-front'],
    'S37-D1013-pattern-dist': ['S37-GPT-1819-dist'],
}
recs = add_cell.load()
by = {r['id']: r for r in recs}
for new, olds in MAP.items():
    n = by[new]
    sid = new + '-SUP'
    if sid in by:
        continue
    rec = dict(id=sid, kind='supersession', supersedes=olds, hash=n['hash'], row_i=n['row_i'], row_j=n['row_j'],
               object='supersession: %s closes %s' % (new, ', '.join(olds)), question='bookkeeping: which older rows does %s close' % new,
               labels=[], status='COMPUTED', number='n/a', source='main session', own_test=False, evidence='research/dig/CELLS.jsonl ' + new,
               date='2026-10-13', lever=False, gain_bits=None,
               notes='Backfill of a link stated in free text in the notes of %s ("Closes ..."). Not a cell; build_views excludes it from counts.' % new)
    print('added', add_cell.append(rec))
