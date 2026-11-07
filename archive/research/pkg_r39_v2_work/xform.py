#!/usr/bin/env python3
# xform.py TAG : transform the 2b4af365 template texts (pkg_r39_best: proof.md, claim.json, experiments/manifest.json,
# submission note) into pkg_r39_TAG by one-pass string replacement. Every new number is read from its source by nums.py
# (ledger windows, stats windows, frozen sandbox values, tail runs); pair-specific clauses are short factual swaps.
# Misses (template literal not found) are printed, never silent.
import sys, os, re, json, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nums import nums, CASES
TAG = sys.argv[1]
TP = '../pkg_r39_best'; NP_ = '../pkg_r39_%s' % TAG
Vt = nums(CASES['best']); V = nums(CASES[TAG])
CH = {'s108': 'pkg_r39_vars_p_p39chars108_p39s.char', '7111': 'pkg_r39_vars_7111e7edc4.char'}
S108 = TAG == 's108'
QD = V['qd']; t3 = V['time3']
def sig(z, word_lo='low', word_hi='high'): return '%.1f sigma %s' % (abs(z), word_lo if z < 0 else word_hi)

# ---------- generated clauses (numbers from the sources) ----------
lowz = {k: V['low%dz' % k] for k in (8, 12, 16, 20)}; kx = max(lowz, key=lambda k: abs(lowz[k]))
halves = max(abs(float(V['chiz_lo16'])), abs(float(V['chiz_hi16'])))
import math
halves_s = '%.1f' % (math.ceil(halves * 10) / 10)
pw_s = 'is %s' % sig(float(V['pw_sig']))
offline_tail = ('the sum of the 24 squares, %s on 24 df, %s; the low-%d match count is %.1f sigma %s its expectation while the pooled 16-bit halves are within %s sigma; disclosed, not used by the claim)'
                % (V['pw_ss'], pw_s, kx, abs(lowz[kx]), 'below' if lowz[kx] < 0 else 'above', halves_s))
def bin_clause():
    s = 'chi-square %s and %s on 23 df' % (V['bc9'], V['bc8'])
    d = [(n_, z) for n_, z in (('F9', V['bc9sig']), ('F8', V['bc8sig'])) if abs(z) >= 2]
    for n_, z in d: s += '; the %s value is %s, disclosed' % (n_, sig(z))
    return s
acs = V['ac']; acse = [float(x) for x in V['acse']]
ac_note = ''   # no lag-1 value reaches 2 standard errors on either new pair (checked below)
assert max(acse) < 2
rf9_disc = '' if abs((float(V['rf9_chi']) - 23) / math.sqrt(46)) < 2 else '; raw claws repeat distinct claws, so they are not independent trials; disclosed'
p_t = {'s108': 'p < 1e-5', '7111': 'p < 1e-3'}[TAG]   # scipy t.sf(t_decl, 13): s108 6.7161 -> 7.2e-6, 7111 4.4119 -> 3.5e-4
dt = '%.3f' % (117.836 - float(t3))

