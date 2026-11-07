import sys, hashlib, json
sys.dont_write_bytecode=True
import bsrho as b
e=sys.argv[1]
seeds=[hashlib.sha256(("t/%d"%i).encode()).hexdigest() for i in range(int(sys.argv[2]))]
r=b.serve({"experiment_id":e,"trials":[{"trial":i,"seed":s} for i,s in enumerate(seeds)]})
print(e, len(r["trials"]))
