import sys, json, os, re
sys.path.insert(0, '.')
import b3core as B

W = 'research/dig/incoming3/_b3r3_work/'
info = json.load(open('stepinfo.json'))
mut = json.load(open('q2_mutate.json'))
hc = json.load(open('hc_507.json'))
ver = json.load(open('verify_witness_507.json'))


def parse(fn):
    d = {}
    for l in open(fn):
        m = re.match(r'DONE r=(\d+) .*family: E=(\d+) K=(\d+) unary=(\d+) nodes=(\d+) found=(\d+)', l)
        if m:
            d[int(m.group(1))] = tuple(int(x) for x in m.groups())
    return d


A = parse('rot4_out.txt')
Bf = parse('rot4b_out.txt')
prog, out = B.build(3)
RQ = {1: 16, 2: 12, 3: 8, 4: 7}
PAIR = {1: '(a1,d1)', 2: '(c1,b1)', 3: '(a2,d2)', 4: '(c2,b2)'}
UNITS = {'U37': [('R2C2', 1), ('R2C2', 2)], 'U38': [('R2C2', 3), ('R2C2', 4)],
         'U39': [('R2C3', 1), ('R2C3', 2)], 'U40': [('R2C3', 3), ('R2C3', 4)],
         'U41': [('R2D0', 1), ('R2D0', 2)], 'U42': [('R2D0', 3), ('R2D0', 4)],
         'U43': [('R2D1', 1), ('R2D1', 2)], 'U44': [('R2D1', 3), ('R2D1', 4)],
         'U45': [('R2D2', 1), ('R2D2', 2)]}


def call_j(c):
    return int(c[-1]) if c[2] == 'C' else 4 + int(c[-1])


ENV = ("Held fixed: the shipped 595-op circuit (research/blake3_r3/candidate_blake3/experiments/rho.py: 7 lanes x 36 bits, ops add/and/or/xor/shl/shr, "
       "constants folded) re-derived by our own tracer b3core.py (595 ops; equals the scalar 3-round digest on 300+ batches; scalar core equals "
       "verifier/blake3.py on 3 and 7 rounds and the official 7-round fixture).")


def kinds_of(j, q):
    from collections import Counter
    return dict(Counter(o['kind'] for o in prog if o['tag'] == (2, j, q)))