# ---------- the replacement list: (template literal, new text) ----------
R = []
def r(a, b): R.append((a, b))
# time, halts, ledger bounds
r('116.89462', V['time']); r('116.895', t3); r('116.7145', V['t_mean'])
r('875224534025647266674449055745', V['B']); r('434312448423543105820061636936834482177', V['WB'])
r('2^99.4656', '2^' + V['B2']); r('2^99.47', '2^' + V['B2s']); r('2^128.3520', '2^' + V['WB2'])
r('115.3112', V['G2']); r('2^115.3133', '2^' + V['N2']); r('-116.327707', V['plogc'])
r('2^17.1', '2^' + V['hoef_w']); r('2^40.9', '2^' + V['hoef_c'])
r('496,229,273', V['mu_p']); r('58,973.72', V['c_m']); r('58,890.83', V['g_m']); r('0.998513', V['r_m']); r('58,886.03', V['cr_m'])
r('1,418,347', V['C']); r('1,416,335', V['Gt']); r('1,671,129', V['raw'])
r('8,319.1 = 2.9584 compressions', '%s = %s compressions' % (V['opc_c'], V['comp'])); r('8319.1', V['opc']); r('8,319.1', V['opc_c'])
r('8102.8', V['opc_min']); r('8633.9', V['opc_max'])
r('491,639,962', V['ops_mean']); r('8,993,652', V['ops_sd']); r('505,842,814', V['ops_max'])
r('59097.79', V['cl_mean']); r('59097.8 per window', V['cl_mean1'] + ' per window'); r('243.14', V['cl_sd'])
r('59013.96', V['gr_mean']); r('241.30', V['gr_sd']); r('58,497 to 59,534', V['gr_range'])
r('per-window mean 0.998581', 'per-window mean ' + V['r_mean']); r('per-window mean `0.998581`', 'per-window mean `%s`' % V['r_mean'])
r('0.998581', V['ratio']); r('0.000134', V['r_sd'])
r('685 to 755 records', V['krange'] + ' records'); r('206 registers (135 used)', '206 registers (%s used)' % V['nreg'])
r('peak 3,332 over', 'peak %s over' % V['qmax']); r('526,557', V['idc_max']); r('522,360', V['idc_min'])
# Section 5 table and events (the template carried several of 0b2616e3's event figures; all recomputed here)
r('| 3238.3 | 38.9% |', '| %s | %s |' % (V['tab_s1walk'], V['pct_s1walk'])); r('| 1859.1 | 22.3% |', '| %s | %s |' % (V['tab_hits'], V['pct_hits']))
r('| 22.2 | 0.3% |', '| %s | %s |' % (V['tab_cut'], V['pct_cut'])); r('| 1773.9 | 21.3% |', '| %s | %s |' % (V['tab_s2walk'], V['pct_s2walk']))
r('(of which the filters 46.8) | 1413.9 | 17.0% |', '(of which the filters %s) | %s | %s |' % (V['filters'], V['tab_s2oth'], V['pct_s2oth']))
r('| 1.8 | 0.0% |', '| %s | %s |' % (V['tab_ws'], V['pct_ws'])); r('| 9.8 | 0.1% |', '| %s | %s |' % (V['tab_gen'], V['pct_gen']))
r('Events per distinct claw: 8.88 DP hits, 2.390 matches, 1.178 opposite-parity claws (1.208 same parity, discarded), 4.440 stage-1 iterations (1136.7 evaluations), 2.452 stage-2 iterations (313.9 lane-iterations), 2.390 pairs, 1.028 lane moves, 0.0040 dropped pairs; 43.0 stage-2 calls per window.',
  'Events per distinct claw: %s DP hits, %s matches, %s opposite-parity claws (%s same parity, discarded), %s stage-1 iterations (%s evaluations), %s stage-2 iterations (%s lane-iterations), %s pairs, %s lane moves, %s dropped pairs; %s stage-2 calls per window.'
  % (V['ev_hits'], V['ev_match'], V['ev_opp'], V['ev_same'], V['ev_it'], V['ev_eval'], V['ev_s2'], V['ev_s2l'], V['ev_pairs'], V['ev_moves'], V['ev_drops'], V['ev_s2c']))
r('`W9 in F9` 80,621 of 1,671,129 raw claws (0.01588; 65/4096 = 0.01587), `W8 in F8` 5,795 of 80,621 (0.0719; 9/128 = 0.0703), `W17 = published` 0.',
  '`W9 in F9` %s of %s raw claws (%s; 65/4096 = 0.01587), `W8 in F8` %s of %s (%s; 9/128 = 0.0703), `W17 = published` %s.' % (V['rf9'], V['raw'], V['rf9r'], V['rf8'], V['rf9'], V['rf8r'], V['rw17']))
# Section 7 sensitivity sentence (the template's -74.62 / -76.59 figures did not follow its own formula; restated from it)
r('at `log2 p_tail` = -74.62 the time is 117.0545, at -74.3399 (the plain observed mean of the 14 runs) it is 116.7145, at -76.59 it is 118.9645.',
  'at `log2 p_tail` = %.2f the time is %s, at %s (the plain observed mean of the 14 runs) it is %s.' % (float(QD) - 0.1, V['t_m01'], V['mean'], V['t_mean']))
