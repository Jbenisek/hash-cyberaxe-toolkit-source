cd ~/hashsmash/yukon/pos_b3r3pv
PYTHONDONTWRITEBYTECODE=1 nice -n 10 python3 -B - <<'PY'
import sys
sys.dont_write_bytecode=True
sys.path.insert(0,'.')
from pareto.targets import reference_cost
for r in (1,2,3,4,5,7):
    print(r, reference_cost('blake3', r))
PY
git status --short | head
