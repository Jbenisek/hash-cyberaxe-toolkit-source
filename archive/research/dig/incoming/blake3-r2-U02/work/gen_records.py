import json, os
W = '..'
cells = json.load(open('cells64.json')); nec = json.load(open('necessity.json'))
cc = [json.loads(l) for l in open('cc_out.jsonl')]
ax = {l.split()[0]: l.strip() for l in open('axis_out.txt')}
real = [c for c in cells['cells'] if c['realizable']]
assert len(real) == 8 and all(c['replay_all_ok'] and c['n_pins'] == 64 for c in real)
live = [x['Y3'] for x in cc[:8] if x['S_over_2_83'][0] == 67633152]
dead = [x['Y3'] for x in cc[:8] if x['S_over_2_83'][0] == 0]
assert sorted(live) == ['8120c181', '8123c181', '8124c181', '8127c181'] and sorted(dead) == ['8121c181', '8122c181', '8125c181', '8126c181']
yvar = cc[8]; assert yvar['Y11'] == '7af77f3c' and yvar['S_over_2_83'][0] == 67633152
P = 'research/dig/incoming/blake3-r2-U02/work/'
EV = '; '.join([P + 'factp.py', P + 'cells64.py', P + 'cells64.json', P + 'cc_cell.py', P + 'cc_out.jsonl', 'research/pkg17/count/count_class.py (reused unchanged)'])
EV2 = '; '.join([P + 'factp.py', P + 'necessity.py', P + 'necessity.json', P + 'axis.c', P + 'axis_out.txt'])
Q = {1: ('a1,d1', 'q1'), 2: ('c1,b1', 'q2'), 3: ('a2,d2', 'q3'), 4: ('c2,b2', 'q4')}
q4_part = {
 1: "q1 (a1,d1): the carry run X=a1^(a1+8) must be fffffff8 (R=ror(X,16)=fff8ffff): the only one of 29 runs with both cube(D3,R) and cube(D11,R) non-empty (16 and 16 words incl. bit-31 orbits); passes in 64/64 cells (cell independent).",
 2: "q2 (c1,b1): c1=Y11-ror(d1^Y3,8) must satisfy c1^(c1+D11)=rol(Y11^(Y11+D11),12): passes in 8/64 cells (Y11=7af77f38 only); the 7 other settings of Y11 bits 19,15,2 fail here in all 8 Y3 patterns (56/64 fail).",
 3: "q3 (a2,d2): d2 equal needs Y3^(Y3+D3)=R, i.e. Y3 in cube(D3,R); all 8 Y3 bit-18..16 patterns are in the cube: 64/64 pass.",
 4: "q4 (c2,b2): b2 equal needs v=Y11^(Y11+D11) admissible (b1 in cube(D3-8,v)) and W13=Y3-a1-b1 below 2^24: v is admissible in 64/64 cells; with q2 true, all 8 cells also meet the W13 condition (64 pins each); in the 56 q2-failing cells the W13 part is moot (no c1).",
}
def rec(**k):
    base = dict(hash='blake3-r2', row_i=None, row_j=None, labels=['P'], source='our workflow: scan-once', own_test=True,
                date='2026-10-12', lever=False, gain_bits=None)
    base.update(k); return base
out = []
for qi in range(1, 5):
    terms, qn = Q[qi]
    obj = 'C3.%s (%s) pinned constants (Fact P)' % (qn, terms)
    n4 = ("64 (Y3,Y11) cells (Y3 bits 18..16 x Y11 bits 19,15,2 around 8127c181/7af77f38): 8 realizable by Fact P, 56 not; whole profile has 16 Y3 x 2 Y11 (bit-31 orbits of the same 8 cells); "
          "512 constructed pins replayed through C3: all equal b2,d2 with the profile D3,D11. %s "
          "Ledger (beta* 18b0e098, S 6 outcomes, per 2^83): 67,633,152 at Y3 %s and 0 at %s (y16!=y17 gate); control 8127c181 gives 71,698,432 whole / 67,633,152 S; no cell beats the record."
          % (q4_part[qi], ','.join(sorted(live)), ','.join(sorted(dead))))
    nt4 = ("Universe cell blake3-r2|C3.%s|step|Q4. Own enumeration (factp.py: carry-cube solver, validated on the record pins -> Y3 8127c181/7edf3e7e, Y11 7af77f38/850000c3, d2 bbfbdffe, b2 76f7aefd; "
           "valid-R count for D11 = 133,742 agrees with the realize/ report's 66,871 betas x2) plus the existing exact beta* counter count_class.py (reproduces 71,698,432 / 67,633,152 on the control; its width-6 brute-force self-test is the validation). "
           "Scope: record profile (delta=-8, D3=fdb77cfd, D11=0a08818b, eta 830303cf, length XOR 8 so W13 top byte 0); other profiles not enumerated here. Ledger = rate term only (2^11 x part_S); filter (1)/E-count/solver terms for other Y3 were not recomputed (not needed: no cell raises the rate). "
           "Y11 variant check: Y11=7af77f3c (bit 2 flipped, no pin exists) gives the same beta* part 71,698,432 / 67,633,152, so those Y11 bits are free in rate but unrealizable. Other betas: the old +177.69 (1.1e-6 relative) at 8123/8124 lies outside beta* and is not used by the record. "
           "Quarter attribution in a 4-quarter call is by which equality fails; the grid verdict is the same for all four rows." % qn)
    out.append(('blake3-r2_C3.%s_step_Q4' % qn, rec(object=obj, question='Q4 alternative constant pairs (Y3,Y11): recompute Fact P outputs for the 64 (Y3,Y11) cells on the current ledger',
        status='COMPUTED', number=n4, evidence=EV, notes=nt4)))