# Section 7 distinct-claw statistics
r('(chi-square 5.8 and 19.2 on 23 degrees of freedom against the pooled empirical rates, 5.9 and 24.9 against the exact rates 65/4096 and 9/128; the F9 value is 2.5 sigma low, disclosed; pooled 22,528 / 1,418,347 = 0.015883 against 65/4096 = 0.015869, z = 0.13,',
  '(chi-square %s and %s on 23 degrees of freedom against the pooled empirical rates, %s against the exact rates 65/4096 and 9/128; pooled %s / %s = %s against 65/4096 = 0.015869, z = %s,'
  % (V['bc9e'], V['bc8e'], bin_clause().replace('chi-square ', '').replace(' on 23 df', ''), V['s_f9'], V['C'], V['s_f9r6'], V['s_f9z']))
r('1,611 / 22,528 = 0.07151 against 9/128 = 0.07031, z = 0.70); counted over the 1,671,129 raw claws, F9 gives 26,605 (chi-square 15.8 on 23 degrees of freedom against the pooled rate).',
  '%s / %s = %s against 9/128 = 0.07031, z = %s); counted over the %s raw claws, F9 gives %s (chi-square %s on 23 degrees of freedom against the pooled rate%s).'
  % (V['s_bo'], V['s_f9'], V['s_cond'], V['s_condz'], V['raw'], V['rf9'], V['rf9_chi'], rf9_disc))
r('is within 0.0084 in every window (claw-weighted mean -0.0005; 346 adjacent F9 pairs against 357.9 expected under independence, z = -0.63;',
  'is within %s in every window (claw-weighted mean %s; %s adjacent F9 pairs against %s expected under independence, z = %s;' % (V['ac_max'], V['ac_wmean'], V['adj'], V['adj_e'], V['adj_z']))
# offline uniformity block (proof Section 9 and claim H1)
r('`W9 in F9` 22,528 (0.01588 vs 0.01587, z = 0.15); `W8 in F8` 100,445 (0.07082 vs 0.07031, z = 2.35); both 1,611 (0.001136 vs 0.001115); ',
  '`W9 in F9` %s (%s vs 0.01587, z = %s); `W8 in F8` %s (%s vs 0.07031, z = %s); both %s (%s vs %s); ' % (V['s_f9'], V['s_f9r'], V['s_f9z'], V['s_f8'], V['s_f8r'], V['s_f8z'], V['s_bo'], V['s_bor'], V['s_bor_e']))
r('k = 8: 5,431 (5540.42), k = 12: 301 (346.28), k = 16: 17 (21.64), k = 20: 2 (1.35), k = 24: 0 (0.08)',
  'k = 8: %s, k = 12: %s, k = 16: %s, k = 20: %s, k = 24: %s' % (V['low8'], V['low12'], V['low16'], V['low20'], V['low24']))
r('`W17` 66050.1 (65,535 df, z = 1.42), of the high 16 bits of `W17` 65303.2 (65,535 df, z = -0.64), and of `W18 mod 256` 213.4 (255 df, z = -1.84)',
  '`W17` %s (65,535 df, z = %s), of the high 16 bits of `W17` %s (65,535 df, z = %s), and of `W18 mod 256` %s (255 df, z = %s)' % (V['chi_lo16'], V['chiz_lo16'], V['chi_hi16'], V['chiz_hi16'], V['chi_w18'], V['chiz_w18']))
r('has z from -1.30 to 1.10 (mean 0.10, mean square 0.58 against 1 under uniformity; the sum of the 24 squares, 14.0 on 24 df, is 1.4 sigma low; the low-12 match count is 2.4 sigma below its expectation while the pooled 16-bit halves are within 1.5 sigma; disclosed, not used by the claim)',
  'has z from %s to %s (mean %s, mean square %s against 1 under uniformity; %s' % (V['pw_min'], V['pw_max'], V['pw_mean'], V['pw_ms'], offline_tail))
