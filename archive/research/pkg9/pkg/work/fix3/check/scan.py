
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

import re
from pathlib import Path
P = Path(_hca_public_path_text('__HCA_WORKSPACE__/research/pkg7'))
INJECT = re.compile(r"ignore (all|any|the|previous|prior)|disregard|you (must|should|are an?) |as an ai|system prompt|"
                    r"dear (judge|reviewer)|to the (judge|reviewer|model)|assistant:|score this|award|rate this|"
                    r"do not (flag|report|penal)|override|[redacted unsafe instruction]|prompt", re.I)
LINK = re.compile(r"https?://|www\.", re.I)
files = [p for p in sorted((P / 'blake3-r2').rglob('*')) if p.is_file()] + [P / 'submission-note-r2.md']
for p in files:
    raw = p.read_bytes()
    na = sum(1 for b in raw if b > 127)
    cr = raw.count(b'\r')
    t = raw.decode('utf-8', 'replace')
    inj = [m.start() for m in INJECT.finditer(t)]
    ln = [m.start() for m in LINK.finditer(t)]
    html = t.count('<!--')
    print('%-32s nonascii %d CR %d inject %d links %d htmlcomments %d' % (p.relative_to(P), na, cr, len(inj), len(ln), html))
