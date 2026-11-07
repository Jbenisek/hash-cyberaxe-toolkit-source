
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

import json, os, re, difflib, math
from fractions import Fraction as Fr
P = _hca_public_path_text('__HCA_WORKSPACE__/research/pkg7')
PREV = os.path.join(P, 'work', 'fix3', 'prev')
OUT = os.path.join(P, 'work', 'fix3', 'check', 'words_out.txt')
o = []

def words_diff(name):
    a = open(os.path.join(PREV, name), encoding='utf-8').read().split()
    b = open(os.path.join(P, name), encoding='utf-8').read().split()
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    o.append('=== word diff ' + name)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag != 'equal':
            o.append('%s [%s] -> [%s]' % (tag, ' '.join(a[i1:i2]), ' '.join(b[j1:j2])))

for n in ['blake3-r2\\proof.md', 'submission-note-r2.md']:
    words_diff(n)

# claim.json: field-level
ca = json.load(open(os.path.join(PREV, 'blake3-r2', 'claim.json'), encoding='utf-8'))
cb = json.load(open(os.path.join(P, 'blake3-r2', 'claim.json'), encoding='utf-8'))
def walk(x, y, path):
    if type(x) != type(y):
        o.append('TYPE ' + path); return
    if isinstance(x, dict):
        if set(x) != set(y):
            o.append('KEYS ' + path + ' ' + str(set(x) ^ set(y)))
        for k in x:
            if k in y:
                walk(x[k], y[k], path + '.' + str(k))
    elif isinstance(x, list):
        if len(x) != len(y):
            o.append('LEN ' + path)
        for i, (u, v) in enumerate(zip(x, y)):
            walk(u, v, path + '[%d]' % i)
    elif x != y:
        o.append('CHANGED ' + path + (' : %r -> %r' % (x, y) if len(str(x)) < 80 else ''))
o.append('=== claim.json field diff')
walk(ca, cb, '')
o.append('submission_state=%r time_log2=%r' % (cb.get('submission_state'), cb.get('time_log2')))

# evidence ids: every proof:a-b range, prev vs now, compare first and last lines
pa = open(os.path.join(PREV, 'blake3-r2', 'proof.md'), encoding='utf-8').read().split('\n')
pb = open(os.path.join(P, 'blake3-r2', 'proof.md'), encoding='utf-8').read().split('\n')
o.append('=== evidence_ids ranges (prev range -> now range): first/last line identical?')
def ids(c):
    s = json.dumps(c)
    return re.findall(r'"evidence_ids": \[([^\]]*)\]', s)
for ia, ib in zip(ids(ca), ids(cb)):
    ra = re.findall(r'proof:(\d+)-(\d+)', ia)
    rb = re.findall(r'proof:(\d+)-(\d+)', ib)
    for (a1, a2), (b1, b2) in zip(ra, rb):
        a1, a2, b1, b2 = map(int, (a1, a2, b1, b2))
        f_ok = pa[a1 - 1] == pb[b1 - 1]
        l_ok = pa[a2 - 1] == pb[b2 - 1]
        # also: the text just outside the range
        before_ok = pa[a1 - 2] == pb[b1 - 2]
        after_ok = (pa[a2] if a2 < len(pa) else None) == (pb[b2] if b2 < len(pb) else None)
        flag = '' if (f_ok and l_ok and before_ok and after_ok) else '  <-- CHECK'
        o.append('%d-%d -> %d-%d first %s last %s before %s after %s%s | %s ... %s' % (
            a1, a2, b1, b2, f_ok, l_ok, before_ok, after_ok, flag, pb[b1 - 1][:40], pb[b2 - 1][:40]))

# arithmetic
W, MEMB = 18725, 131072
N = 1424469 * 2 ** 81
lN = math.log2(1424469) + 81
o.append('=== arithmetic')
o.append('log2 N = %.6f ; lN - 31.41 = %.5f' % (lN, lN - 31.41))
P_x2 = Fr(W * 47) + Fr(W * 135, 32) + 134 + 1 + Fr(W * 74 + 260 + 8, 2 ** 32) + Fr(16, 2 ** 64)
o.append('P = %.6f per trial %.8f' % (float(P_x2), float(P_x2 / MEMB)))
charged = Fr(77, 10) * MEMB
o.append('charged per X2 %.4f ; (charged - P)/W = %.6f' % (float(charged), float((charged - P_x2) / W)))
o.append('charge above budget %.4f percent' % (float((Fr(77, 10) / (P_x2 / MEMB) - 1) * 100)))
ind = 1 - Fr(255, 256) ** 7
def cost(share):
    return (Fr(W * 47) + W * 135 * share + 134 + 1 + Fr(W * 74 + 260 + 8, 2 ** 32) + Fr(16, 2 ** 64)) / MEMB
o.append('indep share %.8f ; cost at it %.6f ; cost at 0.0270 %.6f' % (float(ind), float(cost(ind)), float(cost(Fr(27, 1000)))))
eg = Fr(185355453) * N / 2 ** 128
eg2 = Fr(12147454997539, 65536) * N / 2 ** 128
o.append('expected good (floor count) %.6f ; (exact cons) %.6f' % (float(eg), float(eg2)))
for e in (1.87, float(eg)):
    o.append('m max for e=%.4f : %.5f' % (e, e / -math.log(0.607)))
for m in (3.74, 3.75):
    o.append('m=%.2f: 1-exp(-1.87/m)-0.003 = %.5f ; with %.4f: %.5f' % (m, 1 - math.exp(-1.87 / m) - 0.003, float(eg), 1 - math.exp(-float(eg) / m) - 0.003))
o.append('18725/16384 = %.8f ; 74899/65536 = %.9f' % (18725 / 16384, 74899 / 65536))
o.append('r_sub 194382080300609/1048576 = %.4f ; r_class 85074516985129/524288 = %.4f' % (
    194382080300609 / 1048576, 85074516985129 / 524288))
o.append('budget rate log2(2^84/N) = %.5f ; gap 84 - (lN-31.41) = %.4f' % (84 - lN, 84 - (lN - 31.41)))
o.append('margin 185355453.45/49.4e6 = %.5f' % (185355453.4536590576 / 49400000))
open(OUT, 'w', encoding='utf-8').write('\n'.join(o) + '\n')
print(len(o), 'lines written')