r('binomial F9/F8 counts over distinct claws (chi-square 5.9 and 24.9 on 23 df; the F9 value is 2.5 sigma low, disclosed), and F9 lag-1 autocorrelation within 0.0006 (346 adjacent F9 pairs vs 357.9 expected)',
  'binomial F9/F8 counts over distinct claws (%s), and F9 lag-1 autocorrelation within %s in every window (%s adjacent F9 pairs vs %s expected)' % (bin_clause(), V['ac_max'], V['adj'], V['adj_e']))
r('binomial F9/F8 counts over distinct claws (chi-square 5.9 and 24.9 on 23 df; the F9 value is 2.5 sigma low, disclosed), and F9 lag-1 autocorrelation within 0.0006.',
  'binomial F9/F8 counts over distinct claws (%s), and F9 lag-1 autocorrelation within %s in every window.' % (bin_clause(), V['ac_max']))
r('SE about 0.16% of ops/claw', 'SE about %.2f%% of ops/claw' % (100 * float(V['ops_sd'].replace(',', '')) / float(V['ops_mean'].replace(',', '')) / 24 ** 0.5))
# sandbox: WIN_EXP, serve(), T4, e1
r('[817, 795, 909, 797]', V['wx_cl']); r('[33229, 32736, 32545, 32820]', V['wx_dp']); r('[1744, 1660, 1771, 1653]', V['wx_ma'])
r('[2874, 2355, 2659, 2529]', V['wx_s2']); r('[840, 809, 926, 804]', V['wx_raw']); r('[17, 11, 12, 11]', V['wx_f9']); r('[3, 1, 3, 0]', V['wx_f8'])
r('[60, 54, 73, 53]', V['wx_f8all']); r('[1, 0, 4, 2]', V['wx_l8']); r('[0, 0, 0, 0]', V['wx_l12']); r('[730, 714, 710, 699]', V['wx_kr'])
r('[22914523, 22090605, 22284239, 21944236]', V['wx_ops']); r('[1238, 1238, 1236, 1168]', V['wx_blk'])
assert V['wx_cl'] == V['wx_gr']
r('(805, 835, 792, 838; ratio 1.0000)', '(%s; ratio %s)' % (V['wx_cl'][1:-1], V['wx_ratio']))
r('(`52` total vs 51.9 expected)', '(`%s` total vs %s expected)' % (V['f9t'], V['e9'])); r('(51 total vs 52.65 expected)', '(%s total vs %s expected)' % (V['f9t'], V['e9']))
r('(7 joint F9 & F8 passes vs 3.70 expected)', '(%s joint F9 & F8 passes vs %s expected)' % (V['f8t'], V['ej']))
r('(`228` total vs 229.9 expected)', '(`%s` total vs %s expected)' % (V['f8allt'], V['e8'])); r('(240 total vs 233.30 expected)', '(%s total vs %s expected)' % (V['f8allt'], V['e8']))
r('(`11` total vs 12.77 expected)', '(`%s` total vs %s expected)' % (V['l8t'], V['el8'])); r('(7 total vs 12.96 expected)', '(%s total vs %s expected)' % (V['l8t'], V['el8']))
r('(`2` total vs 0.80 expected)', '(`%s` total vs %s expected)' % (V['l12t'], V['el12'])); r('(0 total vs 0.81 expected)', '(%s total vs %s expected)' % (V['l12t'], V['el12']))
r('`W9 in F9` 51 (52.65 expected), `W8 in F8` 240 (233.30 expected), joint `F9 & F8` 2 (3.65 expected), `W17` low-8-bit matches 7 (12.96 expected), low-12-bit matches 0 (0.81 expected)',
  '`W9 in F9` %s (%s expected), `W8 in F8` %s (%s expected), joint `F9 & F8` %s (%s expected), `W17` low-8-bit matches %s (%s expected), low-12-bit matches %s (%s expected)'
  % (V['f9t'], V['e9'], V['f8allt'], V['e8'], V['f8t'], V['ej'], V['l8t'], V['el8'], V['l12t'], V['el12']))
