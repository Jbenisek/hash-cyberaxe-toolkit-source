#!/bin/bash
# Reviewer (count and cost): the organizer's cost model file, read only (primitive operations, memory rule)
cd "$HOME/hashsmash/hash-smash-pkg7text" || exit 1
python3 - <<'PY'
import json
d = json.load(open("cost-models/collision-frontier-v5.json"))
print("primitive_operations:", d.get("primitive_operations"))
for k, v in d.items():
    if k not in ("primitive_operations", "computation_model", "reference_operation_costs") and len(str(v)) < 500:
        print(k, "::", str(v)[:480])
PY
