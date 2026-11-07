"""count.py - run the emitter only and print the exact instruction counts and the static length of every block kind."""
import json
import emit_b3z7 as X
from collections import Counter, defaultdict
code, labels, probes, g = X.build()
tag = Counter(c[4] for c in code)
parts = {}
parts["solver_rows_6_outcomes"] = sum(tag[k] for k in ("setup", "desc", "forced", "free", "leaf", "root"))
parts["entry_stubs_and_ledger(glob)"] = tag["glob"]
parts["context(39 lines + S2,w5,w12)"] = tag["context"]
parts["routine_of_step_3(found)"] = tag["found"]
d = defaultdict(list)
for k, i, n in g.stats:
    d[(k, i if k in ("forced", "free") and i in (9, 15, 20, 25, 29, 31) else "")].append(n)
blocks = {"%s%s" % (k, ("@%s" % i) if i != "" else ""): dict(count=len(v), static_min=min(v), static_max=max(v)) for (k, i), v in sorted(d.items(), key=str)}
nodes = sum(len(v) for (k, i), v in d.items() if k in ("forced", "free", "leaf"))
ops = Counter(X.OPS[c[0]] for c in code)
imm = max((abs(v) for c in code if X.OPS[c[0]] in ("ADDI", "XORI", "ANDI", "ORI", "LI", "SHLI", "SHRI") for v in (c[3] if X.OPS[c[0]] not in ("LI",) else c[2],)), default=0)
print(json.dumps(dict(total_instructions=len(code), by_block=dict(tag), parts=parts, static_nodes=nodes, block_static_lengths=blocks,
                      opcodes=dict(ops), registers_used=g.peak + 4, max_immediate_abs=imm, bytes_at_32=32 * len(code))))
