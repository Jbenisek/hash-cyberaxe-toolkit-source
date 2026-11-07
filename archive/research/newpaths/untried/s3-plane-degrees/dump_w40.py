"""Dump the certified field W40 (35 SOLCLOUD_16 Appendix B vectors + c0..c4 of D17 section 9) as 80-hex-digit lines,
exactly as research/sha3r6/lowdegree/cube_degree.py builds it (imported, not re-typed). Also prints its GF(2) rank."""

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
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/sha3r6/lowdegree'))
import cube_degree as cd

OUT = _hca_public_path_text('__HCA_WORKSPACE__/research/newpaths/untried/s3-plane-degrees/w40.txt')
with open(OUT, 'w', newline='\n') as f:
    for v in cd.W:
        f.write('%080x\n' % v)
print('vectors', len(cd.W), 'rank', cd.rank(cd.W))
