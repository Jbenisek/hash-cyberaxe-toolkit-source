"""check2-3: compare run lines reproduced here (binary built from the scout's source) with the scout's logs."""

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

import sys
sys.dont_write_bytecode = True
S = _hca_public_path_text('__HCA_WORKSPACE__/research/sha256grid/scout2-3') + '\\'
C = _hca_public_path_text('__HCA_WORKSPACE__/research/sha256grid/check2-3') + '\\'

def runs(fn):
    d = {}
    for line in open(fn):
        if line.startswith('run '):
            d[int(line.split()[1])] = line.rstrip('\n')
    return d

for mine, theirs in (('rep_g2a.log', 'g2_main.log'), ('rep_g2b.log', 'g2_main.log'), ('rep_g3a.log', 'g3_v1.log')):
    a = runs(C + mine); b = runs(S + theirs)
    same = sum(1 for r in a if b.get(r) == a[r]); diff = [r for r in a if r in b and b[r] != a[r]]; miss = [r for r in a if r not in b]
    print('%s vs %s: %d runs reproduced, %d identical lines, %d differ, %d missing in scout log; run range %d..%d'
          % (mine, theirs, len(a), same, len(diff), len(miss), min(a), max(a)))
    for r in diff[:3]:
        print('  mine  :', a[r]); print('  theirs:', b[r])
