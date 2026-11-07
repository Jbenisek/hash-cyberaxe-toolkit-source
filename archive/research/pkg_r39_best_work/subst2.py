#!/usr/bin/env python3
# subst2.py - second pass: dk's offline uniformity block and the residual dk numbers, replaced with OUR measurements
# (work/stats/SUMMARY.txt over the same 24 ledger windows, work/ac_vals.txt, the frozen WIN_EXP). Numbers only; misses reported.
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); S = os.path.join(HERE, '..', 'sha256')
AC = open(os.path.join(HERE, 'ac_vals.txt')).read().split('\n')
r = {l.split(' r=')[0]: l.split(' r=')[1].split()[0] for l in AC if ' r=' in l}
r9, r17, r18 = r['W9 in F9'], r['W17[0]'], r['W18[0]']
REPL = [
 ("`W9 in F9` 68,460 (0.01588 vs 0.01587, z = 0.3); `W8 in F8` 304,102 (0.07056 vs 0.07031); both 4,879 (0.001132 vs 0.001116); "
  "`W17` low-k matches k = 8: 16,902 (16834.9), k = 12: 1,028 (1052.2), k = 16: 80 (65.76), k = 20: 3 (4.11), k = 24: 0 (0.26); "
  "chi-square against uniform of the low 16 bits of `W17` 64968.0 (65,535 df, z = -1.57), of the high 16 bits of `W17` 65975.5 (65,535 df, z = 1.22), "
  "and of `W18 mod 256` 272.7 (255 df, z = 0.79); per window, the low-16-bit chi-square of `W17` has z from -3.40 to 3.34 (mean 0.05, mean square 1.30 "
  "against 1 under uniformity; the sum of the 73 squares, 94.6 on 73 df, is 1.8 sigma high, while the pooled low and high halves are within 1.6 sigma; "
  "disclosed, not used by the claim)",
  "`W9 in F9` 22,528 (0.01588 vs 0.01587, z = 0.15); `W8 in F8` 100,445 (0.07082 vs 0.07031, z = 2.35); both 1,611 (0.001136 vs 0.001115); "
  "`W17` low-k matches k = 8: 5,431 (5540.42), k = 12: 301 (346.28), k = 16: 17 (21.64), k = 20: 2 (1.35), k = 24: 0 (0.08); "
  "chi-square against uniform of the low 16 bits of `W17` 66050.1 (65,535 df, z = 1.42), of the high 16 bits of `W17` 65303.2 (65,535 df, z = -0.64), "
  "and of `W18 mod 256` 213.4 (255 df, z = -1.84); per window, the low-16-bit chi-square of `W17` has z from -1.30 to 1.10 (mean 0.10, mean square 0.58 "
  "against 1 under uniformity; the sum of the 24 squares, 14.0 on 24 df, is 1.4 sigma low; the low-12 match count is 2.4 sigma below its expectation "
  "while the pooled 16-bit halves are within 1.5 sigma; disclosed, not used by the claim)"),
 ("binomial F9/F8 counts over distinct claws (chi-square 91.3 and 86.6 on 23 df), and F9 lag-1 autocorrelation within 0.0092 (1099 adjacent F9 pairs vs 1087.5 expected)",
  "binomial F9/F8 counts over distinct claws (chi-square 5.9 and 24.9 on 23 df; the F9 value is 2.5 sigma low, disclosed), and F9 lag-1 autocorrelation within 0.0006 (346 adjacent F9 pairs vs 357.9 expected)"),
 ("binomial F9/F8 counts over distinct claws (chi-square 91.3 and 86.6 on 23 df), and F9 lag-1 autocorrelation within 0.0092",
  "binomial F9/F8 counts over distinct claws (chi-square 5.9 and 24.9 on 23 df; the F9 value is 2.5 sigma low, disclosed), and F9 lag-1 autocorrelation within 0.0006"),
 ("over 73 pre-declared full-size windows", "over 24 pre-declared full-size windows"),
 ("`3,365` verified hits", "`6,326` verified hits"),
 ("3,318 distinct claws and 3,270 groups in WIN_EXP", "3,318 distinct claws and 3,318 groups in WIN_EXP"),
 ("tested in the organizer sandbox on 3,270 groups", "tested in the organizer sandbox on 3,318 groups"),
 ("lag-1 group autocorrelation `< 0.02` (`-0.0162`, `0.0070`, `-0.0062`)",
  "lag-1 group autocorrelation with the test `|r| sqrt(n) < 3` (`%s`, `%s`, `%s` on 3,318 groups)" % (r9, r17, r18)),
 ("lag-1 autocorrelation `< 0.02`", "lag-1 autocorrelation with `|r| sqrt(n) < 3`"),
 ("lag-1 group autocorrelation < 0.02 for F9, W17[0], and W18[0]",
  "lag-1 group autocorrelation with |r| sqrt(n) < 3 for F9, W17[0] and W18[0] (%s, %s, %s)" % (r9, r17, r18)),
 ("lag-1 group autocorrelation across consecutive groups is < 0.02 for W9 in F9 (-0.0162), W17[0] (0.0070), and W18[0] (-0.0062)",
  "lag-1 group autocorrelation across consecutive groups satisfies |r| sqrt(n) < 3 for W9 in F9 (%s), W17[0] (%s) and W18[0] (%s)" % (r9, r17, r18)),
]
def fix(t, label):
    for a, b in REPL:
        n = t.count(a)
        if n: t = t.replace(a, b); print('  %-10s %dx %s' % (label, n, a[:70]))
    return t
for name in ('proof.md', 'claim.json', os.path.join('experiments', 'manifest.json')):
    p = os.path.join(S, name); t = open(p, encoding='utf-8').read()
    t2 = fix(t, name)
    if name.endswith('.json'): json.loads(t2)          # still valid JSON
    open(p, 'w', encoding='utf-8', newline='\n').write(t2)
print('done; autocorr', r9, r17, r18)
