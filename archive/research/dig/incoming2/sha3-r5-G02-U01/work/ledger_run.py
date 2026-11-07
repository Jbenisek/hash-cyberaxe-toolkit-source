
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

import re,sys
src=open(_hca_public_path_text('__HCA_WORKSPACE__/research/tools/build_pkg/scratch/pkgR5T/pkg/sha3-256-r5/proof.md'),encoding='utf-8').read()
i=src.index('I.4. The ledger program and its output')
m=re.search(r'```python\n(.*?)```',src[i:],re.S)
code=m.group(1)
open('ledger_extracted.py','w',encoding='utf-8').write(code)
