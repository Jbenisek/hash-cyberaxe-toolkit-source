
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/blake3_r4/b4/pkg/blake3/experiments"
( ulimit -v 2000000; time nice -n 10 python3 -B - <<'PY'
import sys
sys.dont_write_bytecode=True
import bsrho as b
st=b.Step(256)
code,regs=b.allocate(st)
print("gates",st.ops,st.by,"gen_calls",st.gen_calls,"regs",regs,"instr",len(code),"peak",st.peak_live())
g,out=b.trace(256)
print("nodes",len(g.nodes))
print("packed ops",b.packed_circuit(st.qwords)[1])
ph,filt,body,codeb,tmax=b.machine_constants(st)
print("PH",ph,"filt",filt,"body",body,"code bytes",codeb,"tmax",tmax)
PY
)
