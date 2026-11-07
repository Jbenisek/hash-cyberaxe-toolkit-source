"""Writes the run scripts of research/blake3_rR/b8rR (tm_run, stage_pre, stage_run, bld, rc_run) and org_summary_b8.py.  usage: python3 -B mkroll8_scripts.py R"""
import sys, os
R = int(sys.argv[1]); HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.abspath(os.path.join(HERE, "..", "blake3_r%d" % R, "b8r%d" % R)); P = "research/blake3_r%d/b8r%d" % (R, R)
W = 'historical-sources/~~Projects/~HashSmash/workspace'
def w(f, t): open(os.path.join(D, f), "w", encoding="utf-8", newline="\n").write(t)
w("tm_run.sh", """cd '%s/%s/pkg/blake3/experiments'
( ulimit -v 2000000
nice -n 10 python3 -B - <<'PY'
import sys, time, json, hashlib
sys.dont_write_bytecode = True
import bsrho as b
seeds = [hashlib.sha256(("stats/%%d" %% i).encode()).hexdigest() for i in range(256)]
t=time.time(); b.serve({"experiment_id": "bsrho-n18", "trials": [{"trial": i, "seed": s} for i, s in enumerate(seeds)]}); t18=time.time()-t
t=time.time(); b.serve({"experiment_id": "proj-k0-w256", "trials": [{"trial": i, "seed": s} for i, s in enumerate(seeds)]}); t21=time.time()-t
json.dump({"t18": "%%.1f" %% t18, "t21": "%%.1f" %% t21}, open("../../../timing.json", "w")); print(t18, t21)
PY
)
""" % (W, P))
stage = """export PATH="$HOME/.local/bin:$HOME/.bun/bin:$PATH" NO_COLOR=1
cd %(W)s
nice -n 10 bash research/launch/slotstage/slotstage_pareto.sh B3R%(R)dC%(PRE)s blake3 %(R)d %(P)s/pkg/blake3 %(P)s/pkg/submission-note.md pos_b3r4d 2>&1 | tail -8
S=~/hashsmash/yukon/pos_b3r%(R)dc%(pre)s/pareto
cp %(P)s/pkg/dependencies.json $S/dependencies.json
cd $S
date; time nice -n 10 python3 -B ../scripts/pareto_pipeline.py intake --family blake3 2>&1 | tail -3
cat .yukon/work/tracks/blake3-pareto/pareto-outcome.json; echo
cp .yukon/work/tracks/blake3-pareto/experiment-report.json '%(W)s/%(P)s/%(rep)s'
sha256sum STAGED.sha256 dependencies.json
rm -rf __pycache__
date
"""
w("stage_pre.sh", stage % dict(W=W, R=R, P=P, PRE="PRE", pre="pre", rep="organizer_report_pre.json"))
w("stage_run.sh", stage % dict(W=W, R=R, P=P, PRE="", pre="", rep="organizer_report_b8r%d.json" % R))
w("bld.sh", """cd '%s/%s'
( ulimit -v 2500000; nice -n 10 python3 -B build_all8.py 2>&1 | tail -12 )
date
""" % (W, P))
w("rc_run.sh", """cd '%s/research/tools'
nice -n 10 python3 -B rulecheck/rulecheck.py ../blake3_r%d/b8r%d/pkg/blake3 2>&1 | cut -c1-260 | head -120
echo "=== prefile"
cd '%s/research/launch'
nice -n 10 python3 -B prefile_check.py ../blake3_r%d/b8r%d/pkg 2>&1 | cut -c1-220 | tail -40
""" % (W, R, R, W, R, R))
t = open(os.path.join(D, "org_summary_b8.py"), encoding="utf-8").read()
t = t.replace("json.load(open('organizer_report_b8.json'))", "json.load(open(sys.argv[1]))").replace("import json\n", "import json, sys\n", 1)
open(os.path.join(D, "org_summary_b8.py"), "w", encoding="utf-8", newline="\n").write(t)
print("ok", D)
