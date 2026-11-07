#!/usr/bin/env python3
"""tail_var_gen.py : one tail replica per distinct verified 39-step pair (owner 10-27: the pair is our choice; pick the best tail).
For each FOUND file: CV = chain, MX = M1, check M2 == MX + DL (the characteristic's modular differences), PIN = W16, W17 of MX's
expansion (self-tested against the shipped replica's own CV/MX/PIN). Writes tail_var/<sig>/r39tail_free.py and a run list."""
import re, os, sys, glob, shutil
HERE = os.path.dirname(os.path.abspath(__file__)); SRC = os.path.join(HERE, 'tail', 'r39tail_free.py')
G = os.path.normpath(os.path.join(HERE, '..', '..', 'game', 'climber', 'guided'))
M = 0xffffffff
def rotr(x, n): return ((x >> n) | (x << (32 - n))) & M
def s0(x): return rotr(x, 7) ^ rotr(x, 18) ^ (x >> 3)
def s1(x): return rotr(x, 17) ^ rotr(x, 19) ^ (x >> 10)
def w16_17(W):
    w16 = (s1(W[14]) + W[9] + s0(W[1]) + W[0]) & M; w17 = (s1(W[15]) + W[10] + s0(W[2]) + W[1]) & M; return w16, w17
src = open(SRC).read()
cv0 = [int(x, 16) for x in re.search(r'^CV=\[int\(x,16\)for x in "([0-9a-f ]+)"', src, re.M).group(1).split()]
mx0 = [int(x, 16) for x in ''.join(re.search(r'^MX=\[int\(x,16\)for x in\(("[^)]+)\)', src, re.M).group(1).split('"')[1::2]).split()]
DL = eval(re.search(r'^DL=(\[.*\])$', src, re.M).group(1))
pin0 = eval(re.search(r'^PIN=(\{.*\})$', src, re.M).group(1))
import io, contextlib
sys.path.insert(0, os.path.normpath(os.path.join(HERE, '..', '..', 'pkg_r39_newchar', 'sha256', 'experiments')))
with contextlib.redirect_stdout(io.StringIO()):
    import r39joint as J
def pin_of(cv, mx):
    A, E, W = J.traj(cv, mx); return E[20], E[21]          # replica PIN[16], PIN[17] = E rows 17, 18 of the MX message (self-tested)
assert pin_of(cv0, mx0) == (pin0[16], pin0[17]), ('PIN rule self-test failed', pin_of(cv0, mx0), pin0)
print('self-test ok: PIN = E17,E18 of traj(CV, MX); DL =', [hex(d) for d in DL if d])
# one FOUND file per distinct characteristic (classify.py output pasted by the dispatcher)
PAIRS = dict(l.split() for l in """35d0d27869 wiggle/FOUND_w_W9W10_s1.txt
3602c1ee40 wiggle/FOUND_w_W10W11_s1.txt
3d6ddf7dbe wiggle/FOUND_w_W11W12_s1.txt
3e4c6ceaf9 wiggle/FOUND_w_W10W12_s1.txt
566c26bd10 wiggle/FOUND_w_A0-3_s1.txt
58fca7a18e wiggle/FOUND_w_W9W11_s1.txt
7111e7edc4 cloud_found/p39seed/FOUND_n39_free_W0-15_s2.txt
7f900642a2 cloud_found/p39seed/FOUND_n39_free_W0-15_s4.txt
9755b8d5b6 wiggle/FOUND_w_W8W9_s1.txt
b09c9d592d wiggle/FOUND_w_W8W11_s1.txt
b8cb3120ea cloud_found/p39seed/FOUND_n39_free_W0-15_s3.txt
cde0acf011 wiggle/FOUND_w_W12_s1.txt
dade958e31 p39seed/FOUND_p39char_s101.txt
fbe0332343 wiggle/FOUND_w_W11_s1.txt""".strip().split('\n'))
runs = []
for sig, rel in PAIRS.items():
    f = os.path.join(G, rel)
    if not os.path.exists(f):
        alt = glob.glob(os.path.join(G, '**', os.path.basename(rel)), recursive=True); f = alt[0] if alt else None
    if not f: print('MISSING', sig, rel); continue
    s = open(f).read()
    cv = [int(x, 16) for x in re.search(r'chain=([0-9a-f ]+)', s).group(1).split()][:8]
    m1 = [int(x, 16) for x in re.search(r'M1: W=([0-9a-f ]+)', s).group(1).split()]
    m2 = [int(x, 16) for x in re.search(r'M2: W=([0-9a-f ]+)', s).group(1).split()]
    dl = [(b - a) & M for a, b in zip(m1, m2)]
    if dl != DL and [(a - b) & M for a, b in zip(m1, m2)] == DL: m1, m2 = m2, m1; dl = DL   # MX is the message with MX + DL = MY
    if dl != DL:
        print('SKIP', sig, 'modular differences differ from the replica DL:', [hex(d) for d in dl if d]); continue
    p16, p17 = pin_of(cv, m1)
    d = os.path.join(HERE, 'tail_var', sig); os.makedirs(d, exist_ok=True)
    t = src
    t = re.sub(r'^CV=\[int\(x,16\)for x in "[0-9a-f ]+"', 'CV=[int(x,16)for x in "%s"' % ' '.join('%08x' % v for v in cv), t, flags=re.M)
    t = re.sub(r'^MX=\[int\(x,16\)for x in\("[^)]+\)', 'MX=[int(x,16)for x in("%s "\n"%s")' % (' '.join('%08x' % v for v in m1[:8]), ' '.join('%08x' % v for v in m1[8:])), t, flags=re.M)
    t = re.sub(r'^PIN=\{.*\}$', 'PIN={16:0x%08x,17:0x%08x}' % (p16, p17), t, flags=re.M)
    open(os.path.join(d, 'r39tail_free.py'), 'w', newline='\n').write(t)
    runs.append(sig); print('wrote', sig, 'from', os.path.basename(f), 'PIN', hex(p16), hex(p17), '(same as shipped)' if (p16, p17) == (pin0[16], pin0[17]) else '')
open(os.path.join(HERE, 'tail_var', 'RUNS.txt'), 'w', newline='\n').write('\n'.join(runs) + '\n'); print(len(runs), 'variants staged')
