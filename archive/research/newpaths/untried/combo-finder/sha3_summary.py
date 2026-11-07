"""Summarise sha3_ldconn.py JSON lines per family: min/median/max of the per-stage numbers."""
import sys, json, statistics as st
rows = [json.loads(l) for l in open(sys.argv[1]) if l.startswith('{')]
fam = {}
for r in rows:
    if 'family' in r:
        fam.setdefault(r['family'], []).append(r)
    else:
        print('INFO', r)
keys = ['delta_src_weight', 'r1_rank', 'r1_dim', 'r2_rank', 'r2_dim', 'r2_delta_weight_at0', 'r2_delta_colparity_weight',
        'r2_theta3_out_weight', 'r2_constant_check_distinct', 'r3_rank', 'r3_dim', 'r3_delta_weight_at0',
        'r4_mean_weight', 'r4_max_bias', 'r5_mean_weight', 'r5_max_bias', 'r6_mean_weight', 'r6_max_bias', 'r6_const0_bits']
for f, rs in fam.items():
    print('== family', f, 'n =', len(rs))
    for k in keys:
        vals = [r[k] for r in rs if r.get(k) is not None]
        if vals:
            print('  %-28s min %s  median %s  max %s' % (k, min(vals), st.median(vals), max(vals)))
