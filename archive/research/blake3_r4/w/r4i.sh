
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
hits=[0]; mk0=b.Gen.mk; newn=[0]
def mk(self,op,a,c):
    self.calls+=1
    if a>c: a,c=c,a
    k=(op,a,c)
    if k in self.memo: hits[0]+=1
    else: newn[0]+=1
    if k not in self.memo:
        self.nodes.append(k); self.memo[k]=len(self.nodes)-1
    return self.memo[k]
b.Gen.mk=mk
g,out=b.trace(256)
print("nodes",len(g.nodes),"memo hits",hits[0],"new",newn[0])
# reachability
seen=set(o[0] for o in out)
for k in range(len(g.nodes)-1,0,-1):
    if k in seen and g.nodes[k][0] in "xao":
        seen.add(g.nodes[k][1]); seen.add(g.nodes[k][2])
gates=[k for k in range(1,len(g.nodes)) if k in seen and g.nodes[k][0] in "xao"]
print("reachable gates",len(gates))
# per-op: dead nodes by type
dead=[k for k in range(257,len(g.nodes)) if k not in seen]
print("dead",len(dead))
PY
)
