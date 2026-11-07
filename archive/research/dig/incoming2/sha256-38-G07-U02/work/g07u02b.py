# metered static-size estimate of the "other routines" code (proof says 600 instr, asserted); passing-path op counts by section

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

import sys, math
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/tools/build_pkg/scratch/pkgR38M3/pkg/sha256-r38/experiments'))
import a0lean38 as L
cal=L.calibrate(full=False)
m=L.Mach(); fb=L.fb_scalars(m,L.PCV)
ev=[]
code=L.step3b.__code__
def tr(frame, event, arg):
    if frame.f_code is code:
        def lt(fr, ev_, a):
            if ev_=='line': ev.append((fr.f_lineno, fr.f_locals.get('i'), m.ops))
            return lt
        return lt
    return None
m=L.Mach(); sys.settrace(tr); r=L.step3b(m,L.PCV,fb,0xb75dae71); sys.settrace(None)
print('result', r is not None, 'total ops', m.ops)
# line numbers: loop header at 505
first505=[e for e in ev if e[0]==505][0][2]
print('ops before loop (prologue, straight line):', first505)
# ops per i (loop iteration, both members + row_check)
byi={}
prev=None
for ln,i,o in ev:
    if ln==505: pass
import collections
st={}
for k,(ln,i,o) in enumerate(ev):
    if ln==506 and i is not None: st.setdefault(i,o)
ks=sorted(st); 
for a,b in zip(ks,ks[1:]+[None]): 
    print('i',a,'ops', (st[b]-st[a]) if b else m.ops-st[a])
rc=0
