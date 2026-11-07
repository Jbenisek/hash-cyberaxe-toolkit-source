# stage_consts.py PKG VARSDIR B W : advice lines 14-16 from the pair's r39joint.py, halts from tc_<sig>.py output
import sys, re
pkg, vd, B, W = sys.argv[1:5]
p = pkg + '/sha256/experiments/r39joint.py'; t = open(p, encoding='utf-8').read()
src = open(vd + '/r39joint.py', encoding='utf-8').read()
for k in ('CV_PUB', 'M_PUB', 'MP_PUB'):
    old = re.search(r'^%s=H\(".*"\)$' % k, t, re.M).group(0); new = re.search(r'^%s=H\(".*"\)$' % k, src, re.M).group(0)
    t = t.replace(old, new)
t = re.sub(r'^B_WINDOWS=\d+$', 'B_WINDOWS=' + B, t, flags=re.M); t = re.sub(r'^W_BUDGET=\d+$', 'W_BUDGET=' + W, t, flags=re.M)
open(p, 'w', encoding='utf-8', newline='\n').write(t); print(p, 'ok')
