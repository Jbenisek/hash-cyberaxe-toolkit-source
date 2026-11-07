s = open('t_pre_d.py').read()
def rep(old, new):
    global s
    assert s.count(old) == 1, old[:60]
    s = s.replace(old, new)
rep('''# t_pre_d.py - the changed preprocessing bodies of vtpre.py as counted code, against their definitions; writes
# runs/pre1.json and runs/pre2.json (the base values with LIVE_ops, LIVE_g, P5_SETUP, P5_APPEND, P6_COUNT, P6_FILL
# re-measured by executing the bodies).  usage: t_pre_d.py <dir of vt38.py> <runs dir>''',
'''# t_pre_d.py - the changed preprocessing bodies of vtpre.py as counted code, against their definitions; writes
# runs/pre1.json and runs/pre2.json (the base values of P1..P4 with LIVE_ops and LIVE_g; every P5 and P6 value is the count of an
# executed body: P5 setup, body, append and loop, the P6 zero, count and fill iterations and their per-variant overheads, the prefix).
# usage: t_pre_d.py <dir of vt38.py> <runs dir>''')
rep("app.append(m.ops - setup_ops - body)", "app.append(m.ops - setup_ops - body); bodies.append(body)")
rep("setup_ops = None; app = []; nvalid = 0; badw = 0", "setup_ops = None; app = []; bodies = []; nvalid = 0; badw = 0")
rep("""print('P5: setup', setup_ops, '| valid candidates', nvalid, 'list words != (c7 + 2^32, mkent fields, c9x):', badw, '| append ops', sorted(set(app)))
assert badw == 0 and nvalid >= 6 and len(set(app)) == 1
""", """a = Asm(); a('add', 'r', 'r', 1); a('bne', 'r', 'r1', 'S'); a.L('S'); p5_loop = execute(a, dict(r=5, r1=9)).ops
print('P5: setup', setup_ops, '| valid candidates', nvalid, 'list words != (c7 + 2^32, mkent fields, c9x):', badw, '| append ops', sorted(set(app)), '| body ops (valid candidates)', sorted(set(bodies)), '| loop control', p5_loop)
assert badw == 0 and nvalid >= 6 and len(set(app)) == 1 and len(set(bodies)) == 1
""")
i = s.index("# ---- P6 count and fill on a toy")
s = s[:i] + open('_tail_p6.txt').read()
open('t_pre_d.py', 'w', newline='\n').write(s)