r('W9 in F9 51 (52.65 expected), W8 in F8 240 (233.30), joint F9 & F8 7 (3.70), W17 low-8 matches 7 (12.96), low-12 matches 0 (0.81)',
  'W9 in F9 %s (%s expected), W8 in F8 %s (%s), joint F9 & F8 %s (%s), W17 low-8 matches %s (%s), low-12 matches %s (%s)'
  % (V['f9t'], V['e9'], V['f8allt'], V['e8'], V['f8t'], V['ej'], V['l8t'], V['el8'], V['l12t'], V['el12']))
r('3,318', V['nG']); r('3318', V['nG'].replace(',', ''))
r('268.01', V['c17']); r('280.20', V['c18']); r('280.2', V['c18s'])
r('(`0.0050`, `0.0459`, `0.0144` on 3,318 claws; `0.0459` is 2.6 standard errors, disclosed)', '(`%s`, `%s`, `%s` on %s claws)' % (acs[0], acs[1], acs[2], V['nG']))
r('(`0.0050`, `0.0459`, `0.0144` on 3,318 groups)', '(`%s`, `%s`, `%s` on %s groups)' % (acs[0], acs[1], acs[2], V['nG']))
r('W9 in F9 (0.0050), W17[0] (0.0459) and W18[0] (0.0144) on 3,318 claws (0.0459 is 2.6 standard errors, disclosed)', 'W9 in F9 (%s), W17[0] (%s) and W18[0] (%s) on %s claws' % (acs[0], acs[1], acs[2], V['nG']))
r('(0.0050, 0.0459, 0.0144; 0.0459 is 2.6 SE, disclosed)', '(%s, %s, %s)' % tuple(acs))
r('(0.0050, 0.0459, 0.0144)', '(%s, %s, %s)' % tuple(acs))
t4o = [473, 477, 32719, 978, 748, 15, 15, 7317, 21892301, 1234, 0, 996, 493]; t4n = V['t4']
K4 = ("distinct_claws", "raw_claws", "dp_hits", "matches", "stage2_iterations", "parks", "resumes", "cuts", "ops", "blk_census", "drops", "idc_stop_iteration", "idc_stop_stage2_iterations")
r(', '.join('%s %d' % kv for kv in zip(K4, t4o)), ', '.join('%s %d' % kv for kv in zip(K4, t4n)))
r(', '.join('`%s` %d' % kv for kv in list(zip(K4, t4o))[:10]), ', '.join('`%s` %d' % kv for kv in list(zip(K4, t4n))[:10]))
r('`idc_stop_iteration` 996, `idc_stop_stage2_iterations` 493', '`idc_stop_iteration` %d, `idc_stop_stage2_iterations` %d' % (t4n[11], t4n[12]))
r('2^20 - 1998', '2^20 - 2000')
r('`pair_is_published` 1, `sfs_collision` 1, `published_w16_is_g` 1, `published_w17` 1, `kernel_records` 734,', '`pair_is_advice` 1, `sfs_collision` 1, `advice_w16_is_g` 1, `advice_w17` 1, `kernel_records` %s,' % V['krec'])
r('pair_is_published 1, sfs_collision 1, published_w16_is_g 1, published_w17 1, kernel_records 734,', 'pair_is_advice 1, sfs_collision 1, advice_w16_is_g 1, advice_w17 1, kernel_records %s,' % V['krec'])
# tail
r('6,326', V['hits']); r('[1628, 1526, 1556, 1616]', V['cls']); r('4.48', V['chi'])
r('-74.3399', V['mean']); r('-74.4140', V['lcb99']); r('-74.4156', V['lcblog']); r('-74.4489', V['lcb999']); r('-74.5162', V['par99'])
r('6.2110', V['tdecl']); r('sample sd of `log2(Q\')` 0.1022', 'sample sd of `log2(Q\')` ' + V['sdl']); r('-74.52', QD); r('QDECL=-74.52', 'QDECL=' + QD)
r('(t = 6.2110, 13 df, p < 1e-4)', '(t = %s, 13 df, %s)' % (V['tdecl'], p_t)); r('6.2110, 13 df, p < 1e-4', '%s, 13 df, %s' % (V['tdecl'], p_t))
r('(13 df, p < 1e-5)', '(13 df, %s)' % p_t); r('(t = 6.2110, p < 1e-5)', '(t = %s, %s)' % (V['tdecl'], p_t))
r('0.0711 bits above the declared -74.52 (linear 99%), and the linear 99.9% bound -74.4489 is 0.0711 above it',
  '%.4f bits above the declared %s (linear 99%%), and the linear 99.9%% bound %s is %s above it' % (float(V['lcb99']) - float(QD), QD, V['lcb999'], V['margin']))
