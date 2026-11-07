"""Check downloaded SHA-256 row data against its published metadata.

Usage: python check_row_projections.py sha256-row-projections.jsonl.gz trajectory-atlas.json
Standard library only. This checks transcription format/identity, not SAT or collisions.
"""
import gzip
import hashlib
import json
import re
import sys
from pathlib import Path

if not __debug__:
    raise SystemExit('Run without -O: assertions are required')
if len(sys.argv)!=3:
    raise SystemExit(__doc__)
blob=Path(sys.argv[1]).read_bytes();meta=json.loads(Path(sys.argv[2]).read_text())
assert len(blob)==meta['gzip_bytes'] and hashlib.sha256(blob).hexdigest()==meta['gzip_sha256']
raw=gzip.decompress(blob)
assert len(raw)==meta['uncompressed_bytes'] and hashlib.sha256(raw).hexdigest()==meta['uncompressed_sha256']
seen=set();sources=set();steps={}
for line in raw.splitlines():
    r=json.loads(line)
    assert r['target']=='sha2' and r['declared_word_bits']==32 and 1<=r['declared_steps']<=64
    assert r['status']=='data-only-not-an-encoding-or-verdict'
    canonical={k:r[k] for k in ('target','declared_steps','declared_word_bits','rows')}
    digest=hashlib.sha256(json.dumps(canonical,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    assert r['id']==digest and digest not in seen;seen.add(digest)
    indices=[]
    for row in r['rows']:
        assert set(row)<=set(('row','A','E','W')) and len(row)>1
        assert -4<=row['row']<r['declared_steps'];indices.append(row['row'])
        for name,value in row.items():
            if name!='row': assert re.fullmatch('[01?xunXUN-]{32}',value)
    assert indices==sorted(set(indices))
    for s in r['sources']:
        assert s['path'].startswith('research/') and '..' not in s['path'].split('/')
        assert re.fullmatch('[a-f0-9]{64}',s['sha256']) and s['path'] not in sources
        sources.add(s['path'])
    key=str(r['declared_steps']);steps[key]=steps.get(key,0)+1
assert len(seen)==meta['count'] and len(sources)==meta['source_files']
assert steps==meta['declared_step_counts']
print(json.dumps({'passed':True,'distinct_projections':len(seen),'source_identities':len(sources),
    'scope':'Downloaded-byte integrity, canonical identity and row schema only. Original XML files are not bundled or independently rechecked here. No solver or collision assertion.'},indent=2))
