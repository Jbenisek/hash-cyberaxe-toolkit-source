"""Isolated reproduction (organizer code only, read-only clone): does the organizer's experiment runner accept a python-message-pairs-v1
experiment for the Orchard target?  Needs Docker and the pinned image; the candidate program is run only inside the organizer's sandbox."""
import json, os, sys, traceback
CLONE = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'pareto_clone'))
sys.path.insert(0, CLONE)
from experiments import run_experiments, ExperimentLimits
from verifier.hash_functions import digest
stage = sys.argv[1]
manifest = json.load(open(os.path.join(stage, 'experiments', 'manifest.json')))
src = open(os.path.join(stage, 'experiments', 'replay.py'), 'rb').read()
try:
    rep = run_experiments(manifest, {'experiments/replay.py': src}, target_profile='poseidon-orchard-r1-prefix-v1', target_config_sha256='0' * 64,
                          digest_fn=lambda m: digest(m, 'poseidon-orchard', 1), limits=ExperimentLimits(trials=8))
    print('experiment ran:', json.dumps(rep)[:300])
except Exception:
    traceback.print_exc()
