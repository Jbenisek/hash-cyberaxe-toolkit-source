# classes.py : exact reachable set of class = sigma0(MY11) - sigma0(MX11) under base39's W11 signed row (MX: u-bit 0, n-bit 1;
# MY = MX + DL11), enumerating every value of the free '-' bits; marks seen/unseen against VALUE_MAP. Writes class_set_W11.tsv.
import re, collections, numpy as np
M = 0xffffffff
row = re.search(r'^\s*11 A: \S+ E: \S+ W: (\S+)', open('base39.xml').read(), re.M).group(1)
bits = {31 - j: ch for j, ch in enumerate(row)}
fix = sum(1 << i for i, c in bits.items() if c == 'n')                  # MX value on signed bits
DL = (sum(1 << i for i, c in bits.items() if c == 'u') - sum(1 << i for i, c in bits.items() if c == 'n')) & M
free = [i for i, c in bits.items() if c == '-']
def rotr(x, n): return ((x >> n) | (x << (32 - n))) & M
def s0(x): return rotr(x, 7) ^ rotr(x, 18) ^ (x >> 3)
# sanity on the published pair (FOUND li39): its class must equal the VALUE_MAP entry 2000bea0
s = open('../luna_found/FOUND_li39_tab23_s1.txt').read()
m1 = [int(x, 16) for x in re.search(r'M1: W=([0-9a-f ]+)', s).group(1).split()]; m2 = [int(x, 16) for x in re.search(r'M2: W=([0-9a-f ]+)', s).group(1).split()]
print('li39 DL11 ok', (m2[11] - m1[11]) & M == DL, 'class', '%08x' % ((s0(m2[11]) - s0(m1[11])) & M))
n = len(free); idx = np.arange(1 << n, dtype=np.uint64); x = np.full(1 << n, fix, dtype=np.uint64)
for k, i in enumerate(free): x |= ((idx >> np.uint64(k)) & np.uint64(1)) << np.uint64(i)
y = (x + np.uint64(DL)) & np.uint64(M)
def S0(v): r = lambda v, k: ((v >> np.uint64(k)) | (v << np.uint64(32 - k))) & np.uint64(M); return r(v, 7) ^ r(v, 18) ^ (v >> np.uint64(3))
c = (S0(y) - S0(x)) & np.uint64(M)
u, cnt = np.unique(c, return_counts=True)
seen = {l.split()[0] for l in open('../../../../pkg_r39_combined/work/tail_var/VALUE_MAP.txt') if l[:1] not in '#' and len(l.split()) == 5}
with open('class_set_W11.tsv', 'w', newline='\n') as f:
    f.write('# class count_of_2^%d status (W11 row %s, DL11 %08x)\n' % (n, row, DL))
    for v, k in sorted(zip(u.tolist(), cnt.tolist()), key=lambda t: -t[1]): f.write('%08x\t%d\t%s\n' % (v, k, 'seen' if '%08x' % v in seen else 'UNSEEN'))
print('free bits', n, 'reachable', len(u), 'seen', sum('%08x' % v in seen for v in u.tolist()), 'VALUE_MAP classes', len(seen), 'not reachable', sorted(seen - {'%08x' % v for v in u.tolist()}))
