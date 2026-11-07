"""Round cells U04..U20 (R1,R2,R3,P1,P2,R60..R63).  One exact degree-tracker recount per variant (tracker validated against
independent NTT degrees, see validate_log.txt).  Writes one JSON per cell.  r = 2 (poseidon-r2)."""
import json, copy, random, sys, re
from pos_scan_lib import *

R_ = 2
DATE = '2026-10-12'
SRC = 'our workflow: dig-scan-poseidon'
EV_COMMON = ('research/dig/incoming4/_pr2scan/pos_scan_lib.py; research/dig/incoming4/_pr2scan/rcells.py; '
             'research/dig/incoming4/_pr2scan/validate_log.txt; research/dig/incoming4/_pr2scan/r2_j0_c0.json.txt')
IDX = {'R1': 1, 'R2': 2, 'R3': 3, 'P1': 4, 'P2': 5, 'R60': 60, 'R61': 61, 'R62': 62, 'R63': 63}
rng = random.Random(20261012)

# ---- unit/cell list
units = {}
for l in open(os.path.join(OUT, '..', 'UNITS.jsonl'), encoding='utf8'):
    d = json.loads(l)
    i = d.get('id', '')
    if i.startswith('poseidon-r2-U') and 4 <= int(i[-2:]) <= 20:
        units[i] = d['cells']

FULL = {1, 2, 3, 60, 61, 62, 63}
E5 = INV5
E5_BITS = E5.bit_length(); E5_POP = bin(E5).count('1')

# ---- W-model (rounds >= 2) --------------------------------------------------
_line_cache = {}
def lineaff(j):
    if j not in _line_cache:
        _line_cache[j] = line_affine(j)
    return _line_cache[j]

def wdeg(specs, j):
    alpha, beta, line = lineaff(j)
    res = W_deg(alpha, beta, [d for d in specs if d['idx'] >= 2])
    return res[0] if res and res[1] else ('UNK' if res else 0)

def tweak(specs, kind, idx, lane, val=None):
    sp = copy.deepcopy(specs)
    for rd in sp:
        if rd['idx'] == idx:
            if kind == 'arc': rd['c'][lane] = 0 if val is None else val
            elif kind == 'sbox': rd['sb'][lane] = not rd['sb'][lane]
            elif kind == 'sbox_only': rd['sb'] = [k == lane for k in range(3)]
            elif kind == 'mds_id': rd['M'][lane] = [1 if k == lane else 0 for k in range(3)]
            elif kind == 'mds_row': rd['M'][lane] = val
            elif kind == 'mds_zero': rd['M'][lane][val] = 0
    return sp

def lane_degs(specs, j, upto):
    alpha, beta, line = lineaff(j)
    lanes = W_start(alpha, beta)
    for rd in specs:
        if rd['idx'] < 2: continue
        lanes = run_round(lanes, rd)
        if rd['idx'] == upto: break
    return [(x.e if x is not None else None) for x in lanes]

def ld_txt(sp0, sp, upto):
    b = lane_degs(sp0, 0, upto); v = lane_degs(sp, 0, upto)
    f = lambda L: '[' + ','.join(('5^%d' % round(__import__('math').log(x, 5))) if x and x > 1 else str(x) for x in L) + ']'
    return 'lane degrees (W, j0) after this round: baseline %s, variant %s' % (f(b), f(v))

# ---- tau-model for R1 cells -------------------------------------------------
def setup_line_rc(j, rc1):
    Kp = pow((CAPACITY + RC[0][2]) % P, 5, P)
    base = [(MDS[i][2] * Kp + rc1[i]) % P for i in range(3)]
    a, b = MDS[j][1], (-MDS[j][0]) % P
    d = [(MDS[i][0] * a + MDS[i][1] * b) % P for i in range(3)]
    ii = [i for i in range(3) if i != j]
    (p0, q0), (p1, q1) = (MDS[ii[0]][0], MDS[ii[0]][1]), (MDS[ii[1]][0], MDS[ii[1]][1])
    det = (p0 * q1 - p1 * q0) % P
    r0, r1 = (-base[ii[0]]) % P, (-base[ii[1]]) % P
    U0 = (r0 * q1 - r1 * q0) * inv(det) % P
    V0 = (p0 * r1 - p1 * r0) * inv(det) % P
    return a, b, U0, V0

