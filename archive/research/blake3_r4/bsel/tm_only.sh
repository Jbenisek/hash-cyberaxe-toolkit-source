
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/blake3_r4/bsel"
( ulimit -v 2000000; cd pkg/blake3/experiments
python3 -B - <<'PY'
import sys, time, json, hashlib
sys.dont_write_bytecode = True
import bsrho as b
seeds = [hashlib.sha256(("stats/%d" % i).encode()).hexdigest() for i in range(256)]
t=time.time(); b.serve({"experiment_id": "bsrho-n18", "trials": [{"trial": i, "seed": s} for i, s in enumerate(seeds)]}); t18=time.time()-t
t=time.time(); b.serve({"experiment_id": "proj-k0-w256", "trials": [{"trial": i, "seed": s} for i, s in enumerate(seeds)]}); t21=time.time()-t
json.dump({"t18": "%.1f" % t18, "t21": "%.1f" % t21}, open("../../../timing.json", "w")); print(t18, t21)
PY
)
