#!/usr/bin/env python3
"""count_ctr.py [WORDS] [SEED]   (counter/value; research only)

Machine count of the counter arrangement's batch, on the SAME counting machine as the filed program
(research/pkg10/pkg/blake3-r2/experiments/halfsearch.py: Machine, seven 36-bit lanes per 256-bit word, a rotation
= 5 operations, every operation 1 unit, every load 1 unit, at most 16 registers).  halfsearch.py is imported read
only (no bytecode written).

Counter arrangement (pin H8, lengths 55/63, last-chunk compression with counter T0): Y4 and seven other basis words
fixed per outer step, the inner word E1.d1 runs through the heavy beta cube (c1 & 0e09818b) == 02008000.
Because Y11 is a pinned constant, the packed words RT[j] = ROL(E1.d1, 16) and D[j] = E1.d1 of the cube's members
(seven per word) are the same for the whole run: a table built once (2^21 members, memory free).
  stage A:  a1 = RT[j] ^ Y12;  Y6 = a1 - (Y1 + w12);  Y10 = ROL(Y6,7) ^ C2.b1;  Y14 = Y10 - C2.c1;  z = ROL(Y14, 8);
            rule A on z with the filed plan (A_STEPS) and a right-side word that is a constant of the outer step
            (Y4 is fixed per outer step), in place of the filed list word V[j].
  stage 2:  E1 for both messages (beta is the constant 18b0e098), eps, the E1 test word of Lemma E (filed form).
Validation: every lane's rule-A flag and E1-test word against a scalar reference that solves the whole order
(verify_ctr, real arithmetic) for that lane's E1.d1.
"""

# Publication path adapter: resolve data paths from the extracted source tree.
def _hca_public_path_text(value):
    if "__HCA_WORKSPACE__/" not in value:
        return value
    import os as _hca_os
    from pathlib import Path as _hca_Path
    root = _hca_os.environ.get("HASHCYBERAXE_WORKSPACE")
    if root is None:
        here = _hca_Path(__file__).resolve().parent
        root = next((str(p) for p in (here, *here.parents) if (p / "research").is_dir()), None)
    if root is None:
        raise FileNotFoundError("Extract the research source tree, or set HASHCYBERAXE_WORKSPACE to its archive directory.")
    return value.replace("__HCA_WORKSPACE__/", str(_hca_Path(root).resolve()).replace("\\", "/") + "/")

import sys, random
sys.dont_write_bytecode = True
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/pkg10/pkg/blake3-r2/experiments'))
import halfsearch as H
import verify_ctr as V

MASK = 0xFFFFFFFF
CM, CV, BETA = 0x0E09818B, 0x02008000, 0x18B0E098
ror, rol = V.ror, V.rol
txt = open('cone4_E1b1_B10.txt').read().splitlines()
import re
BASIS = re.search(r'basis = ([^|]*)', txt[0]).group(1).split()
LINES = [(l.split('<-')[0].replace('*', ' ').strip(), l.split('<-')[1].split()) for l in txt[1:]
         if '<-' in l and 'cone of' not in l]


def solve_all(basis_vals):
    class Stub:
        def __init__(s): s.i = 0
        def randrange(s, n):
            v = vals[s.i]; s.i += 1
            return v
    vals = [basis_vals[b] for b in BASIS]
    orig = V.class_member; V.class_member = lambda k: basis_vals['Y4']
    try:
        return V.solve_order(LINES, BASIS, Stub())
    finally:
        V.class_member = orig


def rule_a(h1):
    return all(bin(h1 & m).count('1') & 1 == v for m, v in H.RULE_A)


def ctr_memory(outer, d1s):
    """memory of the batch: filed FIXED constants plus the outer step's words; RT/D words for this batch."""
    c = {name: H.rep(value) for name, value in H.FIXED.items()}
    c['bit 32'], c['not bit 32'] = H.ONES << 32, H.ONES * (H.LANE ^ 1 << 32)
    c['end of list'] = (1 << 21) // 7 + 1
    c['Y12'] = H.rep(outer['Y12'])
    c['-Y1-w12'] = H.rep(-(outer['Y1'] + outer['w12']))
    c['C2.b1'] = H.rep(outer['C2.b1'])
    c['-C2.c1'] = H.rep(-outer['C2.c1'])
    c['w5'] = H.rep(outer['w5'])
    c['w5+delta'] = H.rep(outer['w5'] + H.DELTA5)
    c['beta'] = H.rep(BETA)
    c['V'] = H.pack([H.rule_word(outer['Y4'])] * H.LANES)     # right sides: constant over the outer step
    c['RT'] = H.pack(rol(d, 16) for d in d1s)
    c['D'] = H.pack(d1s)
    return c


