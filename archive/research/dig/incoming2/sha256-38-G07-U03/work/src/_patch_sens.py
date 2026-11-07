s = open('sens38.orig.py').read()
def rep(old, new):
    global s
    assert s.count(old) == 1, old[:60]
    s = s.replace(old, new)
rep("row('claimed configuration (q3_model 2^-101.5, delta 1, A_C 2^70, A_S 2^60, DEV 2^60)')", "row('claimed configuration (q3_model 2^-101.5, delta 0.564, A_C 2^70, A_S 2^60, DEV 2^60)')")
rep("row('pair budget delta = 1/2', delta=Fr(1, 2))\nrow('pair budget delta = 1.5', delta=Fr(3, 2))",
    "row('pair budget delta = 0.56 (the limits rounded down)', delta=Fr(56, 100))\nrow('pair budget delta = 1/2', delta=Fr(1, 2))\nrow('pair budget delta = 1 (the budget of aa0496d3)', delta=Fr(1))\nrow('pair budget delta = 1.5', delta=Fr(3, 2))")
rep("row('without L0 (tables over all 32 words of G)', ngw=32, p2=dict(p2, P6_COUNT=205, P6_FILL=269))",
    "# the pass iterations scale with the words listed: 6 (count) and 10 (fill) operations per word of G\nrow('without L0 (tables over all 32 words of G)', ngw=32, p2=dict(p2, P6_COUNT_IT=p2['P6_COUNT_IT'] + 6 * 10, P6_FILL_IT=p2['P6_FILL_IT'] + 10 * 10))")
rep("p2=dict(p2, P5_SETUP=32, P5_BODY_MAX=58, P5_APPEND=28, P6_FILL=255, P6_PREFIX_NONEMPTY=14))",
    "p2=dict(p2, P5_SETUP=32, P5_BODY_MAX=58, P5_APPEND=28, P6_FILL_IT=p2['P6_FILL_IT'] + 22, P6_PREFIX_NONEMPTY=14))")
s = s.replace("# sens38.py - sensitivity of the derivative's exact ledger", "# sens38.py - sensitivity of the derivative's exact ledger")
open('sens38.py', 'w', newline='\n').write(s)
