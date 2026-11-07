
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

import sys,json,random,glob,math
sys.path.insert(0,_hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/pareto_clone'))
sys.path.insert(0,_hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/orchard/impl'))
from verifier import poseidon as V
import poseidon_ref as R
PC=_hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/pareto_clone/pareto')
P=R.P
print("p==V.P",P==V.P, "bitlen",P.bit_length(),"p-2^254",hex(P-(1<<254)))
# 1 verifier vs ours
random.seed(1);bad=0;n=0
for r in list(range(0,57)):
  for _ in range(6):
    a,b=random.randrange(P),random.randrange(P)
    m=a.to_bytes(32,'little')+b.to_bytes(32,'little')
    n+=1
    if V.digest(m,r)!=R.hash_reduced(a,b,r).to_bytes(32,'little'): bad+=1
print("verifier vs ours (r 0..56 x6):",n-bad,"/",n)
# edge inputs
for a,b in [(0,0),(P-1,P-1),(0,P-1)]:
  m=a.to_bytes(32,'little')+b.to_bytes(32,'little')
  print("edge",a==0,V.digest(m,1)==R.hash_reduced(a,b,1).to_bytes(32,'little'))
for bad_m in [(P).to_bytes(32,'little')+bytes(32), bytes(63), bytes(65), bytearray(64)]:
  try: V.digest(bad_m,1); print("ACCEPTED bad")
  except Exception as e: print("rejected",type(e).__name__)
# profiles
fs=sorted(glob.glob(PC+r'\target-profiles\poseidon-orchard-r*-prefix-v1.json'))
print("profiles",len(fs))
mis=0
for f in fs:
  d=json.load(open(f)); r=d['rounds']
  assert f.endswith(f"r{r}-prefix-v1.json") and d['id']==f"poseidon-orchard-r{r}-prefix-v1"
  rs=d['round_selection']; exp=f"Original full rounds 0..3, original partial rounds 4..{3+r}" if r else "partial rounds 4..3"
  if exp not in rs: mis+=1; print("round_selection text mismatch",r,rs)
  if int(d['field_modulus'],16)!=P: print("modulus mismatch")
print("round_selection mismatches:",mis)
d=json.load(open(fs[0])); print("full_rounds field:",d['full_rounds'],"(true full rounds 8, partial 56)")
print("digest_bits field:",d['digest_bits'],"actual output bits",(P-1).bit_length(), "log2p/2",math.log2(P)/2)
# cost C(r)
cost=json.load(open(PC+r'\orchard-cost-v2.json'))
print([k for k in cost if 'norm' in k.lower() or 'C' == k])
# count ops of verifier formula
def ops(r):
  full=3+9+9+6; part=3+3+9+6
  return 8*full+r*part
print("C(r) ops count == 216+21r:",all(ops(r)==216+21*r for r in range(57)))
# alt counts: x^5 via mult, MDS adds 6, const adds 3
print("full-round ops",27,"partial",21, " r=56 total",ops(56),"C(1)",ops(1))
# capacity
print("2^65 = L*2^64, L=2:",(1<<65)==2*(1<<64), "< p",(1<<65)<P)
# MDS invertible, constant facts
M=R.MDS
det=(M[0][0]*(M[1][1]*M[2][2]-M[1][2]*M[2][1])-M[0][1]*(M[1][0]*M[2][2]-M[1][2]*M[2][0])+M[0][2]*(M[1][0]*M[2][1]-M[1][1]*M[2][0]))%P
print("MDS det nonzero",det!=0)
print("gcd(5,p-1)",math.gcd(5,P-1),"gcd(5,p-1) means x^5 permutation:",math.gcd(5,P-1)==1)
print("p mod 5",P%5)
print("2-adicity p-1:",((P-1)&-(P-1)).bit_length()-1)
# schedule: r=1 uses index
print("schedule(1)",R.schedule(1),"verifier index tuple r=1",[*range(4),*range(4,5),*range(60,64)])
