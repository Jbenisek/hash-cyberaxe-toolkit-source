import json, sys
a = json.load(open(sys.argv[1], encoding='utf-8')); b = json.load(open(sys.argv[2], encoding='utf-8'))
diffs = []
def walk(x, y, p=''):
    if type(x) != type(y):
        diffs.append((p, str(x)[:80], str(y)[:80])); return
    if isinstance(x, dict):
        for k in sorted(set(x) | set(y)):
            if k not in x or k not in y: diffs.append((p + '/' + k, 'missing' if k not in x else 'present', 'missing' if k not in y else 'present'))
            else: walk(x[k], y[k], p + '/' + k)
    elif isinstance(x, list):
        if len(x) != len(y): diffs.append((p, 'len %d' % len(x), 'len %d' % len(y))); return
        for i, (u, v) in enumerate(zip(x, y)): walk(u, v, p + '[%d]' % i)
    elif x != y:
        diffs.append((p, str(x)[:80], str(y)[:80]))
walk(a, b)
print(len(diffs), "differences")
for d in diffs[:20]: print(d)
