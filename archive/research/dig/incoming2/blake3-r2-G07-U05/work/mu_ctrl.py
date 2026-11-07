# MU R3 control. Rule written before the run:
# (1) recount: sums over the 4 recorded tsv files must give 1196284356 total debit and mean 0.004352057134...
# (2) known answer: re-run contexts i in 0..N-1 plus the 8 recorded largest-debit contexts with fl_run.py (run copy, same seeds): D_i must equal recorded exactly.
# (3) negative control: same contexts with fl_ship.py (shipped program, no U_PRE): D_i must equal recorded - 15*prechecked_i exactly (and so differ wherever prechecked>0).

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

import sys, os, glob, time
sys.dont_write_bytecode=True
here=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,here)
import importlib
run=_hca_public_path_text('__HCA_WORKSPACE__/research/tools/build_pkg/scratch/pkgB3H/run')
rec={}
for k in range(4):
    for ln in open(os.path.join(run,'out_w%d.tsv'%k)):
        p=ln.split('\t'); i=int(p[0]); rec[i]=[int(x) for x in p[1:]]
S=sum(v[0]+v[1] for v in rec.values()); n=len(rec)
print('recount contexts',n,'total D',S,'mean',S/2**38, 'prechecked sum',sum(v[2] for v in rec.values()))
import statistics
big=sorted(rec,key=lambda i:-(rec[i][0]+rec[i][1]))[:8]
N=int(sys.argv[1]); ids=list(range(N))+big
A=importlib.import_module('fl_run'); B=importlib.import_module('fl_ship')
okA=okB=0; diffB=0; t=time.time()
for i in ids:
    seed=b"b3H-prereg-20261011/%d"%i
    oa=A.walk_thi(seed,bits=16,credit=10**30,full_every=10**18)[3]
    ob=B.walk_thi(seed,bits=16,credit=10**30,full_every=10**18)[3]
    r=rec[i]; Da=oa['screen_debits']+oa['solver_debits']; Db=ob['screen_debits']+ob['solver_debits']; Dr=r[0]+r[1]
    okA+= (Da==Dr); okB+= (Db==Dr-15*r[2]); diffB+= (Db!=Dr)
print('contexts',len(ids),'run-copy equals recorded',okA,'ship equals recorded-15*prechecked',okB,'ship differs from recorded',diffB,'secs',round(time.time()-t))
