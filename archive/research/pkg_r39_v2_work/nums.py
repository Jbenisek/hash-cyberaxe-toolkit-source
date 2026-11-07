# nums.py : every advice-dependent number of the r39 package text, computed from its sources (ledger windows, stats windows,
# frozen sandbox values, tail runs). nums(case) -> dict name -> formatted string. Used for the template (to locate) and the new pairs.
import json, glob, math
from fractions import Fraction
T99 = 2.499867
def fc(x, d=0): return format(x, ',.%df' % d)
def st(x):
    n = len(x); m = sum(x) / n; return m, math.sqrt(sum((v - m) ** 2 for v in x) / (n - 1))
def timeq(q, mu_p, c_m, r_m):
    lp = math.log2(585 / 524288) - 32 + q; lam = -math.log(0.60999); G = lam / 2 ** lp; N = G / r_m
    B = math.floor(N * (1 + 2 ** -19) / c_m) + 1; WB = math.floor(B * mu_p * (1 + 2 ** -20)) + 1
    T = Fraction(WB + 2 ** 51 + 6 * B, 2812) + 2 ** 36
    return math.log2(T.numerator) - math.log2(T.denominator), G, N, B, WB
def nums(c):
    V = {}
    W = sorted((json.load(open(f))[0] for f in glob.glob(c['led'] + '/win_*.json')), key=lambda w: w['seed']); n = len(W)
    ops = [w['ops'] for w in W]; cl = [w['distinct_claws'] for w in W]; gr = [w['distinct_groups'] for w in W]; rr = [g / x for g, x in zip(gr, cl)]
    C, Gt, T = sum(cl), sum(gr), sum(ops); raw = sum(w['raw'] for w in W)
    mo, so = st(ops); mc, sc = st(cl); mg, sg = st(gr); mr, sr = st(rr)
    mu_p = math.ceil(mo + T99 * so / math.sqrt(n)); c_m = mc - T99 * sc / math.sqrt(n); g_m = mg - T99 * sg / math.sqrt(n); r_m = mr - T99 * sr / math.sqrt(n)
    q = c['qdecl']; t, G, N, B, WB = timeq(q, mu_p, c_m, r_m)
    V.update(C=fc(C), Gt=fc(Gt), raw=fc(raw), opc='%.1f' % (T / C), opc_c=fc(T / C, 1), comp='%.4f' % (T / C / 2812),
      opc_min='%.1f' % min(o / x for o, x in zip(ops, cl)), opc_max='%.1f' % max(o / x for o, x in zip(ops, cl)),
      ops_mean=fc(mo), ops_sd=fc(so), ops_max=fc(max(ops)), cl_mean='%.2f' % mc, cl_mean1='%.1f' % mc, cl_sd='%.2f' % sc,
      gr_mean='%.2f' % mg, gr_sd='%.2f' % sg, gr_range='%s to %s' % (fc(min(gr)), fc(max(gr))), ratio='%.6f' % (Gt / C), r_mean='%.6f' % mr, r_sd='%.6f' % sr,
      mu_p=fc(mu_p), c_m=fc(c_m, 2), g_m=fc(g_m, 2), r_m='%.6f' % r_m, cr_m=fc(float('%.2f' % c_m) * float('%.6f' % r_m), 2), cr_m_x=fc(c_m * r_m, 2),
      B=str(B), B2='%.4f' % math.log2(B), B2s='%.2f' % math.log2(B), WB=str(WB), WB2='%.4f' % math.log2(WB), G2='%.4f' % math.log2(G), N2='%.4f' % math.log2(N),
      time='%.5f' % t, time3='%.3f' % (math.ceil(t * 1000) / 1000), plogc='%.6f' % (math.log2(585 / 524288) - 32 + q),
      t_m01='%.4f' % timeq(q - 0.1, mu_p, c_m, r_m)[0],
      hoef_w='%.1f' % (math.floor((1 + math.log2(B) + 2 * (math.log2(mu_p) - 20) - 102) * 10) / 10),
      hoef_c='%.1f' % (math.floor((1 + math.log2(B) + 2 * (math.log2(c_m) - 20) - 52) * 10) / 10),
      krange='%d to %d' % (min(w['kernel_len'] for w in W), max(w['kernel_len'] for w in W)), nreg=str(max(w['kernel_nreg'] for w in W)),
      qmax=fc(max(w['qmax'] for w in W)), idc_max=fc(max(w['trails'] for w in W)), idc_min=fc(min(w['trails'] for w in W)),
      idc_frac='%.3f' % (max(w['trails'] for w in W) / 2 ** 20))
    V['_tq'] = lambda qq: '%.4f' % timeq(qq, mu_p, c_m, r_m)[0]
    # Section 5 table and events
    S = lambda k: sum(w['cat'].get(k, 0) for w in W); E = lambda k: sum(w[k] for w in W)
    s1 = sum(w['iters'] * (w['kernel_len'] + 10) for w in W); s2w = sum(w['s2iters'] * (w['kernel_len'] + 3) for w in W)
    rows = [('s1walk', s1), ('hits', S('hits')), ('cut', S('cutscan')), ('s2walk', s2w), ('s2oth', S('stage2') - s2w), ('ws', S('window_setup') - S('generator')),
            ('gen', S('generator')), ('run', S('run_setup'))]
    for k, v in rows:
        V['tab_' + k] = '%.1f' % (v / C); V['pct_' + k] = '%.1f%%' % (100 * v / T)
    V['tab_end'] = '%.1f' % ((T - sum(v for _, v in rows)) / C); V['filters'] = '%.1f' % ((S('claw_filter') + S('claw_f8') + S('claw_w17')) / C)
    V.update(ev_hits='%.2f' % (E('hits') / C), ev_match='%.3f' % (E('matches') / C), ev_opp='%.3f' % (E('opp') / C), ev_same='%.3f' % (E('same') / C),
      ev_it='%.3f' % (E('iters') / C), ev_eval='%.1f' % (E('iters') * 256 / C), ev_s2='%.3f' % (E('s2iters') / C), ev_s2l='%.1f' % (E('s2iters') * 128 / C),
      ev_pairs='%.3f' % (E('pairs') / C), ev_moves='%.3f' % (E('moves') / C), ev_drops='%.4f' % (E('drops') / C), ev_s2c='%.1f' % (E('s2phases') / n),
      rf9=fc(E('f9')), rf9r='%.5f' % (E('f9') / raw), rf8=fc(E('f8')), rf8r='%.4f' % (E('f8') / E('f9')), rw17=str(E('w17')))
    pr = E('f9') / raw
    V['rf9_chi'] = '%.1f' % sum((w['f9'] - w['raw'] * pr) ** 2 / (w['raw'] * pr * (1 - pr)) for w in W)
    V['appA'] = ['| %d | %d | %d | %d | %.1f | %d | %d |' % (w['seed'], w['distinct_claws'], w['distinct_groups'], w['ops'], w['ops'] / w['distinct_claws'], w['kernel_len'], w['kernel_nreg']) for w in W]
    # offline uniformity (stats windows)
    if c.get('stats'):
        Ss = sorted((json.load(open(f)) for f in glob.glob(c['stats'] + '/s_*.json')), key=lambda s: s['seed'])
        Lc = {w['seed']: w['distinct_claws'] for w in W}
        assert len(Ss) == n and all(Lc[s['seed']] == s['claws'] for s in Ss)
        p9, p8 = 65 / 4096, 9 / 128; pj = p9 * p8
        z = lambda o, N_, p: (o - N_ * p) / math.sqrt(N_ * p * (1 - p))
        f9 = sum(s['f9'] for s in Ss); f8 = sum(s['f8'] for s in Ss); bo = sum(s['both'] for s in Ss); Nn = sum(s['claws'] for s in Ss)
        V.update(s_f9=fc(f9), s_f9r='%.5f' % (f9 / Nn), s_f9z='%.2f' % z(f9, Nn, p9), s_f9r6='%.6f' % (f9 / Nn), s_f8=fc(f8), s_f8r='%.5f' % (f8 / Nn), s_f8z='%.2f' % z(f8, Nn, p8),
          s_bo=fc(bo), s_bor='%.6f' % (bo / Nn), s_bor_e='%.6f' % pj, s_cond='%.5f' % (bo / f9), s_condz='%.2f' % z(bo, f9, p8))
        for k in (8, 12, 16, 20, 24):
            o = sum(s['low'][str(k)] for s in Ss); V['low%d' % k] = '%s (%.2f)' % (fc(o), Nn / 2 ** k); V['low%dz' % k] = (o - Nn / 2 ** k) / math.sqrt(Nn / 2 ** k)
        def chi(h):
            e = sum(h) / len(h); return sum((x - e) ** 2 / e for x in h)
        def agg(key):
            h = [0] * len(Ss[0][key])
            for s in Ss:
                for i, v in enumerate(s[key]): h[i] += v
            return h
        for key, df in (('lo16', 65535), ('hi16', 65535), ('w18', 255)):
            x = chi(agg(key)); V['chi_' + key] = '%.1f' % x; V['chiz_' + key] = '%.2f' % ((x - df) / math.sqrt(2 * df))
        zs = [(chi(s['lo16']) - 65535) / math.sqrt(2 * 65535) for s in Ss]; ss = sum(x * x for x in zs)
        V.update(pw_min='%.2f' % min(zs), pw_max='%.2f' % max(zs), pw_mean='%.2f' % (sum(zs) / n), pw_ms='%.2f' % (ss / n), pw_ss='%.1f' % ss, pw_sig='%.1f' % ((ss - n) / math.sqrt(2 * n)))
        V['bc9'] = '%.1f' % sum((s['f9'] - s['claws'] * p9) ** 2 / (s['claws'] * p9 * (1 - p9)) for s in Ss)
        V['bc8'] = '%.1f' % sum((s['f8'] - s['claws'] * p8) ** 2 / (s['claws'] * p8 * (1 - p8)) for s in Ss)
        q9 = f9 / Nn; q8 = f8 / Nn
        V['bc9e'] = '%.1f' % sum((s['f9'] - s['claws'] * q9) ** 2 / (s['claws'] * q9 * (1 - q9)) for s in Ss)
        V['bc8e'] = '%.1f' % sum((s['f8'] - s['claws'] * q8) ** 2 / (s['claws'] * q8 * (1 - q8)) for s in Ss)
        V['bc9sig'] = (float(V['bc9']) - (n - 1)) / math.sqrt(2 * (n - 1)); V['bc8sig'] = (float(V['bc8']) - (n - 1)) / math.sqrt(2 * (n - 1))
        adj = sum(s['adj9'] for s in Ss); ea = sum((s['claws'] - 1) * (s['f9'] / s['claws']) ** 2 for s in Ss)
        V.update(adj=fc(adj), adj_e='%.1f' % ea, adj_z='%.2f' % ((adj - ea) / math.sqrt(ea)))
        rs = []
        for s in Ss:
            m_ = s['claws']; p = s['f9'] / m_; rs.append(((s['adj9'] / (m_ - 1) - p * p) / (p * (1 - p)), m_))
        V['ac_max'] = '%.4f' % max(abs(r) for r, _ in rs); V['ac_wmean'] = '%.4f' % (sum(r * m_ for r, m_ in rs) / sum(m_ for _, m_ in rs))
    # sandbox frozen values
    F = json.load(open(c['freeze']))
    wx = list(F['WIN_EXP'].values()); nG = F['nG']
    col = lambda i: [w[i] for w in wx]
    V.update(nG=fc(nG), wx_cl=str(col(0)), wx_gr=str(col(1)), wx_dp=str(col(2)), wx_ma=str(col(3)), wx_s2=str(col(4)), wx_raw=str(col(5)), wx_f9=str(col(6)), wx_f8=str(col(7)),
      wx_f8all=str(col(8)), wx_l8=str(col(9)), wx_l12=str(col(10)), wx_kr=str(col(11)), wx_ops=str(col(12)), wx_blk=str(col(14)),
      f9t=str(sum(col(6))), f8t=str(sum(col(7))), f8allt=str(sum(col(8))), l8t=str(sum(col(9))), l12t=str(sum(col(10))),
      e9='%.2f' % (nG * 65 / 4096), ej='%.2f' % (nG * 585 / 524288), e8='%.2f' % (nG * 9 / 128), el8='%.2f' % (nG / 256), el12='%.2f' % (nG / 4096),
      c17='%.2f' % F['c17'], c18='%.2f' % F['c18'], c18s=repr(F['c18']), ac=['%.4f' % a[0] for a in F['autocorr']], acse=['%.1f' % a[1] for a in F['autocorr']],
      krec=str(F['e1_tmpl']['kernel_records']), wx_ratio='%.4f' % (sum(col(1)) / nG))
    V['t4'] = c['t4']; V['idc_off'] = c['idc_off']
    # tail
    rows = []
    for i in range(1, 15):
        d = json.load(open('%s/out_%02d.json' % (c['tail'], i)))['trials']; o0 = d[0]['observations']
        rows.append((o0['log2_carrier'], sum(x['observations']['hits'] for x in d[1:21]), [sum(x['observations']['c%s' % k] for x in d[1:21]) for k in ('00', '01', '10', '11')]))
    NP = 20 * 80 * 2048; m14 = 14
    ql = [(2.0 ** r[0]) * (r[1] / NP) for r in rows]; m, sd = st(ql); lg = [math.log2(x) for x in ql]; ml, sdl = st(lg)
    q01 = [(2.0 ** r[0]) * (4.0 * r[2][1] / NP) for r in rows]; m1, sd1 = st(q01); l01 = [math.log2(x) for x in q01]; _, sdl01 = st(l01)
    cls = [sum(r[2][k] for r in rows) for k in range(4)]; H = sum(cls); e = H / 4
    V.update(hits=fc(H), cls=str(cls), chi='%.2f' % sum((x - e) ** 2 / e for x in cls), mean='%.4f' % math.log2(m), lcb99='%.4f' % math.log2(m - 2.650308 * sd / math.sqrt(m14)),
      lcblog='%.4f' % (ml - 2.650308 * sdl / math.sqrt(m14)), lcb999='%.4f' % math.log2(m - 3.852 * sd / math.sqrt(m14)), par99='%.4f' % math.log2(m1 - 2.650308 * sd1 / math.sqrt(m14)),
      m01='%.4f' % math.log2(m1), sd01='%.4f' % sdl01, h01=fc(cls[1]), sdl='%.4f' % sdl, tdecl='%.4f' % ((m - 2 ** q) / (sd / math.sqrt(m14))),
      margin='%.4f' % (math.log2(m - 3.852 * sd / math.sqrt(m14)) - q), qd='%.2f' % q, hmin=str(min(r[1] for r in rows)), hmax=str(max(r[1] for r in rows)),
      lmin='%.3f' % min(lg), lmax='%.3f' % max(lg))
    V['t_mean'] = V['_tq'](math.log2(m))
    return V

BASE = '../pkg_r39_best_work'
CASES = {
 'best': dict(led=BASE + '/led', stats=BASE + '/stats', freeze='freeze_best.json', t4=[473,477,32719,978,748,15,15,7317,21892301,1234,0,996,493], idc_off=1998,
              tail=BASE + '/tail', qdecl=-74.52),
 's108': dict(led='../pkg_r39_vars/p_p39chars108_p39s/led', stats='stats_s108', freeze='freeze_s108.json', idc_off=2000,
              tail='../pkg_r39_combined/work/tail_var/p_p39chars108_p39s', qdecl=-74.49),
 '7111': dict(led='../pkg_r39_vars/7111e7edc4/led', stats='stats_7111', freeze='freeze_7111.json', idc_off=2000,
              tail='../pkg_r39_combined/work/tail_var/7111e7edc4', qdecl=-74.50),
}
for k in ('s108', '7111'):
    try: CASES[k]['t4'] = json.load(open('t4_%s.json' % k))['T4']
    except Exception: CASES[k]['t4'] = None
if __name__ == '__main__':
    import sys
    V = nums(CASES[sys.argv[1]])
    for k, v in V.items():
        if k not in ('appA', '_tq'): print(k, '=', v)
