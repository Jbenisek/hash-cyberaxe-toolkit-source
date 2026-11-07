"""Recount the two downloaded historical tables; not a solver-proof checker."""
import collections, hashlib, json, re, sys
from pathlib import Path
if not __debug__: raise SystemExit('Run without -O')
if len(sys.argv)!=2: raise SystemExit('Usage: python check_search_outcomes.py DIRECTORY')
root=Path(sys.argv[1])
data=json.loads((root/'search-outcomes.json').read_text(encoding='utf-8'))
expected={'waterfall':('WATERFALL.tsv',47,14), 'closure':('CLOSURE.tsv',138,17)}
rows=[]
for group,(name,total,unique) in expected.items():
    source=next(s for s in data['sources'] if s['path'].endswith('/'+name))
    raw=(root/name).read_bytes()
    assert len(raw)==source['bytes'] and hashlib.sha256(raw).hexdigest()==source['sha256']
    grouped=collections.defaultdict(list); parsed=[]
    for line_number,line in enumerate(raw.decode('utf-8-sig').splitlines(),1):
        if not line.strip():continue
        name,rung,slice_number,status,clock=line.split('\t')
        assert re.fullmatch('[A-Za-z0-9_-]+',name)
        assert re.fullmatch(r'rung \d+',rung) and re.fullmatch(r'slice \d+',slice_number)
        assert status in {'SAT','UNSAT','HELD'} and re.fullmatch(r'\d{2}:\d{2}',clock)
        row={'table':group,'source_line':line_number,'instance_label':name,
             'rung':int(rung.split()[1]),'slice':int(slice_number.split()[1]),
             'reported_status':status,'source_clock_label':clock}
        parsed.append(row); grouped[(name,row['rung'])].append(row)
    assert len(parsed)==total and len(grouped)==unique
    assert parsed==[r for r in data['records'] if r['table']==group]
    for (name,rung),history in grouped.items():
        assert [r['slice'] for r in history]==list(range(1,len(history)+1))
        assert all(r['reported_status']=='HELD' for r in history[:-1])
        entry=next(o for o in data['instances'] if o['table']==group and o['instance_label']==name and o['rung']==rung)
        assert entry['recorded_slices']==len(history)
        assert entry['last_reported_status']==history[-1]['reported_status']
    summary=data['summaries'][group]
    assert summary['table_rows']==total and summary['instance_rung_labels']==unique
    assert summary['row_status_counts']==dict(collections.Counter(r['reported_status'] for r in parsed))
    assert summary['last_status_counts']==dict(collections.Counter(h[-1]['reported_status'] for h in grouped.values()))
    assert summary['slice_count_distribution']==dict(sorted(collections.Counter(str(len(h)) for h in grouped.values()).items()))
    rows.extend(parsed)
assert len(data['records'])==len(rows)==185 and len(data['instances'])==31
print(json.dumps({'passed':True,'table_rows':185,'instance_rung_labels':31,
                  'last_reported_statuses':{'UNSAT':9,'HELD':22},
                  'scope':'Exact transcription and grouping of two source tables. No independent solver verdict, model, proof or runtime certification.'},indent=2))
