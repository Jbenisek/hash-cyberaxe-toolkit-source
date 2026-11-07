#!/usr/bin/env python3
# freeze.py PKG_EXPERIMENTS_DIR REQ_DIR : every frozen sandbox value of r39joint.py recomputed for the staged advice
# (as the 2b4af365 build: WIN_EXP, T4_EXP with stop_grp == 1, chi-squares, kernel_records, e1 trial-0 dict, autocorr)
import sys, json, importlib.util
D, R = sys.argv[1], sys.argv[2]
sp = importlib.util.spec_from_file_location("r39joint", D + "/r39joint.py"); J = importlib.util.module_from_spec(sp); sp.loader.exec_module(J)
class ANY:
    def __eq__(s, o): return True
seeds = [int(t["seed"][:16], 16) for t in json.load(open(R + "/r39-window-small.json"))["trials"]]
res = {}
# --- e1 trial 0, both claw-call forms
adv = J.verify_advice_construction(); res["adv"] = adv
for form in ("tmpl", "dk"):
    try:
        A = J.Attack(win=1 << 20, check=True); A.window_setup(cv=J.CV_PUB)
        if form == "tmpl":
            a0, u = J.BA[4], J.MP_PUB[1]
            ok = int(a0 % 2 == 0 and J.fstep(a0, A.c) == (J.s0(u) - u) & J.M)
            A.check = False; o0 = A.m.o; r = A.claw(a0, u); A.check = True
        else:
            ok = -1; o0 = A.m.o; r = A.claw(J.MP_PUB[1], J.BA[4])
        W1m, W2m = A.pairs_found[0][1:3] if r == 1 else (None, None)
        res["e1_" + form] = {"claw_eq_assert": ok, "claw_returned_pair": r, "passed_f9": A.st["f9"], "passed_f8": A.st["f8"], "passed_w17": A.st["w17"],
          "pair_is_advice": int(W1m == J.MP_PUB and W2m == J.M_PUB), "kernel_records": len(A.ks[0]["recs"]), "claw_ops": A.m.o - o0, "blk_census": sum(A.m.blk.values())}
    except Exception as e:
        res["e1_" + form] = "ERR %r" % (e,)
res["W1_parity"] = J.MP_PUB[1] & 1; res["a0_parity"] = J.BA[4] & 1
res["sfs"] = int(J.compress(J.CV_PUB, J.MP_PUB) == J.compress(J.CV_PUB, J.M_PUB)); res["G16"] = "%08x" % J.G16; res["W17"] = "%08x" % J.W17PUB
# G16 fibre at idx 0 (as verify_advice_construction): the members and |G17(g)| per member
A0, E0, W0 = J.BA[:20], J.BE[:20], J.MP_PUB[:16]; A1, E1, W1 = J.CA[:20], J.CE[:20], J.M_PUB[:16]
g16, _ = J.solve_row_exact(A0, E0, W0, A1, E1, W1, 16); res["g16_set"] = ["%08x" % g for g in g16]
# --- e2 trials 0..3 (WIN_EXP) + hist/autocorr
J.WIN_EXP = {sd: ANY() for sd in seeds[:4]}
win = []
for i in range(4):
    o = J._e2(i, seeds[i]); win.append((o["distinct_claws"], o["distinct_groups"], o["dp_hits"], o["matches"], o["stage2_iterations"], o["raw_claws"],
        o["passed_f9"], o["passed_f8"], o["f8_all"], o["w17_low8"], o["w17_low12"], o["kernel_records"], o["ops"], o["generator_ops"], o["blk_census"]))
res["WIN_EXP"] = {str(seeds[i]): win[i] for i in range(4)}
G = J._G_SEQ; n = len(G); e = n / 256.0
res["nG"] = n; res["c17"] = round(sum((c - e) ** 2 / e for c in J._W17_HIST), 2); res["c18"] = round(sum((c - e) ** 2 / e for c in J._W18_HIST), 2)
ac = []
for k in range(3):
    xs = [g[k] for g in G]; m = sum(xs) / n; v = sum((x - m) ** 2 for x in xs)
    r = sum((xs[j] - m) * (xs[j + 1] - m) for j in range(n - 1)) / v; ac.append((round(r, 4), round(abs(r) * n ** 0.5, 2)))
res["autocorr"] = ac
# --- trial 4: id-exhaustion start with stop_grp == 1, then the T4 tuple
sd = seeds[4]; scan = {}
for off in [1998, 2000] + [x for x in range(1990, 2011) if x not in (1998, 2000)]:
    C = J.Attack(win=1 << 22, seed=sd, check=True); C.idc0 = (1 << 20) - off; C.run_window()
    ok = C.lim == 0 and C.idc == 1 << 20 and C.it < 1 << 14 and C.s2 is None and C.qn == 0
    scan[off] = (ok, C.st.get('stop_grp', 0), C.it, C.st['s2iters'])
    if ok and scan[off][1] == 1 and off in (1998, 2000): break
res["idc_scan"] = {str(k): v for k, v in scan.items()}
good = [k for k, v in scan.items() if v[0] and v[1] == 1]
off = 1998 if 1998 in good else (good[0] if good else None); res["idc_off"] = off
if off is not None:
    src = open(D + "/r39joint.py").read()
    J.T4_EXP = (0, None)
    import types
    # run _t4 with the chosen start: patch the literal through a wrapper module copy
    code = src.replace("C.idc0=(1<<20)-1998", "C.idc0=(1<<20)-%d" % off)
    M2 = types.ModuleType("r39j2"); exec(compile(code, "r39j2", "exec"), M2.__dict__); M2.T4_EXP = (0, None)
    t = M2._t4(sd); res["T4"] = [sd, [t[k] for k in ("distinct_claws","raw_claws","dp_hits","matches","stage2_iterations","parks","resumes","cuts","ops","blk_census","drops","idc_stop_iteration","idc_stop_stage2_iterations")]]
print(json.dumps(res))
