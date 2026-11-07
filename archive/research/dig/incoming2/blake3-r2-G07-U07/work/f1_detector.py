# Text detector for the F1 cause (advice construction not shown to be produced by the charged, bounded SEL).
# A proof PASSES the detector only if every marker of a closed construction path is present; each marker is a literal.

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

import re,sys,json
S=_hca_public_path_text('__HCA_WORKSPACE__/research/tools/build_pkg/scratch/')
files={
 'KNOWN-FAIL 5a08fffa (judge REFUTED F1)': 'proof_5a08fffa.md',
 'pkgB3L retry-1 (staged, pinned SEL)': S+'pkgB3L/pkg/blake3-r2/proof.md',
 'pkgB3U (filed c994a61f, PASSED)': S+'pkgB3U/pkg/blake3-r2/proof.md',
 'pkgB3V (staged, next)': S+'pkgB3V/pkg/blake3-r2/proof.md',
}
def markers(t):
    sel=t[t.find('The selection procedure SEL'):]
    return {
     'M1 SEL programs not in package':  bool(re.search(r'programs? of the participant that are not in the package',sel)),
     'M2 instance sha256 stated':        '286927dd9581cc54' in t,
     'M3 solver binary sha256 stated':   'binary SHA-256' in t or 'e0458ae23487a6d2' in t,
     'M4 generator listing shipped':     'class CNF' in t and 'def gen(' in t,
     'M5 replay record':                 bool(re.search(r'replay of 1\d October 2026',t)),
     'M6 compares output with stored record': bool(re.search(r'comparison of the 68 bytes',t)),
     'M7 admits SEL may return other/none': bool(re.search(r'(could|may) return (different|other)|SEL could return',t)),
    }
res={}
for k,f in files.items():
    t=open(f,encoding='utf-8').read(); m=markers(t); res[k]=m
    closed = (not m['M1 SEL programs not in package']) and m['M2 instance sha256 stated'] and m['M3 solver binary sha256 stated'] and m['M4 generator listing shipped'] and m['M5 replay record'] and m['M6 compares output with stored record']
    print('%-42s closed_path=%s'%(k,closed)); 
    for a,b in m.items(): print('    %-42s %s'%(a,b))
json.dump(res,open('f1_detector_out.json','w'),indent=1)
