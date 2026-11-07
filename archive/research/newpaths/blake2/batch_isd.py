"""Run a list of ISD configs sequentially, append one JSON line per config to the output file.
Usage: python -B batch_isd.py outfile "w,setting,objective,iters,seed" ..."""
import sys, json
sys.dont_write_bytecode = True
from isd import run

out = sys.argv[1]
for spec in sys.argv[2:]:
    w, s, o, it, sd = spec.split(",")
    r = run(int(w), s, o, int(it), int(sd))
    with open(out, "a") as fh:
        fh.write(json.dumps(r) + "\n")
    print(spec, r["best"], r["secs"], flush=True)
