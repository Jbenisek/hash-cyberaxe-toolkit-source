# t4at.py R39JOINT OFF : the T4 tuple of trial 4 with the id-exhaustion start at 2^20 - OFF (stop_grp reported)
import sys, types, json
src = open(sys.argv[1]).read(); off = int(sys.argv[2])
assert src.count("C.idc0=(1<<20)-1998") == 1
M2 = types.ModuleType("r39j2"); exec(compile(src.replace("C.idc0=(1<<20)-1998", "C.idc0=(1<<20)-%d" % off), "r39j2", "exec"), M2.__dict__)
sd = 7466204727408384999; M2.T4_EXP = (0, None)
t = M2._t4(sd); C = M2.Attack(win=1 << 22, seed=sd, check=True); C.idc0 = (1 << 20) - off; C.run_window()
print(json.dumps({"off": off, "stop_grp": C.st.get('stop_grp', 0), "T4": [t[k] for k in ("distinct_claws","raw_claws","dp_hits","matches","stage2_iterations","parks","resumes","cuts","ops","blk_census","drops","idc_stop_iteration","idc_stop_stage2_iterations")]}))
