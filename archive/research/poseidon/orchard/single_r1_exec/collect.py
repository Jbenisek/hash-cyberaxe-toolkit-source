import re, json, os, glob, sys
# usage: collect.py [LOG_PREFIX [OUT_JSON]]   defaults: single_  collisions.json   (reads logs/<prefix>*.txt, writes data/<out>)
HERE = os.path.dirname(os.path.abspath(__file__))
PREFIX = sys.argv[1] if len(sys.argv) > 1 else 'single_'
OUTJ = sys.argv[2] if len(sys.argv) > 2 else 'collisions.json'
os.makedirs(os.path.join(HERE, 'data'), exist_ok=True)
out = []
for f in sorted(glob.glob(os.path.join(HERE, 'logs', PREFIX + '*.txt'))):
    v = {}
    for line in open(f):
        m = re.match(r'COLLISION (\S+)\s+0x([0-9a-f]{64})', line)
        if m: v[m.group(1)] = int(m.group(2), 16)
    if 'digest' in v:
        out.append(dict(file=os.path.basename(f), **v))
json.dump(out, open(os.path.join(HERE, 'data', OUTJ), 'w'), indent=1)
print(len(out), 'collisions')