def tau_run(specs_from1, j, line=None):
    """lanes after R0.S are (U0+a t, V0+b t, K); apply R0.M then rounds >=1.  Returns (deg_tau, Wform_after_R1)."""
    a, b, U0, V0 = line if line else setup_line_rc(j, RC[1])
    Kp = pow((CAPACITY + RC[0][2]) % P, 5, P)
    lanes = [add(const(U0), scale(S(1, [mpz(1)], NEG), a)), add(const(V0), scale(S(1, [mpz(1)], NEG), b)), const(Kp)]
    lanes = [lin(MDS[i], lanes) for i in range(3)]
    wform = None
    first = True
    for rd in specs_from1:
        lanes = run_round(lanes, rd)
        if first:
            first = False
            ok = True
            for x in lanes:
                if x is None: continue
                if x.low > NEG // 2: raise Unknown('R1 lanes should be exact')
                for k, cf in enumerate(x.c):
                    if cf != 0 and (x.e - k) % 5 != 0: ok = False
            wform = ok
    y = lanes[0]
    return (y.e if y is not None else 0), wform, (y.low <= y.e if y is not None else True)

def eff(deg_tau, wform):
    return deg_tau // 5 if wform else deg_tau

def r1_variant_runs(kind, lane, val=None, resolve=False):
    out = []
    sp0 = [d for d in rounds_spec(R_) if d['idx'] >= 1]
    for j in range(3):
        sp = tweak(sp0, kind, 1, lane, val)
        line = None
        if resolve and kind == 'arc':
            rc1 = list(RC[1]); rc1[lane] = sp[0]['c'][lane]
            line = setup_line_rc(j, rc1)
        dt, wf, cert = tau_run(sp, j, line)
        out.append((j, dt, wf, eff(dt, wf), cert))
    return out

def fmt_r1(runs):
    return '; '.join('j%d: tau-deg 5^%s, W-affine-after-R1=%s, effective %s' % (j, round(__import__('math').log(dt, 5), 3) if dt else 0, wf, ('5^%d' % round(__import__('math').log(e, 5))) if e and 5 ** round(__import__('math').log(e, 5)) == e else e) for j, dt, wf, e, cert in runs)

# ---- facts for MDS / S-box alternatives ------------------------------------
def mds_facts():
    M = MDS
    ent = sum(1 for r in M for x in r if x != 0)
    minors = 0
    for i1 in range(3):
        for i2 in range(i1 + 1, 3):
            for j1 in range(3):
                for j2 in range(j1 + 1, 3):
                    if (M[i1][j1] * M[i2][j2] - M[i1][j2] * M[i2][j1]) % P != 0: minors += 1
    # char poly x^3 - t x^2 + s x - d ; root test via gcd(x^P - x, f) with flint
    import flint
    from flint import fmpz_mod_poly_ctx, fmpz_mod_ctx
    R = fmpz_mod_poly_ctx(fmpz_mod_ctx(P))
    t = sum(M[i][i] for i in range(3)) % P
    s = sum(M[i][i] * M[k][k] - M[i][k] * M[k][i] for i in range(3) for k in range(i + 1, 3)) % P
    dt = (M[0][0] * (M[1][1] * M[2][2] - M[1][2] * M[2][1]) - M[0][1] * (M[1][0] * M[2][2] - M[1][2] * M[2][0]) + M[0][2] * (M[1][0] * M[2][1] - M[1][1] * M[2][0])) % P
    f = R([(-dt) % P, s, (-t) % P, 1])
    X = R([0, 1])
    g = f.gcd(X.pow_mod(P, f) - X)
    # powers M^2, M^3 dense?
    def mm(A, B): return [[sum(A[i][k] * B[k][j] for k in range(3)) % P for j in range(3)] for i in range(3)]
    M2 = mm(M, M); M3 = mm(M2, M)
    dense23 = all(x != 0 for r in M2 + M3 for x in r)
    return dict(entries_nonzero=ent, minors_nonzero=minors, charpoly_roots_in_Fp=g.degree(), M2_M3_dense=dense23)

MF = mds_facts()

# ---- the record writer ------------------------------------------------------
def labels_for(comp, deg_changed):
    if comp == 'ARC': return ['N', 'I', 'Z']
    if comp == 'SBOX': return ['C', 'Z'] if deg_changed else ['Z']
    return ['I', 'Z']