r('`2^116.89462 + 2^36`', '`2^%s + 2^36`' % V['time'])
# Appendix A header + table
r('24 fresh seeds (1000, 2000, ..., 24000), 12 on the local machine and 12 on a 32-core cloud machine', '24 fresh seeds (1000, 2000, ..., 24000), 11 on the local machine and 13 on a 32-core cloud machine')
r('none excluded), 12 on one machine and 12 on another', 'none excluded), 11 on one machine and 13 on another')
r('(dkuthoore, time_log2 = 116.895)', '(dkuthoore, time_log2 = 117.836)')
r("is dkuthoore's accepted 0b2616e3 (time_log2 = 116.895), unchanged;", "is dkuthoore's accepted 0b2616e3 (time_log2 = 117.836), unchanged;")
r("The 14 public tail runs were about 0.07 bit favourable against the 56 further runs (mean -74.4113); the declared -74.52 sits below both.", None)  # placeholder, set per pair below

# ---------- pair-specific clauses ----------
if S108:
    PAIR = 'our second 39-step pair on the published characteristic'
    r('ordinary collision by a transplanted re-signed advice pair,', 'ordinary collision by a transplanted advice pair,')
    r('this entry replaces its advice with our re-signed 39-step pair (Section 2.1, Appendix C)', 'this entry replaces its advice with %s (Section 2.1, Appendix C)' % PAIR)
    r('**2.1 The base is advice: our pair on a re-signed characteristic.**', '**2.1 The base is advice: our second pair on the published characteristic.**')
    r("Its characteristic is the 39-step characteristic of ePrint 2026/1120 Table 21 with the message-schedule signs of rows `W11` and `W12` re-chosen (found by the W9/W11 wiggle search); every A and E state row equals the published characteristic's,",
      "Its signed characteristic is the 39-step characteristic of ePrint 2026/1120 Tables 21 and 23 unchanged: every signed row, state and message schedule, is the published one, only the values differ,")
    r("The signed differences of every state row are the published characteristic's; the state and message values are this pair's own,", "The state and message values are this pair's own,")
    r("(The advice pair's own `W1` is even, so `r39-transplant-claw` trial 0 checks the claw equation through both branch formulas of `F` with check mode off.)",
      "(The advice pair's own `A[4]` is odd, so `r39-transplant-claw` trial 0 checks the claw equation through the even-branch formula of `F` and passes the pair as `claw(u, a0)` with check mode off.)")
    r('with rows W11 and W12 re-signed (proof Section 12, Appendix C)', 'with every signed row the published one (proof Section 12, Appendix C)')
    r('of ePrint 2026/1120 with rows W11 and W12 re-signed (chaining value', 'of ePrint 2026/1120, every signed row the published one (chaining value')
    r('on the advice pair (our re-signed 39-step pair)', 'on the advice pair (our second 39-step pair on the published characteristic)')
    r("the advice's own `W1` is even, so `r39-transplant-claw` trial 0 asserts the claw equation `fstep(a0) = s0(u) - u` directly and runs the filters with check mode off; the forced id-exhaustion run of `T4_EXP` starts at `2^20 - 1998` (at `2^20 - 2000` it no longer stops inside a partly restarted hit group); the lag-1 autocorrelation test is `|r| sqrt(n) < 3` (observed `0.0459` for `W17[0]` on 3,318 groups, 2.6 standard errors, disclosed).",
      "the advice's own `A[4]` is odd, so `r39-transplant-claw` trial 0 asserts the claw equation through the even-branch formula of `F` and passes the pair as `claw(u, a0)` with check mode off; the forced id-exhaustion run of `T4_EXP` starts at `2^20 - 2000`, as in 0b2616e3; the lag-1 autocorrelation test is `|r| sqrt(n) < 3`, as in our 2b4af365.")
