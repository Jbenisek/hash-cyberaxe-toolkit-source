"""rho.py digest == organizer verifier/poseidon.py digest at r = 23 on 24 inputs (WSL: python3 -B verify_digest.py <organizer root>)."""
import sys, os, random, importlib.util
sys.dont_write_bytecode = True
sys.path.insert(0, sys.argv[1])
from verifier.poseidon import digest as odig
spec = importlib.util.spec_from_file_location("rho", os.path.join(os.path.dirname(os.path.abspath(__file__)), "rho.py"))
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
rng = random.Random(23)
ins = [(0, 0), (1, 0), (m.P - 1, m.P - 1)] + [(rng.getrandbits(254), rng.getrandbits(254)) for _ in range(21)]
ok = sum(odig(a.to_bytes(32, "little") + b.to_bytes(32, "little"), 23) == m.digest(a, b).to_bytes(32, "little") for a, b in ins)
print(f"rho.py digest equals organizer digest at r=23 on {ok} of {len(ins)} inputs")