a = {k: v.split(' first')[0] for k, v in ax.items()}
q2 = {
 1: "q1 (a1,d1) is where the difference is born: d1^d1' = ror(a1^(a1+8),16) is nonzero for every a1, so equal d2/b2 can never come from 'no difference' and must be cancelled later. Pin freedom per coordinate (others at record, all 2^32 values): a1 -> {%s}; d1 -> {%s}. Single-bit flips of a1: 1/32 keep d2 equal, 0/32 keep b2, 0 keep digest words 0,2,5,7; of d1: 4/32, 0/32, 0; random replacement 0/2000 keep both. Only 1 of 29 carry runs fits the profile." % (a['a1'], a['d1']),
 2: "q2 (c1,b1) carries the b-side cancellation b1^b1' = ror(c1^c1',12) = c2^c2'. Per coordinate: c1 -> {%s}; b1 -> {%s} (b1 mostly leaves d2 alone: 67,108,856 values keep d2 only, so b1 is the b2 knob). Single-bit flips: c1 3/32 keep d2, 1/32 both (bit 31 symmetry); b1 25/32 keep d2, 2/32 keep b2, 1/32 both (bit 31); random replacement 0/2000 keep both." % (a['c1'], a['b1']),
 3: "q3 (a2,d2): d2 equal iff a2^a2' = d1^d1' = R; Y15=d2 feeds E0. W13 axis (moves a2 only): {%s}; single-bit flips of W13: 4/32 keep d2, 4/32 keep b2, 0/32 both, 0 keep digest words 0,2,5,7. Digest test: with the pin, words 0,2,5,7 agree for A and B in 64/64 random trials of the other Y words and messages, words 1,3,4,6 agree in 0/64; a2 (Y3) and c2 (Y11) differ by DY3,DY11 by design and feed only E3/E1 (the residual)." % a['w13'],
 4: "q4 (c2,b2): b2 equal iff b1^b1' = c2^c2' = v; Y7=b2 feeds E2 and Y15=d2 feeds E0; E0 and E2 outputs make up all four of digest words 0,2,5,7 (o0=Z0^Z8, o2=Z2^Z10, o5=Z5^Z13, o7=Z7^Z15), so one unequal b or d output spoils them (over 160 single-bit flips of the five coordinates only the 2 bit-31 symmetry flips of c1 and b1 keep Fact P, and only those keep words 0,2,5,7). Without the pin the half-collision costs extra conditions on E0/E2 (doors 22,24).",
}
for qi in range(1, 5):
    terms, qn = Q[qi]
    obj = 'C3.%s (%s) pinned constants (Fact P)' % (qn, terms)
    n2 = "NECESSARY. " + q2[qi]
    nt2 = ("Universe cell blake3-r2|C3.%s|step|Q2. Own tests: necessity.py (C3 and the 2-round E half re-implemented, validated: record pin -> equal d2/b2, words 0,2,5,7 equal in 64/64 trials) and axis.c (exhaustive 2^32 scan per pin coordinate, others at the record value; "
           "(a1,d1,c1,b1) is a bijection with (X3,X7,X11,X15) given w4). 'Necessary' = equal b/d outputs are not a property of random constants (random replacement 0/2000) and the pin is exactly the cube above; a single-coordinate scan is a local test around the record, not the global solution count (global: 64 pins per realizable cell, 8 cells, record profile; see the Q4 rows). "
           "Quarter attribution is by which equality the quarter carries; all four rows come from the same tests." % qn)
    out.append(('blake3-r2_C3.%s_step_Q2' % qn, rec(object=obj, question='Q2 necessity of the C3 pin (w4 advice; a,c differ by DY3,DY11)',
        status='COMPUTED', number=n2, evidence=EV2, notes=nt2)))
for name, r in out:
    json.dump(r, open('%s/%s.json' % (W, name), 'w'), indent=1)
print(len(out), 'records written')
