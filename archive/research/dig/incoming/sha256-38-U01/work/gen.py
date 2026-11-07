
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

import re, json
SRC=_hca_public_path_text('__HCA_WORKSPACE__/research/tools/traillab/chi/chi38.txt')
lines=open(SRC,encoding='utf-8').read().split('\n')
def rowidx(r):
    for i,l in enumerate(lines):
        if re.match(r'row\s+%d\s'%r,l): return i
def getrow(r):
    p=lines[rowidx(r)].split(); return p[2],p[3],p[4]
def setrow(ls,r,A=None,E=None,W=None):
    for i,l in enumerate(ls):
        if re.match(r'row\s+%d\s'%r,l):
            p=l.split(); a,e,w=p[2],p[3],p[4]
            ls[i]='row %2d %s %s %s'%(r,A or a,E or e,W or w); return
    raise Exception
# signed patterns from sdiff.txt
def pats(delta):
    t=open('sdiff.txt').read().split('=== sdiff ')
    for blk in t:
        if blk.startswith(delta):
            return [m.group(1) for m in re.finditer(r'^\s+([=nu]{32})\s+xor',blk,re.M)]
def overlay(orig,pat):
    o=list(orig); overl=[]
    for i,c in enumerate(o):
        if c in 'nu': o[i]='='
    for i,c in enumerate(pat):
        if c!='=':
            if o[i]!='=': overl.append((31-i,o[i]))
            o[i]=c
    return ''.join(o),overl
tests=[]  # name, kind, group, desc, modified lines
def variant(name,fn,desc):
    ls=list(lines); fn(ls)
    open('chi/%s.txt'%name,'w',newline='\n').write('\n'.join(ls))
    tests.append(dict(name=name,desc=desc))
A17,E17,W17=getrow(17); A18,E18,W18=getrow(18); A21,E21,W21=getrow(21)
cellid={'A17':'sha256-38|r17|A|Q4','E18':'sha256-38|r18|E|Q4','E21':'sha256-38|r21|E|Q4'}
meta={}
for obj,orig,delta,row,col in (('A17',A17,'e0000000',17,'A'),('E18',E18,'0003fff0',18,'E'),('E21',E21,'e0000000',21,'E')):
    P=pats(delta)
    for k,p in enumerate(P):
        new,ov=overlay(orig,p)
        name='%s_p%02d'%(obj,k)
        isorig = (new==orig)
        if isorig: 
            meta[name]=dict(cell=cellid[obj],kind='alt',obj=obj,pattern=p,printed=True,overlap=ov); continue
        variant(name,lambda ls,row=row,col=col,new=new: setrow(ls,row,**{col:new}),'')
        meta[name]=dict(cell=cellid[obj],kind='alt',obj=obj,pattern=p,newrow=new,printed=False,overlap=ov)
rels={'r17':[('A17',9,'A17',20),('A17',6,'A17',18),('A17',8,'A17',17),('E17',15,'E18',15),('E17',24,'E18',24)],
 'r18':[('A18',29,'A19',29),('E18',0,'E18',13)],
 'r19':[('E19',6,'E19',19),('E19',20,'E19',2)],
 'r21':[('E21',2,'E21',16)],
 'r23':[('W23',0,'W23',30),('W23',1,'W23',31),('W23',14,'W23',21),('W23',16,'W23',25)]}
for r,L in rels.items():
    for (a,i,b,j) in L:
        pat=re.compile(r'^x2 %s\[%d\] (=|!=) %s\[%d\]$'%(a,i,b,j))
        idx=[n for n,l in enumerate(lines) if pat.match(l)]
        # also reversed order in file (E19[20] = E19[2])
        assert len(idx)==1,(a,i,b,j,idx)
        orig=pat.match(lines[idx[0]]).group(1)
        flip='!=' if orig=='=' else '='
        name='REL_%s_%s%d_%s%d'%(r,a,i,b,j)
        def fn(ls,n=idx[0],a=a,i=i,b=b,j=j,flip=flip): ls[n]='x2 %s[%d] %s %s[%d]'%(a,i,flip,b,j)
        variant(name,fn,'')
        meta[name]=dict(cell='sha256-38|%s|REL|Q4'%r,kind='rel',printed_rel='%s[%d] %s %s[%d]'%(a,i,orig,b,j),opposite='%s[%d] %s %s[%d]'%(a,i,flip,b,j))
json.dump(meta,open('meta.json','w'),indent=1)
print(len(meta),[ (k,v.get('overlap')) for k,v in meta.items() if v.get('overlap')])
print([k for k,v in meta.items() if v.get('printed')])
