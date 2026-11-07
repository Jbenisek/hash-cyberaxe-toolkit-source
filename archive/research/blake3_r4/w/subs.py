
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

import json, sys
d = json.load(open(_hca_public_path_text('__HCA_WORKSPACE__/research/blake3_r4/w/subs_all.json'), encoding='utf-8'))
rows = d if isinstance(d, list) else d.get('submissions', d.get('data', d))
print(type(d), len(rows))
print(json.dumps(rows[0], indent=1)[:1500])
ids = ('62cfd777', '0a9640ed', '3356413f', '6ae36351')
for r in rows:
    sid = r.get('id') or r.get('submissionId') or ''
    if sid[:8] in ids:
        print({k: (str(v)[:120]) for k, v in r.items() if k in ('id', 'status', 'score', 'valid', 'validationStatus', 'state', 'rounds', 'roundCount', 'track', 'benchmark', 'createdAt', 'metrics')})
r4 = [r for r in rows if 'r4' in json.dumps(r)[:3000] and 'blake3' in json.dumps(r)[:3000].lower()]
print("rows mentioning r4 and blake3 near top:", len(r4))
