import json,re,sys
dirs=sys.argv[1:]
numre=re.compile(r'(?<![\w.])(?:\d[\d,]*\.?\d*(?:e[+-]?\d+)?|\d*\.\d+(?:e[+-]?\d+)?)(?![\w])')
def norm(s): return s.replace(',','')
for d in dirs:
    c=json.load(open('pa_src/%s/claim.json'%d)); p=open('pa_src/%s/proof.md'%d,encoding='utf8',errors='replace').read()
    pn=norm(p)
    txt=json.dumps(c.get('restrictions',[]))+' '+' '.join((h.get('statement','')+' '+h.get('scope','')+' '+h.get('extrapolation','')+' '+h.get('limitations','')) for h in c.get('heuristics',[]))
    miss=[]
    for m in set(numre.findall(txt)):
        n=norm(m).rstrip('.')
        digs=re.sub(r'\D','',n)
        if len(digs)<4: continue
        if n not in pn: miss.append(m)
    print('==',d,'claim',c['claim']); print('  numbers in claim text absent from proof:',sorted(miss)[:60])
