
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
export PATH="$HOME/.local/bin:$HOME/.bun/bin:$PATH" NO_COLOR=1
yukon submissions --all --json mooselumph/hashsmash-pareto/blake3 > "${HASHCYBERAXE_WORKSPACE}"/research/blake3_r7/subs8.json 2>/dev/null
python3 - <<'PY'
import json
d = json.load(open("${HASHCYBERAXE_WORKSPACE}/research/blake3_r7/subs8.json"))
print(type(d), len(d))
rows = d if isinstance(d, list) else d.get('submissions', d)
for r in rows:
    s = json.dumps(r)
    if any(x in s for x in ('a2e94df7', '57174971', '4a9f31b8')):
        print({k: (v if not isinstance(v, (dict, list)) else '...') for k, v in r.items()})
PY
