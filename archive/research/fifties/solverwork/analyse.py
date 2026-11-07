#!/usr/bin/env python3
"""analyse.py (fifties/solverwork): executed solver work vs its cap, from measure_{P,R}_<limit>.json.
Model cells (T, count over 2^67) and CBAR are copied from pkg19/as_subset/prereg7/ledger.txt; CREDIT_G and N_G from
sol_answer_CD_stack.md 11.4. Prints one JSON summary per walk and writes summary.json."""
import sys, os, json, math
from fractions import Fraction as Fr
HERE = os.path.dirname(os.path.abspath(__file__))
LIMIT = int(sys.argv[1]) if len(sys.argv) > 1 else 1000000
CELLS = {0x01: 2442795331092480, 0x02: 12656372660305920, 0x04: 2442795331092480, 0x08: 715390061248512,
         0x10: 7433077221752832, 0x12: 7593823596183552, 0x18: 628147370852352, 0x40: 1419514137280512,
         0x42: 779001660702720, 0x52: 467400996421632}
CBAR_OLD = Fr(582173006981436, 2 ** 47)
CREDIT_G, N_G = 2249200173638569939473, 13743909611614342827230
SMALLB, LARGEB = {0, 1, 6}, {2, 3, 4}
FAM = {0: 'L175', 1: 'H1', 2: 'L275', 3: 'H1', 4: 'H1', 6: 'H685'}


def caps(T):
    bits = [j for j in range(7) if T >> j & 1]
    F = len({FAM[j] for j in bits})
    ns, nl = sum(j in SMALLB for j in bits), sum(j in LARGEB for j in bits)
    return (1024 + 2304 * F + 3328 * ns + 5216 * nl, 4096 + 2304 * F + 6016 * ns + 10720 * nl)


C7 = {0x01: 12416, 0x02: 12416, 0x04: 17120, 0x08: 17120, 0x10: 17120, 0x12: 23136, 0x18: 27840, 0x40: 12416,
      0x42: 20736, 0x52: 31456}
assert all(caps(T)[1] == C7[T] for T in CELLS)
assert sum(n * C7[T] for T, n in CELLS.items()) == CBAR_OLD * 2 ** 67
P_MODEL = Fr(sum(CELLS.values()), 2 ** 67)
CAPG_MODEL = Fr(sum(n * caps(T)[0] for T, n in CELLS.items()), 2 ** 67)        # per outer step
CREDIT_BASIS = Fr(16, 27) * CBAR_OLD                                          # per outer step (CD 11.4)


def bits_gain(r, f):
    return -math.log2(1 - f * (1 - r))


