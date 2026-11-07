# classvals3.py : one representative MX11 per sigma0 class (all 128 reachable classes of class_set_W11.tsv), consistent with base39's signed W11 row.
# Writes CLASSVALS3.tsv "class mx11 status" (li39's own value for its class). Same class function as cubes.py.
import re, random
M = 0xffffffff
row = re.search(r'^\s*11 A: \S+ E: \S+ W: (\S+)', open('base39.xml').read(), re.M).group(1)
bits = {31 - j: ch for j, ch in enumerate(row)}
fix = sum(1 << i for i, c in bits.items() if c == 'n'); freem = sum(1 << i for i, c in bits.items() if c == '-')
DL = (sum(1 << i for i, c in bits.items() if c == 'u') - sum(1 << i for i, c in bits.items() if c == 'n')) & M
r = lambda x, k: ((x >> k) | (x << (32 - k))) & M; s0 = lambda x: r(x, 7) ^ r(x, 18) ^ (x >> 3)
cls = lambda x: (s0((x + DL) & M) - s0(x)) & M
want = {l.split()[0]: l.split()[2] for l in open('class_set_W11.tsv') if l.strip() and not l.startswith('#')}
got = {'%08x' % cls(0x01003fbb): 0x01003fbb}
assert '%08x' % cls(0x01003fbb) == '2000bea0', '%08x' % cls(0x01003fbb)
random.seed(39); n = 0
while len(got) < len(want) and n < 2_000_000:
    x = (random.getrandbits(32) & freem) | fix; c = '%08x' % cls(x); n += 1
    if c in want and c not in got: got[c] = x
with open('CLASSVALS3.tsv', 'w') as f:
    f.write('# class mx11 status (one representative per reachable class; W11 row %s, DL %08x)\n' % (row, DL))
    for c in want: f.write('%s\t%08x\t%s\n' % (c, got[c], want[c]) if c in got else '%s\t-\t%s MISSING\n' % (c, want[c]))
print('classes', len(want), 'found', len(got), 'samples', n)
