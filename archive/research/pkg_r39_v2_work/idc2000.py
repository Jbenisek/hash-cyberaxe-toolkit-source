import sys, importlib.util
sp = importlib.util.spec_from_file_location("j", sys.argv[1]); J = importlib.util.module_from_spec(sp); sp.loader.exec_module(J)
sd = 7466204727408384999
for off in (2000,):
    C = J.Attack(win=1 << 22, seed=sd, check=True); C.idc0 = (1 << 20) - off; C.run_window()
    print(sys.argv[1][-40:], off, C.lim == 0 and C.idc == 1 << 20 and C.it < 1 << 14 and C.s2 is None and C.qn == 0, C.st.get('stop_grp', 0), C.it)
