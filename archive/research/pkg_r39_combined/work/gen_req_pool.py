import sys, json
sys.path.insert(0, '/root/hashsmash/yukon/scratch_dk_0b2616e3')
from experiments.runner import _trial_seed, _canonical, ExperimentLimits
TC = '76b4a93ecdbedd7590adb35005834807e1769475c675e4e0ed5af8c0e955419e'
sm = _canonical({"domain": "hashsmash-experiments-v1", "seed": "hashsmash-public-seed-v1", "holdout_nonce": None, "target_config_sha256": TC})
n = ExperimentLimits().trials
ids = ["r39-tail-%02d" % i for i in range(15, 71)]
out = sys.argv[1]
for e in ids:
    req = {"schema_version": 1, "experiment_id": e, "target_profile": "sha256-r39-prefix-v1", "trials": [{"trial": i, "seed": _trial_seed(sm, e, i)} for i in range(n)]}
    json.dump(req, open("%s/%s.json" % (out, e), "w"))
