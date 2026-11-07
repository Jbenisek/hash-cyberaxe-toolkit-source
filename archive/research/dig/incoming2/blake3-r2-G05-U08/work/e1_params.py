# exhaustive over message lengths 1..3199: which (t,b,flags,h) the ORGANIZER verifier uses at each block role

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

import sys, collections
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/hash-smash/verifier'))
import blake3 as ver
log=[]
orig=ver._compress
def spy(cv,words,counter,block_len,flags,rounds):
    log.append((counter,block_len,flags,tuple(cv)==tuple(ver.IV))); return orig(cv,words,counter,block_len,flags,rounds)
ver._compress=spy
roles=collections.defaultdict(set); ncalls=0
for L in range(1,3200):
    log.clear(); ver.blake3(bytes(L),2)
    for t,b,f,iv in log:
        ncalls+=1
        if f&4: role='parent'
        else:
            s=f&1; e=f&2
            role='single' if s and e else 'first' if s else 'last' if e else 'mid'
        roles[role].add((b,f,'t=0' if t==0 else 't>=1','h=IV' if iv else 'h=CV'))
print('compressions seen',ncalls,'over',3199,'message lengths')
for r in ('single','first','mid','last','parent'):
    s=roles[r]
    print(r,'| classes',len(s),'| b:',sorted({x[0] for x in s})[:2],'..',max(x[0] for x in s),'(%d values)'%len({x[0] for x in s}),'| flags',sorted({x[1] for x in s}),'| t',sorted({x[2] for x in s}),'| h',sorted({x[3] for x in s}))
