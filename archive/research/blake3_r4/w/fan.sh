
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/blake3_r4/b4/pkg/blake3/experiments"
( ulimit -v 2000000; nice -n 10 python3 -B - <<'PY'
import sys
sys.dont_write_bytecode=True
import bsrho as b
g,out=b.trace(256)
cnt={}
for k in range(257,len(g.nodes)):
    op,a,c=g.nodes[k]
    for v in {a,c}: cnt[v]=cnt.get(v,0)+1
    if a==c: print("same operand gate",k)
from collections import Counter
print(Counter(cnt.values()))
nout=[o[0] for o in out]
G=len(g.nodes)-1
print("outputs are last 256 gates in order:", nout==list(range(G-255,G+1)))
print("outputs used as operands (fanout>0):", sum(1 for o in nout if o in cnt))
print("inputs never used:", sum(1 for j in range(1,257) if j not in cnt), "max reg", )
PY
)