else:
    r('this entry replaces its advice with our re-signed 39-step pair (Section 2.1, Appendix C)', 'this entry replaces its advice with our re-signed 39-step pair (Section 2.1, Appendix C)')
    r("with the message-schedule signs of rows `W11` and `W12` re-chosen (found by the W9/W11 wiggle search);", "with the message-schedule signs of rows `W9` and `W11` re-chosen;")
    r("(The advice pair's own `W1` is even, so `r39-transplant-claw` trial 0 checks the claw equation through both branch formulas of `F` with check mode off.)",
      "(`r39-transplant-claw` trial 0 checks the claw equation `fstep(a0) = s0(u) - u` of the advice pair directly and runs the filters with check mode off, as in our 2b4af365.)")
    r('with rows W11 and W12 re-signed (proof Section 12, Appendix C)', 'with rows W9 and W11 re-signed (proof Section 12, Appendix C)')
    r('of ePrint 2026/1120 with rows W11 and W12 re-signed (chaining value', 'of ePrint 2026/1120 with rows W9 and W11 re-signed (chaining value')
    r("the advice's own `W1` is even, so `r39-transplant-claw` trial 0 asserts the claw equation `fstep(a0) = s0(u) - u` directly and runs the filters with check mode off; the forced id-exhaustion run of `T4_EXP` starts at `2^20 - 1998` (at `2^20 - 2000` it no longer stops inside a partly restarted hit group); the lag-1 autocorrelation test is `|r| sqrt(n) < 3` (observed `0.0459` for `W17[0]` on 3,318 groups, 2.6 standard errors, disclosed).",
      "`r39-transplant-claw` trial 0 asserts the claw equation `fstep(a0) = s0(u) - u` directly and runs the filters with check mode off, as in our 2b4af365; the forced id-exhaustion run of `T4_EXP` starts at `2^20 - 2000`, as in 0b2616e3; the lag-1 autocorrelation test is `|r| sqrt(n) < 3`, as in our 2b4af365.")
r('the chi-square values `268.01` and `280.2`, `kernel_records 731`)', 'the chi-square values `%s` and `%s`, `kernel_records %s`, the group count `%s` of `serve()`)' % (V['c17'], V['c18s'], V['krec'], V['nG']))

# tail cross-check sentence of claim H2 (70 runs exist only for 7111)
H2_OLD = ("Cross-check on this advice: 56 further runs of the same replica (ids r39-tail-15..70, seeds by the organizer's public derivation rule) give, pooled with the 14, 31,570 verified hits in 229,376,000 proposals, "
          "linear 99.9% bound -74.4578 and class-specific 99% bound -74.4669, both above the declared -74.52; runs 15..70 alone have mean -74.4113, so the 14 public runs were about 0.07 bit favourable, which the declared value absorbs. ")
P70 = json.load(open('pool70_%s.json' % TAG))
both = float(P70['par99']) > float(QD)
r(H2_OLD, ("Cross-check on this advice: 56 further runs of the same replica (ids r39-tail-15..70, seeds by the organizer's public derivation rule) give, pooled with the 14, %s verified hits in 229,376,000 proposals, "
           + ("linear 99.9%% bound %s and class-specific 99%% bound %s, both above the declared %s; " if both else "linear 99.9%% bound %s above the declared %s and class-specific 99%% bound %s, %.4f below it (disclosed); ")
           + "runs 15..70 alone have mean %s, so the 14 public runs were about %s bit favourable, which the declared value absorbs. ")
  % (((P70['hits'], P70['lcb999'], P70['par99'], QD) if both else (P70['hits'], P70['lcb999'], QD, P70['par99'], float(QD) - float(P70['par99'])))
  + (P70['mean56'], P70['fav'])))
