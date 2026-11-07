# ledstats.py LEDDIR : per-claw categories/events over the windows (proof Section 5 table and event line)
import json, glob, sys
W=[json.load(open(f))[0] for f in sorted(glob.glob(sys.argv[1]+"/win_*.json"))]
C=sum(w["distinct_claws"] for w in W); T=sum(w["ops"] for w in W)
cat={}
for w in W:
    for k,v in w["cat"].items(): cat[k]=cat.get(k,0)+v
print("claws",C,"ops",T,"opc %.1f"%(T/C), "sumcat==ops", sum(cat.values())==T)
for k,v in sorted(cat.items(), key=lambda x:-x[1]): print("  %-14s %.1f %.1f%%"%(k,v/C,100*v/T))
S=lambda k: sum(w[k] for w in W)
for k in ("hits","matches","opp","same","iters","s2iters","pairs","moves","drops","s2phases","raw","f9","f8","w17"): print("  ev %-8s %d %.4f/claw"%(k,S(k),S(k)/C))
print("  kernel %d..%d nreg max %d qmax %d s2phases/win %.1f"%(min(w["kernel_len"] for w in W),max(w["kernel_len"] for w in W),max(w["kernel_nreg"] for w in W),max(w["qmax"] for w in W),S("s2phases")/len(W)))
