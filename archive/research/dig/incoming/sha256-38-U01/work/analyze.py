import re,glob,os,json,math
meta=json.load(open('meta.json'))
def parse(f):
    s=open(f,encoding='utf-8',errors='replace').read()
    pre=[float(x) for x in re.findall(r'prefix log2 P\(rows 6\.\.21\) = (-?[\d.]+|-inf)',s)]
    cells=[int(x) for x in re.findall(r'cells\s+rows 22\.\.37:\s+(\d+)',s)]
    ex=[int(x) for x in re.findall(r'EXACT\s+zero output difference after the last step:\s+(\d+)',s)]
    ce=[int(x) for x in re.findall(r'with exact (\d+)',s)]
    samp=[int(x) for x in re.findall(r'samples (\d+) \(late',s)]
    ok=re.search(r'^exit 0',s,re.M) is not None
    return dict(pre=pre,cells=cells,ex=ex,cellex=ce[:len(cells)],samp=samp,ok=ok,stage=re.findall(r'stage (\d+) \(E-driven[^)]*\): forced\s+(\d+) bits, accepted (\d+) of',s)[:12])
base=parse('out/_regression_base.txt')
B_pre=sum(base['pre'])/len(base['pre']); B_ex=sum(base['ex'])
res={}
for name,m in meta.items():
    f='out/%s.txt'%name
    if m.get('printed') or not os.path.exists(f): continue
    p=parse(f)
    if not p['ok']: continue
    pre=sum(p['pre'])/max(1,len(p['pre'])) if p['pre'] else float('nan')
    ex=sum(p['ex']); cells=sum(p['cells']); cex=sum(p['cellex'])
    res[name]=dict(m,pre=pre,pre_each=p['pre'],ex=ex,cells=cells,cells_exact=cex,delta_pre=pre-B_pre,ex_ratio=ex/B_ex,
        weight=2**(pre-B_pre)*ex/B_ex if ex else 0.0)
    r=res[name]
    print('%-26s pre %8.3f (d %+7.3f) cells %5d EX %5d (x%.3f) rel.event-weight %.5f'%(name,pre,pre-B_pre,cells,ex,ex/B_ex,r['weight']))
json.dump(dict(base=dict(pre=B_pre,ex=B_ex,cells=sum(base['cells'])),res=res),open('results.json','w'),indent=1)
