'''Validate the C apply() against the pure-Python reference built on the ORGANIZER blake3.py (_g/_compress, rounds=2)
on 1,000 random blocks over the 133 base configurations and all three frames. Every one of the 61 observables, the
damage and info bits and the frame-D check residual must agree (0 mismatches). Also checks the fast path.
usage: python -B validate.py [n=1000] [seed=1]'''
import sys, random, collections
sys.dont_write_bytecode = True
from common import FRAMES, OBS_FIELDS, DAMAGE_BITS, M
from harness import Harness

def random_block(rnd, frame):
    n = len(FRAMES[frame]); m = [0] * n
    lo = 3 if frame == 'D' and rnd.random() < 0.85 else 0           # frame D: mostly the free words B, g
    hi = 10 if lo == 3 else n
    kind = rnd.choice(['bit', 'pair', 'word_k', 'multi', 'msb', 'dense', 'all', 'zero'] + ['multi'] * 3 + ['bit'] * 2)
    pick = lambda: rnd.randrange(lo, hi)
    if kind == 'bit': m[pick()] ^= 1 << rnd.randrange(32)
    elif kind == 'pair': b = rnd.randrange(31); m[pick()] ^= 3 << b
    elif kind == 'word_k':
        w = pick()
        for _ in range(rnd.randint(2, 8)): m[w] ^= 1 << rnd.randrange(32)
    elif kind == 'multi':
        for _ in range(rnd.randint(2, 12)): m[pick()] ^= 1 << rnd.randrange(32)
    elif kind == 'msb':
        for _ in range(rnd.randint(1, 4)): m[pick()] ^= 1 << 31
    elif kind == 'dense': m[pick()] ^= rnd.getrandbits(32) | 1
    elif kind == 'all':
        for w in range(lo, hi): m[w] = rnd.getrandbits(32)
    return kind, m

def main(n=1000, seed=1):
    H = Harness(); rnd = random.Random(seed)
    frames = ['D'] * 40 + ['O'] * 30 + ['R'] * 30
    cases, kinds = [], []
    for _ in range(n):
        fr = rnd.choice(frames); ci = rnd.randrange(len(H.cfgs)); kind, m = random_block(rnd, fr)
        cases.append((ci, fr, m)); kinds.append(kind)
    res = H.apply_batch(cases)
    bad = 0; badfast = 0; fields = collections.Counter(); stats = collections.Counter()
    FAST = sum(1 << DAMAGE_BITS.index(k) for k in ('Y4', 'Y9', 'Y14', 'w8', 'X3', 'X7', 'X11', 'X15', 'T1RANGE'))
    PINS = sum(1 << DAMAGE_BITS.index(k) for k in ('X3', 'X7', 'X11', 'X15'))
    for (ci, fr, m), kind, c in zip(cases, kinds, res):
        r = H.apply_ref(ci, fr, m)
        diff = [k for k in OBS_FIELDS if c['now'][k] != r['now'][k]]
        diff += [k for k in ('damage', 'info', 'chk') if c[k] != r[k]]
        if diff:
            bad += 1; fields.update(diff)
            if bad <= 5: print('MISMATCH', fr, ci, kind, diff[:8])
        f = c['fast']
        ok = f['damage'] == (c['damage'] & FAST) and f['T1'] == c['now']['T1']
        if not (c['damage'] & PINS): ok &= f['K1'] == [c['now']['k1_%d' % i] for i in range(4)]
        badfast += not ok
        stats['frame ' + fr] += 1; stats['kind ' + kind] += 1
        stats['zero damage'] += c['zero_damage']
        stats['zero damage, real point moved'] += c['zero_damage'] and 'SAME_POINT' not in c['info_names']
        stats['zero damage, K1 moved'] += c['zero_damage'] and c['hwK1'] > 0
        if fr == 'D' and not any(m[i] for i in (0, 1, 2, 10)):
            stats['D free-word blocks'] += 1
            only_t1 = (c['damage'] & ~(1 << DAMAGE_BITS.index('T1RANGE'))) == 0
            stats['D: (damage beyond T1RANGE == 0) <=> chk == 0 holds'] += only_t1 == (c['chk'] == 0)
            stats['D: (Y9 damaged) <=> chk != 0 holds'] += ('Y9' in c['damage_names']) == (c['chk'] != 0)
            stats['D: damage subset of {Y9,K3,T1RANGE} holds'] += set(c['damage_names']) <= {'Y9', 'K3', 'T1RANGE'}
    ctrl = 0                                                       # negative control: pair C case i with reference i+1
    for i in range(min(n, 200) - 1):
        ci, fr, m = cases[i + 1]
        ctrl += res[i]['now'] != H.apply_ref(ci, fr, m)['now']
    print('negative control (shifted pairing, 199 pairs): mismatches', ctrl)
    print('cases', n, 'mismatches (C vs organizer-reference, all 61 observables + damage/info/chk):', bad, dict(fields))
    print('fast-path disagreements:', badfast)
    for k in sorted(stats): print('  %-55s %d' % (k, stats[k]))
    return bad + badfast

if __name__ == '__main__':
    a = sys.argv[1:]
    sys.exit(1 if main(int(a[0]) if a else 1000, int(a[1]) if len(a) > 1 else 1) else 0)
