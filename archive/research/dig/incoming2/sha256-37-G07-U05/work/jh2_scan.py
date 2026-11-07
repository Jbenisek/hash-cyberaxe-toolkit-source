"""JUDGE.JH2 proxy check: provenance wording on H2/H3/H9 and organizer-attributed counts (sha256-37). Static, read-only."""

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

import json,re,sys
B=_hca_public_path_text('__HCA_WORKSPACE__/research')
PK=B+r'\dig\incoming2\sha256-37-G07-U05\work\pk'
S=B+r'\tools\build_pkg\scratch'
pk={
 'FAIL b74a016c (not_evaluable)':(PK+r'\fail_b74a016c_claim.json', PK+r'\fail_b74a016c_proof_numbered.md'),
 'PASS c22f86a2 (retry, D109 text)':(PK+r'\pass_c22f86a2_claim.json', PK+r'\pass_c22f86a2_proof.md'),
 'CUR   fcbc9c83 pkgR37X2 (passed)':(S+r'\pkgR37X2\pkg\sha256-r37\claim.json', S+r'\pkgR37X2\pkg\sha256-r37\proof.md'),
 'STAGED pkgR37M3':(S+r'\pkgR37M3\pkg\sha256-r37\claim.json', S+r'\pkgR37M3\pkg\sha256-r37\proof.md'),
}
ORG_RE=re.compile(r'no organizer experiment|organizer experiments?[^.]{0,140}\b(?:not|never)\b|\bnever\b[^.]{0,100}organizer|not organizer|no organizer|not organizer execution',re.I)
PART_RE=re.compile(r'stated premise, not an established fact',re.I)
def sentences(t): return [s.strip() for s in re.split(r'(?<=[.;])\s+|\n+',t) if s.strip()]
res={}
for name,(c,p) in pk.items():
    cl=json.load(open(c,encoding='utf-8')); pr=open(p,encoding='utf-8').read()
    pr=re.sub(r'(?m)^\d{6} \| ?','',pr)
    out={'prov':{}, 'sfs':[]}
    for h in cl['heuristics']:
        hid=h['id'].split('-')[0]
        if hid in ('H2','H3','H9'):
            t=' '.join(str(h.get(k,'')) for k in ('limitations','extrapolation'))
            lim=h.get('limitations','')
            out['prov'][hid]={'premise_wording':bool(PART_RE.search(lim)),'organizer_scope_wording':bool(ORG_RE.search(lim)),'in_limitations_only':True,'role':h['role']}
    txt=json.dumps(cl)+'\n'+pr
    for s in sentences(txt):
        for m in re.finditer(r'\b(\d+) of (128)\b',s):
            org=('organizer' in s.lower() or 'a0-sfs-r37' in s)
            repl=bool(re.search(r'replay|our |ffbe30bb|we ',s,re.I))
            out['sfs'].append({'n':int(m.group(1)),'of':128,'organizer_context':org,'own_replay_context':repl,'text':s[:170]})
    res[name]=out
ORGANIZER_COUNT=124   # returned pairs among trials 0..127 of a0-sfs-r37, from the b74a016c experiment-report.json (measured here)
print('organizer-observed a0-sfs-r37: 124 of 128 trials returned a pair (measured from experiment-report.json)')
for name,o in res.items():
    prov=o['prov']; miss=[h for h,v in prov.items() if not(v['premise_wording'] and v['organizer_scope_wording'])]
    bad=[s for s in o['sfs'] if s['organizer_context'] and not s['own_replay_context'] and s['n']!=ORGANIZER_COUNT and s['n']>=100]
    amb=[s for s in o['sfs'] if s['organizer_context'] and s['own_replay_context'] and s['n']!=ORGANIZER_COUNT and s['n']>=100]
    fire=bool(miss or bad)
    print('\n==',name)
    print(' (premise-statement, organizer-scope) H2/H3/H9:',{h:(v['premise_wording'],v['organizer_scope_wording']) for h,v in prov.items()})
    print(' provenance missing:',miss)
    for s in o['sfs']: print('  N of 128 ->',s['n'],'org' if s['organizer_context'] else '-', 'replay' if s['own_replay_context'] else '-','|',s['text'])
    print(' organizer-attributed count mismatch (no replay wording):',len(bad),' ambiguous (organizer + own-replay wording):',len(amb))
    print(' CHECK FIRES:',fire)
    o['fires']=fire; o['missing']=miss; o['bad']=len(bad); o['amb']=len(amb)
json.dump(res,open(PK+r'\..\jh2_scan_result.json','w'),indent=1)
