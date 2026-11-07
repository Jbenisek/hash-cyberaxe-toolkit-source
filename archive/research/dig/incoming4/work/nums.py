
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

import re,json,math
L=_hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/orchard/lean_r2/logs/')
txt=open(L+'ledger_r2.txt').read()
N={}
# per-centre stage totals (centre 0)
st={}
for m in re.finditer(r'^\s+(line_setup|random centre|build g|S\^\(\(p-1\)/2\) mod g|gcd\(g, S\^h-1\) \(half-gcd\)|root finding|sqrt \+ map back|verification \(2 reference hashes\))\s+arith=\s*(\d+) other=\s*(\d+) total=\s*(\d+)',txt,re.M):
    st.setdefault(m.group(1),(int(m.group(2)),int(m.group(3)),int(m.group(4))))
for k,v in st.items(): assert v[0]+v[1]==v[2],k
N['stages']=st
INIT=662427
B=st['line_setup'][2]+st['random centre'][2]+st['build g'][2]+st['S^((p-1)/2) mod g'][2]
Dbud=21108000000; gap=21000000
per=B+Dbud+gap
N['per_centre_worst']=per
tot4=INIT+4*per+187665120+1172907+200000
N['tot4']=tot4; N['units4']=tot4/258; N['log2_4']=math.log2(tot4/258)
N['log2_1']=math.log2((INIT+per+187665120/4+1172907+200000)/258)
mem=122747+40741792+65536+4096
N['mem']=mem; N['memlog2']=math.log2(mem); N['score']=math.log2(tot4/258)+max(0,math.log2(mem)-20)
# per-type
T=dict(add=13435325042,sub=12622540897,mul=12274801600,sqr=284827007,ld=15396537559,st=8656647975,ctl=84719163718)
tt=sum(T.values()); N['types_sum']=tt; N['types_total_all']=147592743256
N['types_share']={k:v/tt for k,v in T.items()}
# check run total vs types
print(tt, 147592743256, tt-147592743256)
# two-centre run observed total
cs=[73796042626,73796038203]; print(sum(cs)+INIT)
json.dump(N,open('nums.json','w'),indent=1,default=str)
print(json.dumps({k:v for k,v in N.items() if k!='stages'},indent=1))
print(st)