def build(call, q, Q):
    j = call_j(call)
    I = info[call]
    qi = I['q%d' % q]
    r = RQ[q]
    n = qi['ops']
    kd = kinds_of(j, q)
    kdtxt = ', '.join('%s %d' % (k, v) for k, v in sorted(kd.items()))
    ops = [k for k, o in enumerate(prog) if o['tag'] == (2, j, q)]
    isA = q in (1, 3)
    zero = None
    if isA:
        ain = qi['a_in']
        zero = qi['msg_const_zero']
        wd = qi['msg_word']
        sumb = ain[0] + 1 + (0 if zero else 1)
        inp = "a bound %.3f units (1 unit = 2^32) + b 1 + %s -> out %.3f (lane limit 16, headroom %.3f)" % (
            ain[0], ("message word m%d (constant 0, no add emitted)" % wd) if zero else ("message word m%d (variable, one more add)" % wd), sumb, 16 - sumb)
    else:
        cin = qi['c_in']
        sumb = cin[0] + 1
        inp = "c bound %.3f units + d 1 -> out %.3f (lane limit 16, headroom %.3f)" % (cin[0], sumb, 16 - sumb)
    outb = sumb
    has_mask = (call == 'R2D1' and q == 3)
    if isA:
        trees = 1 if zero else 3
    else:
        trees = 1
    if has_mask:
        trees = 1
        inp = "a bound 15.529 units + b 1 + message word m0 (constant 0, no add) -> 16.529 > 16 without the mask; with the mask out 2.0"
        outb = 16.529
    status = 'COMPUTED'
    labels = ['N']
    obj = '%s.q%d %s' % (call, q, PAIR[q])
    ev = W + 'b3core.py; ' + W + 'validate_core.py; ' + W + 'q1_counts.py; ' + W + 'stepinfo.json'
    held = ENV
    reopen = None
    notes = ''
    if Q == 'Q1':
        quest = 'Q1 value/count as used: operations, bounds and message word of this quarter-step in the shipped 3-round circuit'
        num = '%d ops (%s); rotation ror%d is 5 of them (shr, and, shl, and, or); %s; step cost %d/638 = %.5f compression; round 2 %s call %s, circuit ops %d..%d' % (
            n, kdtxt, r, inp, n, n / 638.0, 'column' if call[2] == 'C' else 'diagonal', call, ops[0], ops[-1])
        if has_mask:
            num += '; one of the %d ops is the internal overflow mask (op 507)' % n
        notes = 'Counted by our own tracer per quarter-step tag; totals checked: 595 ops = add 100, xor 88, shr 80, shl 80, and 167, or 80.'
        reopen = 'a recount of this step differs on another lane layout or on the organizer-run harness'
        ev = W + 'b3core.py; ' + W + 'validate_core.py; ' + W + 'q1_counts.py; ' + W + 'q1_counts.json; ' + W + 'stepinfo.py; ' + W + 'stepinfo.json'
    elif Q == 'Q2':
        quest = 'Q2 necessity: delete or bypass each op of this quarter-step (pass operand A, pass operand B, or zero) and recount whether the digest is still right'
        if has_mask:
            num = ('%d of %d ops are individually necessary on 350 random and adversarial batches (every deletion variant gives a wrong digest on the first batch). '
                   'The exception under that test is the internal mask (op 507): removing it passes all 350 batches (random inputs never reach the lane limit). '
                   'A hill climb then found message words %s whose pre-mask sum a+b is %.3f units >= 16; with the mask removed the packed circuit gives a wrong digest '
                   'in the neighbouring lane for that witness placed in lane 1, 3 and 5 (wrong lanes 2, 4, 6), and the shipped circuit is right in all three. '
                   'So all %d ops are necessary; the mask is necessary by an explicit witness.') % (n - 1, n, hc['witness'], hc['best_sum_units'], n)
            status = 'BEDROCK'
            labels = ['C']
            ev = W + 'q2_mutate.py; ' + W + 'q2_mutate.json; ' + W + 'hc.py; ' + W + 'hc_507.json; ' + W + 'verify_witness.py; ' + W + 'verify_witness_507.json; ' + W + 'smt_mask.py; ' + W + 'smt_mask_507.json'
            notes = ('z3 on the same question (some add >= 2^36 with the mask removed) returned unknown after 122 s; the witness came from the numpy hill climb '
                     '(3594 generations, population 32768, 150 s) and is checked on the real packed circuit.')
            reopen = 'none for this mask (the witness is a proof); only a different circuit with a tighter lane-bound proof could remove it'
            held = ENV + ' Single deletion of one op at a time; three replacement variants; 350 batches (300 random, 50 adversarial: all-ones, alternating, 0x7fffffff, 0x80000000 words).'
        else:
            num = ('%d of %d ops are individually necessary: for each op, all deletion variants (pass A, pass B, zero) give a wrong digest on the first of 350 random and adversarial batches; '
                   'the recount after deletion is a wrong digest, so no op of this step is removable. No mask in this step (out bound %.3f units < 16), so there is no overflow-only necessity question: '
                   'the lane sum cannot reach 2^36 (exact arithmetic bound).') % (n, n, outb)
            notes = 'Necessity is shown per op by a counterexample batch for each variant tried; replacement by other operations was not enumerated here (the rotation is covered in Q4).'
            reopen = 'an op of this step is removable under a replacement other than pass A, pass B or zero'
            held = ENV + ' Single deletion of one op at a time; three replacement variants; 350 batches (300 random, 50 adversarial).'
            if call == 'R2D2' and q == 1:
                notes += ' The a-chain out of this step (14.807 units) is what forces the mask in D2.q3 (not in this unit).'
            ev = W + 'q2_mutate.py; ' + W + 'q2_mutate.json'
    elif Q == 'Q3':
        quest = 'Q3 degrees of freedom or score-optimal value: cheapest evaluation of this quarter-step (add order, mask placement) and of the whole circuit under the lane-bound model'
        if has_mask:
            fr = '1 add order: a 15.529 + b 1 = 16.529 units forces the mask before the add (no other placement is cheaper)'
        elif isA and zero:
            fr = '1 add order (a single add, the message word is zero)'
        elif isA:
            fr = '%d cost-equal add trees (which pair is added first), none cheaper' % trees
        else:
            fr = '1 add order (two operands)'
        num = ('%d ops as shipped = score-optimal for this step under the bound model; %s. Whole-circuit exhaustive search over every add order, premask and postmask placement '
               '(two independent halves, Pareto DP over 3 rounds) gives the optimum 595 ops = shipped, so no step can be made cheaper by reordering or by moving masks. '
               'Value of one op = 0.00240 bit of time_log2 (main loop share 0.9944).') % (n, fr)
        labels = ['Z']
        notes = 'Exact inside the shipped bound model (interval bound per word, mask when a sum could reach 2^36); a tighter lane-bound proof would change the model (see Q2 of R2D1.q3 for the mask that the witness shows necessary).'
        ev = W + 'q3_opt.py; ' + W + 'q3_opt_out.txt; ' + W + 'q3_plan.py; ' + W + 'boundcheck.py'
        held = ENV + ' Bound model: add allowed only if bounds sum < 2^36; mask costs 1 op and resets bound to 2^32-1; xor bound = next power of two minus 1; rotation output clean; the 4 digest masks kept.'
        reopen = 'a proof that a lane sum stays below 2^36 where the model masks (false for D1.q3, witness in Q2), or a lane layout other than 7 x 36 bits'
    else:
        quest = 'Q4 alternatives: other ways to compute this quarter-step (rotation by %d in fewer ops; other add trees)' % r
        a = A[r]
        b = Bf.get(r)
        txt = ('no 4-op program computes the lane-wise ror%d (clean 32-bit result, arbitrary 36-bit lane input incl. guard garbage, arbitrary neighbour lanes) '
               'in family A (%d unary ops: shifts and interval/complement masks; %d nodes tried, 0 found)') % (r, a[3], a[4])
        if b:
            txt += ' nor in family B (all 35 shift amounts, %d unary ops, %d nodes, 0 found)' % (b[3], b[4])
        txt += ('. The same search finds the shipped 5-op form (shr, shl, and, and, or/xor/add; 72 variants) in a small validation family, so it can see such programs. '
                'Add alternatives: %s. The rotation part stays 5 ops and the step stays %d ops.') % (('%d equal-cost trees, none cheaper' % trees) if trees > 1 else 'one tree only', n)
        num = txt
        labels = ['Z']
        notes = ('Family-limited: shl/shr by the listed amounts, and with lane-replicated interval masks and their complements, reg-reg and/or/xor/add; no xor/add immediates; '
                 'the middle lane of a 3-lane model must be exact. Outside the family this is OPEN.')
        ev = W + 'rotsearch.cpp; ' + W + 'run_rot4.sh; ' + W + 'rot4_out.txt; ' + W + 'run_rot4b.sh; ' + W + 'rot4b_out.txt; ' + W + 'rot_validate.txt'
        held = ENV + ' Rotation by %d with inputs allowed to carry guard bits (xor of an unclean sum).' % r
        reopen = 'a 4-op rotation using xor/add immediates, other shift sets, or a lane pitch other than 36'
    return dict(hash='blake3-r3', row_i=None, row_j=None, object=obj, question=quest, labels=labels, status=status, number=num,
                source='our workflow: dig-scan-b3r3', own_test=True, evidence=ev, date='2026-10-12', lever=False, gain_bits=None,
                notes=notes, held_fixed=held, reopen_if=reopen)


n = 0
for unit, cells in UNITS.items():
    d = os.path.join('..', 'blake3-r3-' + unit)
    os.makedirs(d, exist_ok=True)
    for call, q in cells:
        for Q in ('Q1', 'Q2', 'Q3', 'Q4'):
            rec = build(call, q, Q)
            cid = 'blake3-r3|%s.q%d|step|%s' % (call, q, Q)
            json.dump(rec, open(os.path.join(d, cid.replace('|', '_') + '.json'), 'w'), indent=1)
            n += 1
print('written', n)
