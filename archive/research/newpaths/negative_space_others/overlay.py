
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

import csv, collections
W = _hca_public_path_text('__HCA_WORKSPACE__/research/newpaths')
cells = {}
for r in csv.DictReader(open(W + r"\negative_space\cells.csv", encoding="utf-8")):
    cells[(r['grid'], r['row'], r['col'])] = r['mark']
oth = [r for r in csv.DictReader(open(W + r"\negative_space_others\records_others.csv", encoding="utf-8"))
       if r['status'] in ('alive', 'dead', 'open') and r['base'] != 'r1']
G = [('freextech', 'free'), ('basextech', 'base'), ('layerxtech', 'layer')]
for g, ax in G:
    d = collections.defaultdict(list)
    for r in oth:
        d[(r[ax], r['tech'])].append(r)
    for (row, col), rs in sorted(d.items()):
        mark = cells.get((g, row, col), '?')
        st = collections.Counter(x['status'] for x in rs)
        flag = '' if mark.startswith('tried') and not (mark == 'tried-dead' and st['alive']) else '  <<<'
        print(f"{g:11s} {row:6s} x {col:6s} ours={mark:13s} theirs={dict(st)} ids={' '.join(x['id'] for x in rs)}{flag}")
