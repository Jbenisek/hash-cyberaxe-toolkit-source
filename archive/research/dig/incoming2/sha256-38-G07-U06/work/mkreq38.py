
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

import json,hashlib,sys,os
S=_hca_public_path_text('__HCA_WORKSPACE__/research/tools/build_pkg/scratch')
def canon(v): return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode()
TC='1240622223d057d2216e82f274765db69f56279f78dfb706022928fadf1aafc8'
for p,tag in [('pkgR38L','L'),('pkgR38N','N'),('pkgR38M3','M3')]:
    man=json.load(open(os.path.join(S,p,'pkg','sha256-r38','experiments','manifest.json')))
    for e in man['experiments']:
        for nm,hn in (('pub',None),('fresh','u06fresh')):
            sm=canon({"domain":"hashsmash-experiments-v1","seed":"hashsmash-public-seed-v1" if nm=='pub' else "u06-fresh-seed-"+hn,"holdout_nonce":None,"target_config_sha256":TC})
            req={"schema_version":1,"experiment_id":e['id'],"target_profile":"sha256-r38-prefix-v1","event":e['event'],"max_message_bytes":4096,
             "trials":[{"trial":i,"seed":hashlib.sha256(sm+canon([e['id'],i])).hexdigest()} for i in range(256)]}
            json.dump(req,open('req_%s_%s_%s.json'%(tag,e['id'],nm),'w'))
        print(tag,e['id'],e['program'])