def one(walk):
    d = json.load(open(os.path.join(HERE, 'measure_%s_%d.json' % (walk, LIMIT))))
    steps = sum(d['steps_scanned'].values())
    calls = d['calls']
    cells = d['cells']                                   # [T, exG, exO, n]
    per = {}
    s1 = s2 = 0
    rat = []
    for T, g, o, n in cells:
        c = per.setdefault(T, dict(n=0, sg=0, so=0, sgg=0))
        c['n'] += n
        c['sg'] += g * n
        c['so'] += o * n
        c['sgg'] += g * g * n
        s1 += g * n
        s2 += g * g * n
        rat.append((g / caps(T)[0], n))
    assert s1 == d['sumG'] and sum(c['n'] for c in per.values()) == calls
    mean_g = s1 / calls
    sd_g = math.sqrt(s2 / calls - mean_g ** 2)
    rat.sort()
    q = {}
    acc = 0
    for x, n in rat:
        acc += n
        for p in (0.01, 0.1, 0.25, 0.5, 0.75, 0.9, 0.99, 1.0):
            if p not in q and acc >= p * calls:
                q[p] = round(x, 4)
    # model-reweighted executed mean per outer step: sum_T P_model(T) * mean_exec(T)
    rw = sum(Fr(CELLS[T], 2 ** 67) * Fr(c['sg'], c['n']) for T, c in per.items())
    rw_var = sum((float(Fr(CELLS[T], 2 ** 67)) ** 2) * ((c['sgg'] / c['n'] - (c['sg'] / c['n']) ** 2) / c['n'])
                 for T, c in per.items())
    raw_step = Fr(s1, steps)
    r_credit = float(rw / CREDIT_BASIS)
    r_capmodel = float(rw / CAPG_MODEL)
    se_r = math.sqrt(rw_var) / float(CREDIT_BASIS)
    xg = d['sumxG'] / calls
    r_credit_x = float((rw + Fr(d['sumxG'], calls) * P_MODEL) / CREDIT_BASIS)
    f_G = CREDIT_G / N_G
    out = dict(
        walk=walk, outer_steps=steps, solver_calls=calls,
        P_T_nonzero_measured=calls / steps, P_T_nonzero_model=float(P_MODEL),
        per_call=dict(mean_exec_G=round(mean_g, 1), sd_exec_G=round(sd_g, 1), se_exec_G=round(sd_g / math.sqrt(calls), 2),
                      mean_cap_G_sample=round(d['sumcapG'] / calls, 1), ratio_sample=round(s1 / d['sumcapG'], 5),
                      max_exec_G=d['maxG'], over_cap_G=d['overG'],
                      mean_exec_old=round(d['sumO'] / calls, 1), mean_cap_old=round(d['sumcapO'] / calls, 1),
                      ratio_old=round(d['sumO'] / d['sumcapO'], 5), max_exec_old=d['maxO'], over_cap_old=d['overO'],
                      program_extras_mean=round(xg, 1)),
        exec_over_cap_quantiles={str(k): v for k, v in q.items()},
        per_step=dict(exec_G_raw=float(raw_step), exec_G_model_reweighted=float(rw), cap_G_model_mean=float(CAPG_MODEL),
                      credit_basis_16_27_cbar_old=float(CREDIT_BASIS), cbar_old=float(CBAR_OLD)),
        r_vs_credit_basis=round(r_credit, 5), r_vs_credit_basis_se=round(se_r, 5),
        r_vs_capG_model=round(r_capmodel, 5),
        r_vs_credit_basis_with_program_extras=round(r_credit_x, 5),
        capG_model_over_credit_basis=round(float(CAPG_MODEL / CREDIT_BASIS), 5),
        bit_gain_f021=round(bits_gain(r_credit, 0.21), 4),
        bit_gain_f021_capmodel_only=round(bits_gain(float(CAPG_MODEL / CREDIT_BASIS), 0.21), 4),
        credit_share_NG=round(f_G, 5), bit_gain_NG=round(bits_gain(r_credit, f_G), 4),
        cells={('%02x' % T): dict(n=c['n'], mean_exec_G=round(c['sg'] / c['n'], 1), cap_G=caps(T)[0],
                                  ratio=round(c['sg'] / c['n'] / caps(T)[0], 4),
                                  mean_exec_old=round(c['so'] / c['n'], 1), cap_old=caps(T)[1],
                                  model_share=round(CELLS[T] / sum(CELLS.values()), 5),
                                  sample_share=round(c['n'] / calls, 5)) for T, c in sorted(per.items())},
        chk=d['chk'], cnt15=d['cnt15'], cnt7=d['cnt7'], ratio_hist_20ths=d['ratio_hist'], seconds=d['seconds'])
    # per-row tree units (G15 layout) vs the row tree caps 1920 / 3808
    rows = {}
    for t, u, n in d['rowG']:
        r = rows.setdefault(t, dict(n=0, s=0, zero=0, mx=0))
        r['n'] += n
        r['s'] += u * n
        r['zero'] += n if u == 0 else 0
        r['mx'] = max(r['mx'], u)
    # split: fixed(T) = 1024 + 2304 F + 1408 |T| depends on T only (exact model mean); tree = executed - fixed
    def fixed(T):
        bits = [j for j in range(7) if T >> j & 1]
        return 1024 + 2304 * len({FAM[j] for j in bits}) + 1408 * len(bits)
    fixed_model = Fr(sum(n * fixed(T) for T, n in CELLS.items()), 2 ** 67)
    tree_cap_model = CAPG_MODEL - fixed_model
    tree_exec_rw = rw - fixed_model
    out['split_per_step'] = dict(fixed_model=float(fixed_model), tree_cap_model=float(tree_cap_model),
                                 tree_exec_measured=float(tree_exec_rw),
                                 tree_exec_share_of_tree_cap=round(float(tree_exec_rw / tree_cap_model), 5),
                                 tree_exec_share_of_exec=round(float(tree_exec_rw / rw), 5),
                                 per_call_fixed=round(float(fixed_model / P_MODEL), 1),
                                 per_call_tree_exec=round(float(tree_exec_rw / P_MODEL), 1),
                                 per_call_tree_cap=round(float(tree_cap_model / P_MODEL), 1))
    out['rows_G15_tree'] = {t: dict(n=r['n'], mean_tree=round(r['s'] / r['n'], 1),
                                    tree_cap=1920 if t[0] in '16' else 3808, dropped_share=round(r['zero'] / r['n'], 4),
                                    max_tree=r['mx']) for t, r in sorted(rows.items())}
    return out


res = {w: one(w) for w in ('P', 'R')}
json.dump(res, open(os.path.join(HERE, 'summary.json'), 'w'), indent=1)
print(json.dumps(res, indent=1))
