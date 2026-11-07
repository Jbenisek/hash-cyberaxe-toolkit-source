
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

import hashlib, os, difflib, sys
P = _hca_public_path_text('__HCA_WORKSPACE__/research/pkg7')
PREV = os.path.join(P, 'work', 'fix3', 'prev')
OUT = os.path.join(P, 'work', 'fix3', 'check')

def sha(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

pairs = []
for root, dirs, files in os.walk(PREV):
    for fn in files:
        rel = os.path.relpath(os.path.join(root, fn), PREV)
        pairs.append(rel)
# also current files not in prev, within blake3-r2 and src
for sub in ['blake3-r2', 'src']:
    for root, dirs, files in os.walk(os.path.join(P, sub)):
        if '__pycache__' in root:
            continue
        for fn in files:
            rel = os.path.relpath(os.path.join(root, fn), P)
            if rel not in pairs:
                pairs.append(rel + '  [NEW, not in prev]')

lines = []
for rel in sorted(pairs):
    if rel.endswith('[NEW, not in prev]'):
        lines.append('NEW ' + rel)
        continue
    a = os.path.join(PREV, rel)
    if rel == 'validation_log_before.txt':
        lines.append('SKIP (log, no counterpart) ' + rel)
        continue
    b = os.path.join(P, rel)
    if not os.path.exists(b):
        lines.append('MISSING NOW ' + rel)
        continue
    ha, hb = sha(a), sha(b)
    lines.append(('SAME ' if ha == hb else 'DIFF ') + rel + ' ' + ha[:12] + ' ' + hb[:12])

with open(os.path.join(OUT, 'cmp_summary.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines) + '\n')

# full unified diffs of the text files that differ
with open(os.path.join(OUT, 'cmp_diffs.txt'), 'w', encoding='utf-8') as f:
    for ln in lines:
        if not ln.startswith('DIFF '):
            continue
        rel = ln.split()[1]
        a = open(os.path.join(PREV, rel), 'rb').read()
        b = open(os.path.join(P, rel), 'rb').read()
        f.write('#' * 70 + '\n# ' + rel + '\n')
        # byte-level facts
        f.write('# bytes %d -> %d; CRLF %d -> %d; trailing-newline %s -> %s; BOM %s -> %s\n' % (
            len(a), len(b), a.count(b'\r\n'), b.count(b'\r\n'), a.endswith(b'\n'), b.endswith(b'\n'),
            a.startswith(b'\xef\xbb\xbf'), b.startswith(b'\xef\xbb\xbf')))
        ta = a.decode('utf-8').splitlines(keepends=True)
        tb = b.decode('utf-8').splitlines(keepends=True)
        for d in difflib.unified_diff(ta, tb, 'prev/' + rel, 'now/' + rel, n=0):
            f.write(d if d.endswith('\n') else d + '\n')
print('\n'.join(l for l in lines if not l.startswith('SAME'))[:1500])
print('same:', sum(1 for l in lines if l.startswith('SAME')))
