"""e3real.py (counter_next/knobs; research only): the E3 search of e3dfs.py on REAL outer steps of the counter
arrangement, checked through real compressions (own b3own.py trace and the organizer's verifier _compress).

Uses copies of counter/structure/arrange_check.py (outer(), inner()) and b3own.py.
For each real outer step o (seven random words + a sub-class member y):
  U = (y, Y9, w8) is read from the outer step.  An inner value h1 is mapped back to the trial by
     Y14 = ROL(h1,16) ^ (Y3 + y); Y10 = Y14 + C2.c1; Y6 = ROR(Y10 ^ C2.b1, 7); a1 = Y6 + Y1 + w12;
     E1.d1 = ROR(a1 ^ Y12, 16)
  and the trial is built by arrange_check.inner (w0, w1, t solved).
(a) planted: a random E1.d1 (any 32-bit value, not only the cube) -> real compressions of A (55 bytes) and B
    (63 bytes) at counter t, flags 3 -> the four E3 differences (dg1, de2, dg2, df2) as the target; the search
    must return the trial's own h1, and every h1 it returns must, mapped back, give real compressions with the
    same four E3 differences and CV words 0, 2, 5, 7 equal.
(b) partial: the dg1 and de2 conditions of the NT heaviest listed outcomes; every solution is mapped back and
    checked on the real compressions.
usage: python -B e3real.py NOUTER SEED NT
"""
import sys, struct, random
sys.dont_write_bytecode = True
import arrange_check as A
import b3own as O
import e3dfs as D

M = 0xFFFFFFFF
rol, ror = O.rol, O.ror


def d1_of_h(o, h):
    e1 = (A.Y3A + o['y']) & M
    Y14 = rol(h, 16) ^ e1
    Y10 = (Y14 + o['C2c1']) & M
    Y6 = ror(Y10 ^ o['C2b1'], 7)
    a1 = (Y6 + o['Y1'] + o['w12']) & M
    return ror(a1 ^ o['Y12'], 16)


def real_trial(o, d1):
    ii, words = A.inner(o, d1)
    t = ii['t']
    wb = list(words); wb[4] = A.W4B; wb[5] = (words[5] + A.DELTA) & M
    trA, trB = {}, {}
    outA, _ = O.compress_full(O.IV, words, t, 55, 3, trace=trA)
    outB, _ = O.compress_full(O.IV, wb, t, 63, 3, trace=trB)
    # organizer verifier on the same descriptors
    oa = A.V._chunk_output(struct.pack('<16I', *words)[:55], t, 2)
    ob = A.V._chunk_output(struct.pack('<16I', *wb)[:63], t, 2)
    cvA = A.V._compress(*oa, 2)[:8]; cvB = A.V._compress(*ob, 2)[:8]
    org_ok = tuple(cvA) == tuple(outA[:8]) and tuple(cvB) == tuple(outB[:8])
    half = all(cvA[i] == cvB[i] for i in (0, 2, 5, 7))
    ea, eb = trA['E3'], trB['E3']
    diffs = (ea['c1'] ^ eb['c1'], ea['a2'] ^ eb['a2'], ea['c2'] ^ eb['c2'], ea['b2'] ^ eb['b2'])
    return dict(t=t, h1=ea['d1'], diffs=diffs, half=half, org_ok=org_ok,
                U=(ea['B'], ea['C'], ea['y']), d1=trA['E1']['d1'])


def main():
    nouter, seed, nt = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    rng = random.Random(seed)
    rows, tot = D.load_targets(nt)
    targets = [D.outcome_target(r[2], r[3]) for r in rows]
    c = dict(outer=0, planted_found=0, planted_extra=0, map_ok=0, map_n=0, U_ok=0, half=0, org=0,
             part_sol=0, part_ok=0, t_zero=0)
    for oi in range(nouter):
        o = A.outer(*[rng.getrandbits(32) for _ in range(7)], A.sub_member(rng))
        y, Y9, w8 = o['y'], o['Y9'], o['w8']
        c['outer'] += 1
        # (a) planted
        d1 = rng.getrandbits(32)
        tr = real_trial(o, d1)
        c['U_ok'] += tr['U'] == (y, Y9, w8)          # E3's b, c, y inputs = the outer step's Y4, Y9, w8
        c['half'] += tr['half']; c['org'] += tr['org_ok']
        sols, _ = D.search(y, Y9, w8, [tr['diffs']])
        hs = [h for h, _ in sols]
        c['planted_found'] += tr['h1'] in hs
        c['planted_extra'] += len(hs) - (tr['h1'] in hs)
        for h in hs:
            t2 = real_trial(o, d1_of_h(o, h))
            c['map_n'] += 1
            c['map_ok'] += t2['h1'] == h and t2['diffs'] == tr['diffs'] and t2['half'] and t2['org_ok']
            c['t_zero'] += t2['t'] == 0
        # (b) partial system, listed targets
        psols, _ = D.search(y, Y9, w8, targets, partial=True)
        for h, ti in psols:
            t2 = real_trial(o, d1_of_h(o, h))
            c['part_sol'] += 1
            c['part_ok'] += (t2['h1'] == h and t2['diffs'][:2] == targets[ti][:2] and t2['half'] and t2['org_ok'])
    print(f'e3real: {c["outer"]} real outer steps (seed {seed}), {len(targets)} targets for the partial system')
    print(f'  E3 inputs (Y4, Y9, w8) of the real compression = outer-step values: {c["U_ok"]}/{c["outer"]}')
    print(f'  planted trial: CV words 0,2,5,7 equal {c["half"]}/{c["outer"]}; own compress = organizer {c["org"]}/{c["outer"]}')
    print(f'  planted h1 found by the search: {c["planted_found"]}/{c["outer"]}; other solutions {c["planted_extra"]}')
    print(f'  every returned h1 mapped back to a trial (E1.d1 -> w0, t), real compressions: same h1, same four E3 '
          f'differences, half-collision and organizer agreement: {c["map_ok"]}/{c["map_n"]} (t = 0: {c["t_zero"]})')
    print(f'  partial system (dg1, de2 of the listed targets): {c["part_sol"]} solutions; mapped back and confirmed '
          f'on real compressions: {c["part_ok"]}/{c["part_sol"]}')


if __name__ == '__main__':
    main()
