
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
export PATH="$HOME/.local/bin:$HOME/.bun/bin:$PATH" NO_COLOR=1
cd ~/hashsmash/yukon/pos_b3r3pv
yukon benchmark show --json 2>/dev/null > "${HASHCYBERAXE_WORKSPACE}"/research/blake3_r4/w/bench_show.json; echo rc $?
yukon submissions --all --json 2>/dev/null > "${HASHCYBERAXE_WORKSPACE}"/research/blake3_r4/w/subs_all.json; echo rc $?
python3 - <<'PY'
import json
d=json.load(open("${HASHCYBERAXE_WORKSPACE}/research/blake3_r4/w/bench_show.json"))
def find(o,p=''):
    if isinstance(o,dict):
        for k,v in o.items():
            if 'dmission' in k or 'round' in k.lower() or k in ('name','updatedAt'): print(p+'/'+k, json.dumps(v)[:200])
            find(v,p+'/'+k)
    elif isinstance(o,list):
        for i,v in enumerate(o[:60]): find(v,p+'[%d]'%i)
find(d)
PY
