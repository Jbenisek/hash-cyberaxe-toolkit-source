"""JUDGE.JSTALE detector for the staged sha256-r37 low-memory package: every ledger-class number in claim.json, proof.md and the note
is compared with what the shipped lowm.py executes (ledger(), memory_bytes(), FEASIBLE_L). Read-only; imports our own package code."""

# Publication path adapter: resolve data paths from the extracted source tree.
def _hca_public_path_text(value):
    if "__HCA_WORKSPACE__/" not in value:
        return value
    import os as _hca_os
    from pathlib import Path as _hca_Path
    root = _hca_os.environ.get("HASHCYBERAXE_WORKSPACE")
    if root is None:
        here = _hca_Path(__file__).resolve().parent
        root = next((str(p) for p in (here, *here.parents) if (p / "research").is_dir()), None)
    if root is None:
        raise FileNotFoundError("Extract the research source tree, or set HASHCYBERAXE_WORKSPACE to its archive directory.")
    return value.replace("__HCA_WORKSPACE__/", str(_hca_Path(root).resolve()).replace("\\", "/") + "/")

import sys, os, re, json, io, contextlib, importlib.util
S=_hca_public_path_text('__HCA_WORKSPACE__/research/tools/build_pkg/scratch')
def load(pkg):
    P=os.path.join(S,pkg,'pkg','sha256-r37','experiments','lowm.py')
    sys.argv=['lowm.py']; sys.path.insert(0,os.path.dirname(P))
    spec=importlib.util.spec_from_file_location('lowm_'+pkg,P); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
def truth(pkg):
    m=load(pkg); buf=io.StringIO()
    with contextlib.redirect_stdout(buf): L=m.ledger(show=False)
    tab,tot=m.memory_bytes()
    t={'time':str(L['time_log2']),'vbar2':'%.2f'%L['vbar'],'fixed':str(L['fixed']),'nfb':str(L['nfb']),'mem':str(tot),'nl':str(len(m.FEASIBLE_L)),
       'pairs':str(len(m.FEASIBLE_L)*65536) , 'vmax_fb':str(int(L['vmax_fb'])),'VMAX':str(L['VMAX']), 'mu':str(L['mu_req']), 'g':'%.3f'%L['g'],'ok_extra':['%.2f'%v for v in L['parts'].values()]+['1048576','048576']}
    return t,m
def texts(pkg):
    d=os.path.join(S,pkg,'pkg')
    cl=open(os.path.join(d,'sha256-r37','claim.json'),encoding='utf-8').read(); pr=open(os.path.join(d,'sha256-r37','proof.md'),encoding='utf-8').read().replace('\r\n','\n')
    nt=open(os.path.join(d,'submission-note-r37.md'),encoding='utf-8').read()
    return {'claim':json.dumps(json.loads(cl),ensure_ascii=False,indent=0),'proof':pr,'note':nt}, json.loads(cl)
def num(s): return s.replace(',','')
def scan(pkg,T):
    X,cl=texts(pkg); flags=[]; checked=0
    pats=[('time_log2 field',r'"time_log2": ([\d.]+)',['claim'],'time'),
          ('title score',r'^# .*?2\^(6\d\.\d+)\s*$',['proof'],'time'),
          ('vbar 5-digit.2dec',r'\b(\d{5}\.\d\d)\b',['claim','proof','note'],'vbar2'),
          ('N_FB value',r'N_FB = ([\d,]{15,})',['proof','note','claim'],'nfb'),
          ('memory bytes',r'\b(\d{3},\d{3}) bytes',['claim','proof','note'],'mem'),
          ('memory total row',r'\*\*(\d{3},\d{3}) = 2\^',['proof'],'mem'),
          ('fixed ops',r'(\d{3}) (?:counted )?fixed operations',['claim','proof','note'],'fixed'),
          ('row-16 pairs enumerated',r'enumeration of ([\d,]{7,9}) pairs',['claim','proof','note'],'pairs'),
          ('row-16 l count',r'on all (\d+) l\b',['claim','proof','note'],'nl'),
          ('vmax_fb',r'vmax_fb = ([\d,]{9,})',['claim','proof','note'],'vmax_fb'),
          ('V_MAX',r'V_MAX = ([\d,]{15,})',['claim','proof','note'],'VMAX')]
    for name,rx,where,key in pats:
        if key=='pairs' and 'R16x' not in X['proof']: continue
        for w in where:
            for mm in re.finditer(rx,X[w],re.M):
                checked+=1; got=num(next(g for g in mm.groups() if g)); ok=(got==T[key] or got in T['ok_extra'])
                if not ok: flags.append((name,w,got,T[key],X[w][max(0,mm.start()-50):mm.end()+30].replace('\n',' ')))
    # evidence_ids of every heuristic must start inside the proof at a non-blank line and within its length
    lines=X['proof'].split('\n'); n=len(lines); eid=[]
    for h in cl['heuristics']:
        for e in h.get('evidence_ids',[]):
            mm=re.match(r'proof:(\d+)-(\d+)$',e)
            if mm:
                a,b=int(mm.group(1)),int(mm.group(2)); checked+=1
                bad = b>n or a<1
                eid.append((h['id'][:3],e,bad,lines[a-1][:70] if 0<a<=n else ''))
                if bad: flags.append(('evidence_ids range',h['id'],e,'<=%d lines'%n,''))
    return flags,checked,eid
if __name__=='__main__':
    results={}
    T3,m3=truth('pkgR37M3'); print('TRUTH M3:',T3)
    for label,pkg,T in (('M3 text vs M3 ledger (the object)','pkgR37M3',T3),):
        f,c,e=scan(pkg,T); print('\n==',label,'checked',c,'flags',len(f))
        for x in f: print('  FLAG',x)
        for x in e: print('  evid',x)
        results[label]={'checked':c,'flags':len(f)}
    # controls: (a) the pre-fix lineage package R37M text against the M3 ledger (known stale), (b) negative control: R37M text against its own ledger
    f,c,e=scan('pkgR37M',T3); print('\n== CONTROL A: pkgR37M text vs M3 truth (known stale lineage) checked',c,'flags',len(f))
    for x in f: print('  FLAG',x[:4])
    results['controlA']={'checked':c,'flags':len(f)}
    try:
        TM,mm_=truth('pkgR37M'); print('TRUTH M:',TM)
        f,c,e=scan('pkgR37M',TM); print('\n== CONTROL B: pkgR37M text vs its own ledger (must be 0) checked',c,'flags',len(f))
        for x in f: print('  FLAG',x[:4])
        results['controlB']={'checked':c,'flags':len(f)}
    except Exception as ex: print('control B error',ex)
    json.dump(results,open(_hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming2/sha256-37-G07-U05/work/jstale_result.json'),'w'),indent=1)
