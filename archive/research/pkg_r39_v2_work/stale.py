# stale.py TAG : template-only values (template != new) still present in the new package texts
import sys, json
from nums import nums, CASES
tag = sys.argv[1]; Vt = nums(CASES['best']); V = nums(CASES[tag])
files = ['sha256/proof.md', 'sha256/claim.json', 'sha256/experiments/manifest.json', 'submission-note-r39.md']
txt = {f: open('../pkg_r39_%s/%s' % (tag, f), encoding='utf-8').read() for f in files}
extra = ['0.0459', '2.6 standard errors', '2.6 SE', '1998', 'W1` is even', 'W1 is even', '58fca7a18e', '0.0711', '31,570', '-74.4113', '-74.4578', '-74.4669', 'W11` and `W12', 'W11 and W12', '17.1', '40.9', '117.0545', '-76.59', '80,621', '5,795', '4.440', '1136.7', '313.9', '0.07 bit',
         '805, 835', '51.9', '229.9', '12.77', '3.65', '734', 'published_w', 'pair_is_published', '(2b4af365', 'b36f5329', 'abc8c59c']
for k, vt in Vt.items():
    if k in ('_tq', 'appA') or V.get(k) == vt: continue
    vals = vt if isinstance(vt, list) else [vt]
    for x in vals:
        x = str(x)
        if len(x) < 4: continue
        for f, t in txt.items():
            if x in t: print('STALE', k, repr(x), f, t.count(x))
for x in extra:
    for f, t in txt.items():
        if x in t: print('EXTRA', repr(x), f, t.count(x))
