
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

from fractions import Fraction as F
import math
P=_hca_public_path_text('__HCA_WORKSPACE__/opus_cloud/Smash-claude-math-help-g3v211/results/pairs_453_weights.txt')
rows=[]
for l in open(P):
    t,s,w15,w13,p1=l.split()
    rows.append((t,s,F(w15),F(w13),F(p1)))
L=lambda x: math.log2(x) if x>0 else float('-inf')
S15=sum(r[2] for r in rows); S13=sum(r[3] for r in rows); S1=sum(r[4] for r in rows)
J15=sum(r[2]*r[4] for r in rows); J13=sum(r[3]*r[4] for r in rows)
print('pairs',len(rows),'nonzero W15',sum(1 for r in rows if r[2]>0),'W13',sum(1 for r in rows if r[3]>0))
print('sum W15 (side3, C15) log2 %.3f'%L(S15)); print('sum W13 (side3, C13) log2 %.3f'%L(S13))
print('sum P1avg over 453 pairs log2 %.3f'%L(S1))
print('sum P1avg over W15>0 pairs log2 %.3f'%L(sum(r[4] for r in rows if r[2]>0)))
print('joint C15 log2 %.3f  R=%.4f'%(L(J15),float(J15*2**128)))
print('joint C13 log2 %.3f  R=%.4f'%(L(J13),float(J13*2**128)))
print('product S15*S1 log2 %.3f'%L(S15*S1))
# per-t marginals
from collections import defaultdict
# max single pair
m=max(rows,key=lambda r:r[2]*r[4]); print('top pair',m[0],m[1],'%.2f %.2f %.2f'%(L(m[2]),L(m[4]),L(m[2]*m[4])))
srt=sorted(rows,key=lambda r:-r[2]*r[4]); acc=F(0)
for i,r in enumerate(srt[:10]):
    acc+=r[2]*r[4]; print(i,r[0],r[1],'W15 %.2f P1 %.2f joint %.2f cum %.3f'%(L(r[2]),L(r[4]),L(r[2]*r[4]),float(acc/J15)))
# side3 max, side1 max
print('max W15 %.2f  max P1 %.2f'%(L(max(r[2] for r in rows)),L(max(r[4] for r in rows))))
# distinct t, s
print('distinct t',len(set(r[0] for r in rows)),'distinct s',len(set(r[1] for r in rows)))
