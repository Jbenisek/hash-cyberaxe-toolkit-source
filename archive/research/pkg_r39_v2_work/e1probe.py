import sys, importlib.util
sp = importlib.util.spec_from_file_location("j", sys.argv[1]); J = importlib.util.module_from_spec(sp); sp.loader.exec_module(J)
A = J.Attack(win=1 << 20, check=True); A.window_setup(cv=J.CV_PUB)
a0, u = J.BA[4], J.MP_PUB[1]
cw, eb, c0, c1, c4, c5 = A.c; e0 = (a0 + eb) & J.M
print("even-branch claw eq", (cw + J.S0(a0) + J.MAJ(a0, c0, c1) + J.S1(e0) + J.CH(e0, c4, c5) - a0) & J.M == (J.s0(u) - u) & J.M, "u odd", u & 1, "a0 odd", a0 & 1)
A.check = False; o0 = A.m.o; r = A.claw(u, a0); A.check = True
W1m, W2m = A.pairs_found[0][1:3] if r == 1 else (None, None)
print("r", r, "f9", A.st["f9"], "f8", A.st["f8"], "w17", A.st["w17"], "pair_is_advice", int(W1m == J.MP_PUB and W2m == J.M_PUB), "krec", len(A.ks[0]["recs"]), "claw_ops", A.m.o - o0, "blk", sum(A.m.blk.values()))
