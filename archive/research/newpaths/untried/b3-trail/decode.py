#!/usr/bin/env python3
"""decode.py - read a SAT model (kissat 'v' lines) for a b3trail.py CNF and print the
characteristic; recompute every active addition with an independent Lipmaa-Moriai routine
(validity + weight) so the solver's answer is checked, not trusted.

usage: decode.py PREFIX SOLVER_OUTPUT [--json OUT]
"""
import json
import sys

MASK = 0xFFFFFFFF


def lm(a, b, c, n=32):
    """Lipmaa-Moriai xdp+ weight of (a,b)->c; None if impossible."""
    mask = (1 << n) - 1

    def eq(x, y, z):
        return (~x ^ y) & (~x ^ z) & mask
    if eq((a << 1) & mask, (b << 1) & mask, (c << 1) & mask) & (a ^ b ^ c ^ ((b << 1) & mask)):
        return None
    return bin(~eq(a, b, c) & (mask >> 1)).count('1')


def load_model(path):
    val = {}
    sat = None
    with open(path) as fh:
        for line in fh:
            if line.startswith('s '):
                sat = line.strip()
            if line.startswith('v '):
                for t in line.split()[1:]:
                    x = int(t)
                    if x != 0:
                        val[abs(x)] = x > 0
    return sat, val


def lit_val(l, val):
    if l == 'T':
        return True
    if l == 'F':
        return False
    v = val.get(abs(l), False)
    return v if l > 0 else not v


def word_val(w, val):
    x = 0
    for i, l in enumerate(w):
        if lit_val(l, val):
            x |= 1 << i
    return x


def main():
    prefix, solout = sys.argv[1], sys.argv[2]
    meta = json.load(open(prefix + '.map.json'))
    sat, val = load_model(solout)
    print('solver:', sat)
    if not sat or 'UNSAT' in sat or not val:
        return
    total = 0
    bad = 0
    per_g = {}
    for ad in meta['adds']:
        g = ad['guard']
        if g is not None and not lit_val(g, val):
            continue
        a, b, z = (word_val(ad[k], val) for k in ('a', 'b', 'z'))
        w = lm(a, b, z)
        if w is None:
            bad += 1
            print('INVALID LM transition', ad['tag'], hex(a), hex(b), hex(z))
            continue
        total += w
        key = ad['tag'].split('.')[0]
        per_g[key] = per_g.get(key, 0) + w
    W = {k: word_val(v, val) for k, v in meta['words'].items()}
    if 'ctr.lo' in W:
        print(f'counter difference chosen: lo={W["ctr.lo"]:08x} hi={W["ctr.hi"]:08x}')
    if 'm0' in W:
        print('message differences:')
        for i in range(16):
            print(f'  dm{i:<2} = {W[f"m{i}"]:08x}')
    print('per G call (inputs a b c d x y -> outputs a2 b2 c2 d2), LM weight:')
    for rec in meta['gcalls']:
        t = rec['tag']
        ins = ' '.join(f'{W[t + "." + k]:08x}' for k in 'abcdxy')
        outs = ' '.join(f'{W[t + "." + k]:08x}' for k in ('a2', 'b2', 'c2', 'd2'))
        print(f'  {t}: in {ins} -> out {outs}   w={per_g.get(t, 0)}')
    if 'out.v0' in W:
        outv = [W[f'out.v{i}'] for i in range(16)]
        coll = all(outv[i] == outv[i + 8] for i in range(8))
        print('final state diff:', ' '.join(f'{x:08x}' for x in outv))
        print('collision condition (dv[i]==dv[i+8]):', coll)
    else:
        coll = None
    print('invalid transitions:', bad)
    print('TOTAL LM WEIGHT (recomputed):', total)
    cnt = meta.get('args', {}).get('count', '')
    if cnt:
        keep = set(cnt.split(','))
        print('COUNTED WEIGHT (' + cnt + '):', sum(v for k, v in per_g.items() if k in keep))
    else:
        print('COUNTED WEIGHT (all):', total)
    if len(sys.argv) > 4 and sys.argv[3] == '--json':
        json.dump({'total': total, 'bad': bad, 'coll': coll, 'per_g': per_g,
                   'dm': [W[f'm{i}'] for i in range(16)] if 'm0' in W else [], 'words': W},
                  open(sys.argv[4], 'w'))


if __name__ == '__main__':
    main()