def ctr_batch(m, c, resident, j):
    k, put, low, neg = H.tools(m, c)
    m.resident(resident)
    m.at('loop')
    m.compare_and_branch(m.advance(j), k('end of list'))
    m.at('cube word to Y14')
    a1 = m.xor(m.load(c['RT']), k('Y12'))
    y6 = m.add(a1, k('-Y1-w12'))
    y10 = m.xor(m.prol(y6, 7), k('C2.b1'))
    y14 = m.add(y10, k('-C2.c1'))
    m.at('z')
    z = m.prol(y14, 8)
    m.at('rule A')
    y, s, n = z, None, 0
    for step in H.A_STEPS:
        if isinstance(step, tuple):
            n, d = n + 1, step[0]
            s = m.band(m.shl(y, d) if d > 0 else m.shr(y, -d), k('A mask %d' % n))
        else:
            s = m.shl(s, step) if step > 0 else m.shr(s, -step)
        y = m.xor(y, s)
    s = m.add(m.band(m.xor(y, k('V')), k('A all')), k('A carry'))
    taken_a = m.compare_and_branch(m.bor(s, k('not bit 32')), k('not bit 32'))
    flags_a = [1 - (s.z >> (H.LANE_BITS * i + 32) & 1) for i in range(H.LANES)]
    m.at('entry count')
    m.compare_and_branch(m.advance(0), k('end of list'))
    # ---- stage 2 (charged per entered word) ----
    m.at('E1, A and B')
    a1 = m.xor(m.load(c['RT']), k('Y12'))
    y6 = m.add(a1, k('-Y1-w12'))
    d1 = m.load(c['D'])
    c1 = m.add(d1, k('Y11'))
    b1 = m.pror(m.xor(c1, y6), 12)
    a2 = m.add(m.add(k('w5'), a1), b1)
    c2 = m.add(c1, m.pror(m.xor(a2, d1), 8))
    c1b = m.add(d1, k("Y11'"))
    b1b = m.pror(m.xor(c1b, y6), 12)
    a2b = m.add(m.add(k('w5+delta'), a1), b1b)
    c2b = m.add(c1b, m.pror(m.xor(a2b, d1), 8))
    m.at('E1 test')
    eps = m.xor(c2, c2b)
    x = m.xor(k('beta'), eps)
    rot = m.bor(m.band(m.shr(x, 31), k('A31')), m.shl(x, 1))
    word = m.band(m.xor(m.xor(rot, eps), k('eta')), k('M'))
    flags = m.band(m.add(word, k('M')), k('bit 32'))
    taken = m.compare_and_branch(flags, k('bit 32'))
    m.finish(resident)
    return flags_a, taken_a, [(word.z >> (H.LANE_BITS * i)) & MASK for i in range(H.LANES)]


STAGE_A = ('loop', 'cube word to Y14', 'z', 'rule A')


def main():
    nwords = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    rng = random.Random(int(sys.argv[2]) if len(sys.argv) > 2 else 5)
    # resident registers: the words of stage A used most, chosen so that the peak stays within 16
    resident = ['Y12', '-Y1-w12', 'A25', 'B25', 'C2.b1', '-C2.c1', 'A24', 'B24', 'A mask 1', 'A mask 2', 'A all', 'A carry', 'V', 'not bit 32'][:int(sys.argv[3]) if len(sys.argv) > 3 else 11]
    right = tot = 0
    counts = None
    for t in range(nwords):
        outer = {b: rng.getrandbits(32) for b in BASIS if b != 'E1.d1'}
        e1 = (H.CLASS_VALUE | (rng.getrandbits(32) & ~H.CLASS_MASK)) & MASK      # sub-class member
        outer['Y4'] = (e1 - H.Y3) & MASK
        d1s, refs = [], []
        for i in range(H.LANES):
            c1 = (rng.getrandbits(32) & ~CM | CV) & MASK
            d1 = (c1 - V.Y11A) & MASK
            val = solve_all(dict(outer, **{'E1.d1': d1}))
            d1s.append(d1); refs.append(val)
        o = refs[0]
        mem = ctr_memory(o, d1s)
        mem.update({'Y4': H.rep(outer['Y4'])})
        m = H.Machine()
        flags_a, taken_a, words = ctr_batch(m, mem, resident, t)
        for i, val in enumerate(refs):
            h1 = val['E3.h1']
            # scalar E1 for both messages
            a1, y6, d1 = val['E1.a1'], val['Y6'], d1s[i]
            c1 = (V.Y11A + d1) & MASK; b1 = ror(y6 ^ c1, 12); a2 = (a1 + b1 + val['w5']) & MASK
            c2 = (c1 + ror(d1 ^ a2, 8)) & MASK
            c1b = (H.Y11B + d1) & MASK; b1b = ror(y6 ^ c1b, 12); a2b = (a1 + b1b + val['w5'] + H.DELTA5) & MASK
            c2b = (c1b + ror(d1 ^ a2b, 8)) & MASK
            eps = c2 ^ c2b
            want_word = (rol(BETA ^ eps, 1) ^ eps ^ H.ETA) & MASK
            ok = (flags_a[i] == 1 - int(rule_a(h1))) and words[i] == want_word and (b1 ^ b1b) == BETA
            right += ok; tot += 1
        if counts is None:
            counts = {p: (m.ops[p], m.loads[p], m.stores[p]) for p in m.ops}
            regs = m.registers()
    sa = [sum(counts[p][i] for p in STAGE_A) for i in range(3)]
    s2 = [sum(counts[p][i] for p in counts if p not in STAGE_A) for i in range(3)]
    print(f'lanes right {right} of {tot} (rule-A flag, E1 test word, beta) over {nwords} packed words')
    for p, (o, l, s) in counts.items():
        print(f'  part {p:20s} ops {o:3d} loads {l:2d} stores {s}')
    print(f'stage A: {sa[0]} operations + {sa[1]} loads + {sa[2]} stores = {sum(sa)} units per word of {H.LANES} trials')
    print(f'stage 2: {s2[0]} operations + {s2[1]} loads + {s2[2]} stores = {sum(s2)} units per entered word')
    print(f'register peak (machine.registers()): {regs} (limit {H.REGISTERS}); resident {len(resident)}: {resident}')
    print(f'filed program (halfsearch.py TABLES, KEPT=9): stage A 37 ops + 10 loads = 47; stage 2 = 135 per entered word')


if __name__ == '__main__':
    main()
