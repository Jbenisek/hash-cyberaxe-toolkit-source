s = open('ledger38.orig.py').read()
def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (s.count(old), old[:70])
    s = s.replace(old, new)
rep("# ledger38.py - the exact ledger of the r38 variant-table attack, derivative R38d (Appendix C).  ledger38.py of the base\n# package with four inputs added:",
    "# ledger38.py - the exact ledger of the r38 variant-table attack, derivative R38L (Appendix C).  ledger38.py of aa0496d3 with the\n# inputs below changed (C.2).  Of the base's four added inputs:")
rep("# is an executed-operation count of the counted programs (runs/costs.json, runs/pre1.json, runs/pre2.json); probabilities are exact rationals except\n# q3_model and delta.  With --base it is ledger38.py of 37742a53 (NGW = 32, ESZ = 3, no N2) and reproduces 2^71.695220.",
    "# is an executed-operation count of the counted programs (runs/costs.json, runs/pre1.json, runs/pre2.json: selftest item 4 of experiments/vt38.py,\n# t_pre1.py, t_pre_d.py); probabilities are exact rationals except q3_model and delta.  Every count of a loop pass includes its loop control.\n# With --base it is ledger38.py of 37742a53 (NGW = 32, ESZ = 3, no N2, the old pass keys of pre2.json) and reproduces 2^71.695220.")
rep("#   python3 ledger38.py [--base] [--q3 -101.5] [--delta 1] [--eps-log2 -4]", "#   python3 ledger38.py [--base] [--q3 -101.5] [--delta 0.564] [--eps-log2 -4]")
# pre_ops
rep("""    t['P6_zero'] = NB * (1 << 64) * 4
    entries = SR * ngw * W32                                         # (Y, variant, g) triples = entries of all tables
    t['P6_count'] = SR * W32 * (p2['P6_COUNT'] + 3) + SR * 16
    t['P6_fill'] = SR * W32 * (p2['P6_FILL'] + 3) + SR * 16
""", """    entries = SR * ngw * W32                                         # (Y, variant, g) triples = entries of all tables
    if 'P6_ZERO16' in p2:                                            # R38L bodies: 16 headers per zero iteration; the Y loop (2^32 iterations per variant) with its control inside the count
        t['P6_zero'] = NB * ((1 << 64) // 16) * p2['P6_ZERO16']     # and fill iterations, and the per-variant overhead (list loads, A1, both segment setups, guard, list-loop branch) measured
        t['P6_count'] = SR * (W32 * p2['P6_COUNT_IT'] + p2['P6_COUNT_VAR'])
        t['P6_fill'] = SR * (W32 * p2['P6_FILL_IT'] + p2['P6_FILL_VAR'])
    else:                                                            # the bodies of the base: 4 operations per header, loop control 3 per (Y, variant), 16 per variant
        t['P6_zero'] = NB * (1 << 64) * 4
        t['P6_count'] = SR * W32 * (p2['P6_COUNT'] + 3) + SR * 16
        t['P6_fill'] = SR * W32 * (p2['P6_FILL'] + 3) + SR * 16
""")
rep("def ledger(q3_log2=-101.5, delta=Fr(1),", "def ledger(q3_log2=-101.5, delta=Fr(141, 250),")
rep("out = dict(q3_log2=q3_log2, S_log2", "out = dict(q3_log2=q3_log2, delta=float(delta), S_log2")
rep("ap.add_argument('--delta', type=float, default=1.0)", "ap.add_argument('--delta', type=float, default=0.564)")
open('ledger38.py', 'w', newline='\n').write(s)
