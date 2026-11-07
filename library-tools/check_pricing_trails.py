"""Check saved trail XML and its witness tables, not a solver or attack price.

Usage: python examples/check_pricing_trails.py <library-root>
Python 3.10+ and Node.js; standard libraries, no network, searches or file writes.
"""
import csv
import hashlib
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

REFERENCE='a08df68ee8b4a98949d94896486fc04cabad9e71087f3a0719003088a3fa1b8c'
MASK=2**32-1
PAIR_SYMBOLS='#0u3n5x71-ABCDE?'
PAIR_MASKS={symbol:i for i,symbol in enumerate(PAIR_SYMBOLS)}
MASK_PATTERN=r'(-?\d+)\s+A:\s*([#0u3n5x71ABCDE?\-]+)\s+E:\s*([#0u3n5x71ABCDE?\-]+)(?:\s+W:\s*([#0u3n5x71ABCDE?\-]+))?'
def permitted(symbol,first,second):return bool(PAIR_MASKS[symbol]&(1<<(first+2*second)))
def pinned(root,pin):
    relative=Path(pin['url'])
    if relative.is_absolute() or '..' in relative.parts:raise ValueError('Unsafe relative path')
    path=(root/relative).resolve()
    if not path.is_relative_to(root):raise ValueError('Path outside library')
    raw=path.read_bytes();assert len(raw)==pin['bytes'] and hashlib.sha256(raw).hexdigest()==pin['sha256']
    return raw

def parse_trail(raw):
    assert b'<!DOCTYPE' not in raw.upper() and b'<!ENTITY' not in raw.upper()
    config=ET.fromstring(raw);assert config.tag=='config'
    options={o.get('name'):o.get('value') for o in config.findall('./options/option')}
    assert options['f']=='sha2' and options['w']=='32'
    rounds=int(options['n']);assert 1<=rounds<=64
    value=config.find('char').get('value')
    matches=list(re.finditer(MASK_PATTERN,value))
    assert not re.sub(r'\s+','',re.sub(MASK_PATTERN,'',value))
    rows=[];owners=Counter();expanded=Counter()
    for m in matches:
        step=int(m[1]);masks={'A':m[2],'E':m[3]}
        if m[4]:masks['W']=m[4]
        assert ('W' in masks)==(step>=0)
        for register,mask in masks.items():
            assert len(mask)==32
            (expanded if register=='W' and step>=16 else owners).update(mask)
        rows.append({'step':step,'masks':masks})
    assert [r['step'] for r in rows]==list(range(-4,rounds))
    return {'rounds':rounds,'rows':rows,'owner_positions':sum(owners[x] for x in 'un01'),
            'owner_sign_positions':owners['u']+owners['n'],'owner_fixed_value_positions':owners['0']+owners['1'],
            'expanded_W_positions':sum(expanded[x] for x in 'un01'),'owner_symbols':dict(owners),
            'owner_generalized_positions':sum(v for k,v in owners.items() if k not in '-un01?')}

def words(text,n):
    tokens=text.split();assert len(tokens)==n and all(re.fullmatch(r'[0-9a-fA-F]{8}',t) for t in tokens)
    return [int(t,16) for t in tokens]
def rr(x,n):return ((x>>n)|(x<<(32-n)))&MASK
def schedule(message,n):
    w=list(message)
    for i in range(16,n):
        a,b=w[i-15],w[i-2];s0=rr(a,7)^rr(a,18)^(a>>3);s1=rr(b,17)^rr(b,19)^(b>>10)
        w.append((w[i-16]+s0+w[i-7]+s1)&MASK)
    return w
def violations(trail,pair,states):
    schedules=[schedule(pair['a'],trail['rounds']),schedule(pair['b'],trail['rounds'])];bad=[]
    for row in trail['rows']:
        t=row['step']
        for reg,mask in row['masks'].items():
            values=[]
            for side in (0,1):
                if reg=='W':value=schedules[side][t]
                elif t<0:value=pair['cv'][-1-t+(4 if reg=='E' else 0)]
                else:value=states[side]['trace'][t][0 if reg=='A' else 4]
                values.append(value)
            for column,symbol in enumerate(mask):
                bits=tuple((v>>(31-column))&1 for v in values)
                accepted=permitted(symbol,*bits)
                if not accepted:bad.append([t,reg,31-column,symbol,list(bits)])
    return bad