# claim H2 extrapolation must stay <= 2000 characters: the published-pair comparison (not required to pass) is cut
r("For comparison, 0b2616e3's 14 runs of the same replica on the published Table 23 pair give 3,365 verified hits and a linear 99.9% bound of -75.4601 (declared -75.47). ", '')
R[:] = [(a, b) for a, b in R if b is not None]

# ---------- Appendix C (both copies in the template) ----------
ch = open(CH[TAG]).read().splitlines()
cv = [l for l in ch if l.startswith('CV ')][0][3:].strip(); mm = [l for l in ch if l.startswith('M  ')][0][3:].strip(); mp = [l for l in ch if l.startswith('MP ')][0][3:].strip()
crows = '\n'.join(l.strip() for l in ch if re.match(r'^\s*\d+ A:', l))
tch = open('../pkg_r39_best_work/char.txt').read().splitlines()
tcv = [l for l in tch if l.startswith('CV ')][0][3:].strip(); tmm = [l for l in tch if l.startswith('M  ')][0][3:].strip(); tmp_ = [l for l in tch if l.startswith('MP ')][0][3:].strip()
trows = '\n'.join(l.strip() for l in tch if re.match(r'^\s*\d+ A:', l))
r('cv `%s`;\nM `%s`;\nM\' equal to M except words 8 to 12: `%s`.' % (tcv, tmm, ' '.join(tmp_.split()[8:13])), 'cv `%s`;\nM `%s`;\nM\' equal to M except words 8 to 12: `%s`.' % (cv, mm, ' '.join(mp.split()[8:13])))
assert mm.split()[:8] == mp.split()[:8] and mm.split()[13:] == mp.split()[13:]
r('```\n%s\n```' % trows, '```\n%s\n```' % crows)
if S108:
    r("Only the message-schedule rows `W11` and `W12` differ from the published Table 21/23 characteristic; every A and E state row is the published one, so the condition count",
      "Every signed row, state and message schedule, is the published Table 21/23 characteristic's (this is a second pair of that characteristic), so the condition count")
else:
    r("Only the message-schedule rows `W11` and `W12` differ from the published Table 21/23 characteristic;", "Only the message-schedule rows `W9` and `W11` differ from the published Table 21/23 characteristic;")

# ---------- apply ----------
def apply(t, label):
    olds = sorted({a for a, _ in R}, key=len, reverse=True); M = dict(R)
    rx = re.compile('|'.join(re.escape(a) for a in olds)); cnt = {}
    def f(m): cnt[m.group(0)] = cnt.get(m.group(0), 0) + 1; return M[m.group(0)]
    return rx.sub(f, t), cnt
TOT = {}
def doit(rel, isjson):
    t = open(os.path.join(TP, rel), encoding='utf-8').read(); t2, cnt = apply(t, rel)
    for k, v in cnt.items(): TOT[k] = TOT.get(k, 0) + v
    if isjson: json.loads(t2)
    return t2
out = {}
for rel, isj in (('sha256/proof.md', 0), ('sha256/claim.json', 1), ('sha256/experiments/manifest.json', 1)):
    out[rel] = doit(rel, isj)
# proof Appendix A rows
t = out['sha256/proof.md']
m = re.search(r'(\| window seed .*?\n\| ---: .*?\n)((?:\| \d+ \|.*\n)+)', t)
t = t[:m.start(2)] + '\n'.join(V['appA']) + '\n' + t[m.end(2):]
out['sha256/proof.md'] = t
c = json.loads(out['sha256/claim.json']); c['claim']['time_log2'] = float(t3)
out['sha256/claim.json'] = json.dumps(c, indent=2, ensure_ascii=False) + '\n'
miss = [a for a, _ in R if a not in TOT]
print('replacements applied:', sum(TOT.values()), '| literals used:', len(TOT), 'of', len(R))
for a in miss: print('MISS(proof/claim/manifest) |', a[:110].replace('\n', ' '))
for rel, t in out.items():
    open(os.path.join(NP_, rel), 'w', encoding='utf-8', newline='\n').write(t); print(rel, len(t.encode()))
json.dump({'V': {k: v for k, v in V.items() if k != '_tq'}, 'miss': miss}, open('xform_%s.json' % TAG, 'w'), indent=0, default=str)
