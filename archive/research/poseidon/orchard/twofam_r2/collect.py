import re, json, os, glob, sys
HERE = os.path.dirname(os.path.abspath(__file__))
out = []
for f in sorted(glob.glob(os.path.join(HERE, 'logs', 'cert_r2_*.txt'))):
    v = {}
    for line in open(f):
        m = re.match(r'COLLISION (\S+)\s+0x([0-9a-f]{64})', line)
        if m: v[m.group(1)] = int(m.group(2), 16)
    if 'digest' in v:
        out.append(dict(file=os.path.basename(f), **v))
json.dump(out, open(os.path.join(HERE, 'data', 'collisions.json'), 'w'), indent=1)
print(len(out), 'collisions')
