
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

import os
w = _hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming/sha256-37-U01/work')
src = open(_hca_public_path_text('__HCA_WORKSPACE__/research/tools/traillab/digs/zoneD/zoneD.c'), encoding='utf8').read()
i = src.index('/* ---------------- cells */')
head = src[:i]
head = head[head.index('#define _GNU_SOURCE'):]
head = head.replace('"../../src/traillab.h"', '"../../../../tools/traillab/src/traillab.h"').replace('"../../src/smc.h"', '"../../../../tools/traillab/src/smc.h"')
new = open(os.path.join(w, 'newpart.c'), encoding='utf8').read()
open(os.path.join(w, 'zoneD14.c'), 'w', encoding='utf8').write(head + new)
open(os.path.join(w, 'build.sh'), 'w', newline='\n').write(_hca_public_path_text('cd __HCA_WORKSPACE__/research/dig/incoming/sha256-37-U01/work\ngcc -O2 -march=native -w -pthread -o zoneD14 zoneD14.c ../../../../tools/traillab/src/traillab.c ../../../../tools/traillab/src/smc.c ../../../../tools/traillab/src/diff.c -lm 2>&1 | head -30\n'))
for r in (14, 8):
    open(os.path.join(w, 'run%d.sh' % r), 'w', newline='\n').write(_hca_public_path_text('cd __HCA_WORKSPACE__/research/dig/incoming/sha256-37-U01/work\ntimeout 900 ./zoneD14 %d > out_row%d.txt 2>&1\n') % (r, r))