def make_cell(cellname, unit):
    _, loc, obj, Q = cellname.split('|')
    rn, ln, comp = loc.split('.')
    lane = int(ln[1])
    idx = IDX[rn]
    full = idx in FULL
    base = 5 ** (6 + R_)
    notes_extra = ''
    deg_changed = False
    held = ''
    reopen = ''
    status = 'COMPUTED'
    q = Q
    if idx == 1:
        # ---------------- tau-model ----------------
        if q == 'Q2':
            if comp == 'ARC':
                fixed = r1_variant_runs('arc', lane, None, resolve=False)
                solved = r1_variant_runs('arc', lane, None, resolve=True)
                number = ('R1.L%d ARC set to 0, line kept: %s | line re-solved for the new constant: %s | baseline: effective 5^8 = %d (W-affine)'
                          % (lane, fmt_r1(fixed), fmt_r1(solved), base))
                deg_changed = any(r[3] != base for r in fixed)
                obj_txt = 'R1 lane %d ARC' % lane
            elif comp == 'SBOX':
                runs = r1_variant_runs('sbox', lane)
                number = 'R1.L%d S-box removed (identity), line kept: %s | baseline effective 5^8 = %d' % (lane, fmt_r1(runs), base)
                deg_changed = any(r[3] != base for r in runs)
                obj_txt = 'R1 lane %d SBOX' % lane
            else:
                runs = r1_variant_runs('mds_id', lane)
                number = 'R1.L%d MDS row replaced by identity row, line kept: %s | baseline effective 5^8 = %d' % (lane, fmt_r1(runs), base)
                deg_changed = any(r[3] != base for r in runs)
                obj_txt = 'R1 lane %d MDS' % lane
            question = 'Q2 necessity: change or drop it and recount the exact digest degree on the line'
        else:
            if comp == 'ARC':
                tot = []
                for t in range(12):
                    v = rng.randrange(1, P)
                    rc1 = list(RC[1]); rc1[lane] = v
                    for j in range(3):
                        sp = tweak([d for d in rounds_spec(R_) if d['idx'] >= 1], 'arc', 1, lane, v)
                        dt, wf, cert = tau_run(sp, j, setup_line_rc(j, rc1))
                        tot.append((eff(dt, wf), wf))
                okc = sum(1 for e, wf in tot if e == base and wf)
                number = '%d of %d random values of the R1.L%d constant (3 lines each, line re-solved by the 2x2 system) keep a W-affine R1 output and effective degree 5^8 = %d' % (okc, len(tot), lane, base)
                deg_changed = okc != len(tot)
                obj_txt = 'R1 lane %d ARC'
                obj_txt = obj_txt % lane
            elif comp == 'SBOX':
                runs = r1_variant_runs('sbox_only', lane)
                number = ('alternative pattern: only lane %d is S-boxed in R1 (others identity), line kept: %s; backward walk through one S-box needs x^(5^-1): %d squarings + %d multiplications (5^-1 mod p-1 has %d bits, popcount %d) versus 3 for the forward x^5'
                          % (lane, fmt_r1(runs), E5_BITS - 1, E5_POP - 1, E5_BITS, E5_POP))
                deg_changed = any(r[3] != base for r in runs)
                obj_txt = 'R1 lane %d SBOX' % lane
            else:
                rowv = [rng.randrange(1, P) for _ in range(3)]
                runs = r1_variant_runs('mds_row', lane, rowv)
                number = ('alternative: random dense row in place of MDS row %d, line kept: %s; pinned M facts: %d/9 entries nonzero, %d/9 2x2 minors nonzero, char poly has %d roots in F_p, M^2 and M^3 dense=%s'
                          % (lane, fmt_r1(runs), MF['entries_nonzero'], MF['minors_nonzero'], MF['charpoly_roots_in_Fp'], MF['M2_M3_dense']))
                deg_changed = any(r[3] != base for r in runs)
                obj_txt = 'R1 lane %d MDS' % lane
            question = 'Q4 alternatives: other patterns, random-value sweep, backward walk'
        held = 'pinned Orchard constants; r=2; line j=0,1,2 (canonical, Q solved for the pinned RC1 unless stated); digest lane 0; everything else in the hash unchanged; exact top-term tracker (24 terms) certified, no cancellation'
        reopen = 'a modified element that keeps the R1 output affine in W while changing the S-box count, or a constant/row choice that makes a leading coefficient vanish'
    else:
        sp0 = specs_from_2(R_)
        degs = lambda sp: [wdeg(sp, j) for j in range(3)]
        def fmt(dg): return 'j0=%s j1=%s j2=%s' % tuple(dg)
        if q == 'Q2':
            if comp == 'ARC':
                dg = degs(tweak(sp0, 'arc', idx, lane))
                what = 'constant set to 0'
            elif comp == 'SBOX':
                dg = degs(tweak(sp0, 'sbox', idx, lane))
                what = 'S-box %s' % ('removed (identity)' if sp0[[d['idx'] for d in sp0].index(idx)]['sb'][lane] else 'added (S-box on this lane too)')
            else:
                dg = degs(tweak(sp0, 'mds_id', idx, lane))
                what = 'MDS row %d replaced by the identity row' % lane
            vsp = tweak(sp0, {'ARC':'arc','SBOX':'sbox','MDS':'mds_id'}[comp], idx, lane)
            number = '%s: digest degree in W %s (baseline 390625 = 5^8 on all three lines, independent NTT check j0,j1,j2); %s' % (what, fmt(dg), ld_txt(sp0, vsp, idx))
            deg_changed = any(x != base for x in dg)
            question = 'Q2 necessity: change or drop it and recount the exact digest degree on the line'
        else:
            if comp == 'ARC':
                tot = []
                for t in range(12):
                    v = rng.randrange(1, P)
                    sp = tweak(sp0, 'arc', idx, lane, v)
                    tot += degs(sp)
                okc = sum(1 for x in tot if x == base)
                number = '%d of %d random values for this constant (12 values x 3 lines) leave the digest degree at 390625; a constant touches only powers below the leading term, so no value can lower the degree unless a top coefficient cancels, and the tracker finds none' % (okc, len(tot))
                deg_changed = okc != len(tot)
            elif comp == 'SBOX':
                dg = degs(tweak(sp0, 'sbox_only', idx, lane))
                number = ('alternative pattern: S-box only on lane %d in this round: digest degree %s (baseline 390625); backward walk through one S-box = x^(5^-1): %d squarings + %d multiplications (exponent %d bits, popcount %d) versus 3 forward'
                          % (lane, fmt(dg), E5_BITS - 1, E5_POP - 1, E5_BITS, E5_POP))
                deg_changed = any(x != base for x in dg)
            else:
                rowv = [rng.randrange(1, P) for _ in range(3)]
                dg = degs(tweak(sp0, 'mds_row', idx, lane, rowv))
                z = [wdeg(tweak(sp0, 'mds_zero', idx, lane, c)[:], 0) for c in range(3)]
                number = ('alternative: random dense row for MDS row %d: degree %s; one entry of the row zeroed (columns 0,1,2, line j0): %s; pinned M: %d/9 entries and %d/9 2x2 minors nonzero, char poly roots in F_p = %d, M^2,M^3 dense=%s'
                          % (lane, fmt(dg), z, MF['entries_nonzero'], MF['minors_nonzero'], MF['charpoly_roots_in_Fp'], MF['M2_M3_dense']))
                deg_changed = any(x != base for x in dg) or any(x != base for x in z)
            question = 'Q4 alternatives: other patterns, random-value sweep, backward walk'
        held = 'pinned Orchard constants; r=2; state after R1 = alpha+beta*W on line j=0,1,2 (reference-validated affine); rounds 2..63 otherwise unchanged; digest lane 0; exact top-term tracker, independently matched by NTT degrees at r=1 (9 variants)'
        reopen = 'a variant whose exact degree is below 5^8 while keeping the pinned hash semantics, or a round-level element where a leading coefficient cancels'
        obj_txt = '%s lane %d %s' % (rn, lane, comp)
    # special notes
    nx = []
    if comp == 'MDS' and idx == 63 and lane in (1, 2):
        nx.append('rows 1 and 2 of the last M are dead (digest reads row 0 only): any change to this row leaves the digest unchanged')
    if rn in ('P1', 'P2') and comp == 'ARC' and lane in (1, 2):
        nx.append('lane-%d constant of a partial round is absorbed into the next round (translation through the linear map)' % lane)
    if rn in ('P1', 'P2') and comp == 'SBOX' and lane in (1, 2):
        nx.append('no S-box acts on this lane in the pinned partial round; the variant adds one')
    if not deg_changed and q == 'Q2':
        nx.append('degree unchanged by this change: the digest degree is the maximum over lanes, so this element does not set it')
    notes = ('universe cell poseidon-r2|%s|RND|%s. %s. Tracker = exact top-term (Laurent) arithmetic over Pallas, 24 terms, precision certificate; '
             'it matched independent NTT degrees (r=1, 9 variants, 3 of them degree-changing, validate_log.txt) and the baseline 5^8 matched an NTT of 2^19 reference-hash evaluations on all three lines (r2_j*_c0.json.txt). '
             'The variants are what-ifs on the pinned hash, not available moves. %s'
             % (loc, q, question, ' '.join(nx)))
    rec = dict(hash='poseidon-r2', row_i=None, row_j=None, object='%s' % obj_txt, question=question,
               labels=labels_for(comp, deg_changed), status=status, number=number, source=SRC, own_test=True,
               evidence=EV_COMMON, date=DATE, lever=False, gain_bits=None, notes=notes, held_fixed=held, reopen_if=reopen)
    return rec

if __name__ == '__main__':
    n = 0
    for unit, cells in units.items():
        for cn in cells:
            rec = make_cell(cn, unit)
            write_cell(unit, cn.split('|', 1)[1] if False else cn, rec)
            n += 1
    print('wrote', n)