def check(root):
    root=Path(root).resolve();manifest=json.loads((root/'data/cellbook/pricing-trails.json').read_bytes())
    reference=root/'sha256-replay.js';assert hashlib.sha256(reference.read_bytes()).hexdigest()==REFERENCE
    decoder=manifest['decoder_reference'];code=pinned(root,decoder['source']).decode('utf-8')
    pinned(root,decoder['header']);pinned(root,decoder['license_file'])
    assert re.search(r'static const char chars\[\]\s*=\s*"([^"]+)"',code)[1]==PAIR_SYMBOLS
    numbers=re.search(r'NUMPAIRS\[16\]\s*=\s*\{([^}]+)\}',code)[1]
    assert [int(v) for v in re.findall(r'\d+',numbers)]==[i.bit_count() for i in range(16)]
    table=re.search(r'PAIRS\[16\]\[4\]\s*=\s*\{(.*?)\};',code,re.S)[1]
    pairsets=[[int(v,16) for v in re.findall(r'0x([0-9a-fA-F]+)',line)] for line in re.findall(r'\{([^{}]*)\}',table)]
    assert pairsets==[[pair for pair in range(4) if (mask>>pair)&1] for mask in range(16)]
    records=[];trails={};totals=Counter()
    lean=parse_trail(pinned(root,manifest['lean']['artifact'])) if 'lean' in manifest else None
    candidates=[]
    for item in manifest.get('candidates_40',[]):
        raw=pinned(root,item['artifact']);assert b'<!DOCTYPE' not in raw.upper() and b'<!ENTITY' not in raw.upper()
        parsed=parse_trail(raw)
        config=ET.fromstring(raw);options={o.get('name'):o.get('value') for o in config.findall('./options/option')}
        assert (options['f'],options['n'],options['w'])==('sha2','40','32')
        rows=re.findall(r'(-?\d+)\s+A:\s*(\S+)\s+E:\s*(\S+)(?:\s+W:\s*(\S+))?',config.find('char').get('value'))
        assert [int(r[0]) for r in rows]==list(range(-4,40))
        assert all(len(mask)==32 for _,a,e,w in rows for mask in (a,e,w) if mask)
        symbols=Counter(''.join(a+e+w for _,a,e,w in rows))
        candidates.append({'url':item['artifact']['url'],'rounds':40,'structural_check_passed':True,'symbol_decoder_checked':True,'observed_symbols':dict(symbols),
                           'extended_symbols':sorted(set(symbols)-set('-un01')),'recorded_status':item['recorded_status'],
                           'source_cap_seconds':item['source_cap_seconds'],'witness_replay_performed':False,
                           'owner_singleton_positions':parsed['owner_positions'],'owner_generalized_positions':parsed['owner_generalized_positions'],
                           'semantic_condition_price':'OPEN: a realizing witness and an operation/probability cost derivation are not supplied by the XML shape or symbol count.'})
    for item in manifest['trails']:
        full=parse_trail(pinned(root,item['full']));signed=parse_trail(pinned(root,item['signed']))
        assert set(full['owner_symbols'])<=set('-un01') and set(signed['owner_symbols'])<=set('-un01')
        assert full['rounds']==signed['rounds']==item['rounds']
        assert signed['owner_fixed_value_positions']==0
        for a,b in zip(full['rows'],signed['rows']):
            assert a['step']==b['step']
            for reg,mask in a['masks'].items():assert ''.join('-' if c in '01' else c for c in mask)==b['masks'][reg]
        pairs=list(csv.DictReader(pinned(root,item['witnesses']).decode('utf-8-sig').splitlines(),delimiter='\t'))
        for row in pairs:
            pair={'tag':item['tag'],'key':row['key'],'cv':words(row['cv'],8),'a':words(row['M1'],16),'b':words(row['M2'],16),'rounds':item['rounds']}
            assert pair['a']!=pair['b'];records.append(pair)
        trails[item['tag']]={'full':full,'signed':signed,'records':len(pairs)}
    js=r"""
const fs=require('node:fs'),H=require(process.argv[1]),rows=JSON.parse(fs.readFileSync(0,'utf8'));
process.stdout.write(JSON.stringify(rows.map(r=>[H.compress(r.a,r.cv,r.rounds),H.compress(r.b,r.cv,r.rounds)])));
"""
    run=subprocess.run(['node','-e',js,str(reference)],input=json.dumps(records),capture_output=True,text=True,timeout=60,check=True)
    states=json.loads(run.stdout);assert len(states)==len(records)
    failures=[];per_tag=Counter();lean_failures=0;lean_rows=0
    for pair,state in zip(records,states):
        bad_signed=violations(trails[pair['tag']]['signed'],pair,state);bad_full=violations(trails[pair['tag']]['full'],pair,state)
        equal=state[0]['output']==state[1]['output']
        if lean is not None and pair['tag']==manifest['lean']['compare_to']:
            lean_rows+=1;lean_failures+=bool(violations(lean,pair,state))
        totals['witness_rows_checked']+=1
        if bad_signed or bad_full or not equal:
            per_tag[pair['tag']]+=1;failures.append({'tag':pair['tag'],'key':pair['key'],'output_equal':equal,'signed_violations':len(bad_signed),'full_violations':len(bad_full),'first_violation':(bad_full or bad_signed or [None])[0]})
    summaries=[]
    for tag,data in trails.items():
        f,s=data['full'],data['signed'];summaries.append({'tag':tag,'rounds':f['rounds'],'witness_rows':data['records'],
            'owner_positions_full':f['owner_positions'],'owner_positions_signed':s['owner_positions'],
            'owner_value_pins':f['owner_fixed_value_positions'],'expanded_W_positions_full':f['expanded_W_positions'],
            'witness_mismatches':per_tag[tag]})
    return {'schema':'hashsmash-pricing-trail-check-v1','passed':not failures and not lean_failures,'trails':summaries,**dict(totals),'failures':failures,
            'pair_symbol_decoder':{s:[[a,b] for b in (0,1) for a in (0,1) if permitted(s,a,b)] for s in PAIR_SYMBOLS},
            'lean':{'owner_positions':lean['owner_positions'],'owner_value_pins':lean['owner_fixed_value_positions'],'witness_rows_checked':lean_rows,'witness_mismatches':lean_failures} if lean else None,
            'candidates_40':candidates,
            'scope':'Pinned XML shape, FULL/SIGNED relation, literal owner-position counts and exact saved witness masks/output only. Counts are not assumed independent probability conditions or an attack price.'}

if __name__=='__main__':
    if len(sys.argv)!=2:raise SystemExit(__doc__)
    result=check(sys.argv[1]);print(json.dumps(result,indent=2));raise SystemExit(0 if result['passed'] else 1)
