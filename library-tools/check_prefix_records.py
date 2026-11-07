"""Validate the downloaded saved-record projection, NOT the reported solver results.

Usage: python check_prefix_records.py prefix-run-records.json prefix-ledger.json
Python 3.10+, standard library; no network, writes, solvers or project dependencies.
"""
import collections,hashlib,json,math,re,sys
from pathlib import Path,PurePosixPath
if not __debug__: raise SystemExit('Run without -O')
if len(sys.argv)!=3: raise SystemExit(__doc__)
raw=Path(sys.argv[1]).read_bytes();metadata=json.loads(Path(sys.argv[2]).read_text())
assert len(raw)==metadata['bytes'] and hashlib.sha256(raw).hexdigest()==metadata['sha256'],'Download differs from manifest'
data=json.loads(raw);assert data['schema_version']==1
records=data['records'];assert len(records)==data['record_count']==metadata['record_count']
assert len({r['id'] for r in records})==len(records)
for r in records:
    required={'id','source','source_sha256','trail','last_checked_row','reported_status','reported_witness','reported_violations'}
    allowed=required|{'warm_start','recorded_metrics'}
    assert required<=set(r)<=allowed
    assert r['source'].startswith('research/cloud_final_1101/hs/ivdepth/') and '..' not in PurePosixPath(r['source']).parts
    assert re.fullmatch(r'[A-Za-z0-9_./-]+\.json',r['source'])
    assert re.fullmatch(r'[0-9a-f]{64}',r['source_sha256'])
    assert r['id']==hashlib.sha256((r['source']+'\0'+r['source_sha256']).encode()).hexdigest()[:24]
    assert re.fullmatch(r'[A-Za-z0-9_.-]+\.xml',r['trail'])
    assert type(r['last_checked_row']) is int and 0<=r['last_checked_row']<64
    assert r['reported_status'] in ('SAT','UNSAT','HELD','BUILD_ERROR')
    assert type(r['reported_witness']) is bool
    assert r['reported_violations'] is None or (type(r['reported_violations']) is int and r['reported_violations']>=0)
    if r['reported_status']=='BUILD_ERROR':
        assert set(r)==required and not r['reported_witness'] and r['reported_violations'] is None
    else:
        assert set(r)==allowed and type(r['warm_start']) is bool
        assert set(r['recorded_metrics'])=={'build_ms','solve_ms','solver_ms','total_ms','rss_mb'}
        assert all(type(v) in (int,float) and math.isfinite(v) and v>=0 for v in r['recorded_metrics'].values())
counts=dict(collections.Counter(r['reported_status'] for r in records))
assert counts==data['counts']==metadata['counts']
assert sum(r['reported_witness'] for r in records)==data['reported_witness_count']==metadata['reported_witness_count']
assert len({r['source_sha256'] for r in records})==data['distinct_source_byte_hashes']==metadata['distinct_source_byte_hashes']
print(json.dumps({'passed':True,'records':len(records),'reported_counts':counts,
    'scope':'Exported schema, source identities and saved counts only. No original solver proof or collision verification.'},indent=2))
