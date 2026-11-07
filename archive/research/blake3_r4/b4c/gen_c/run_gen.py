"""Run gen.wasm in the 1 MiB VM and compare with the Python reference (ref_program.txt, ref_summary.txt)."""

# Publication path adapter: resolve data paths from the extracted source tree.
def _hca_public_path_text(value):
    if "__HCA_WORKSPACE__/" not in value:
        return value
    import os as _hca_os
    from pathlib import Path as _hca_Path
    root = _hca_os.environ.get("HASHCYBERAXE_WORKSPACE")
    if root is None:
        here = _hca_Path(__file__).resolve().parent
        root = next((str(p) for p in (here, *here.parents) if (p / "research").is_dir()), None)
    if root is None:
        raise FileNotFoundError("Extract the research source tree, or set HASHCYBERAXE_WORKSPACE to its archive directory.")
    return value.replace("__HCA_WORKSPACE__/", str(_hca_Path(root).resolve()).replace("\\", "/") + "/")

import sys, os, struct, json, hashlib
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/tools/vm1mib'))
from vm1mib import run, public
H = os.path.dirname(os.path.abspath(__file__))
wasm = os.path.join(H, sys.argv[1] if len(sys.argv) > 1 else "gen.wasm")
r = run(wasm, "run", [])
pub = public(r)
inst, store, mem = r["_inst"], r["_store"], r["_mem"]
ex = inst.exports(store)
ip, cp = ex["info_ptr"](store), ex["code_ptr"](store)
raw = bytes(mem.read(store, ip, ip + 9 * 4 + 32))
f = struct.unpack("<9I", raw[:36]); q = raw[36:68]
info = dict(zip("ninst nreg nodes calls err sz_code sz_ctr sz_uses sz_state".split(), f))
ref = dict(l.split() for l in open(os.path.join(H, "ref_summary.txt")))
code = bytes(mem.read(store, cp, cp + info["ninst"] * 36))
lines = []
for k in range(info["ninst"]):
    rec = code[36 * k:36 * k + 36]
    d, a, b = struct.unpack("<HHH", rec[1:7])
    assert not any(rec[7:]), "nonzero pad in record %d" % k
    lines.append("%s %d %d %d" % (chr(rec[0]), d, a, b))
reflines = open(os.path.join(H, "ref_program.txt")).read().split("\n")
if reflines and reflines[-1] == "": reflines.pop()
mism = [i for i in range(max(len(lines), len(reflines))) if i >= len(lines) or i >= len(reflines) or lines[i] != reflines[i]]
qhex = format(int.from_bytes(q, "little"), "064x")
txt = "\n".join(lines) + "\n"
res = {
  "run_result": pub["result"], "trapped": pub["trapped"], "trap": pub["trap"], "fuel_used": pub["fuel_used"],
  "declared_min_pages": pub["declared_min_pages"], "declared_max_pages": pub["declared_max_pages"], "memory_pages_max": pub["memory_pages_max"],
  "highest_nonzero_byte": pub["highest_nonzero_byte"], "info": info,
  "instructions_equal": info["ninst"] == int(ref["instructions"]), "registers_equal": info["nreg"] == int(ref["registers"]),
  "nodes_equal": info["nodes"] == int(ref["nodes"]), "calls_equal": info["calls"] == int(ref["generator_calls"]),
  "q_hex": qhex, "q_equal": qhex == ref["q_hex"],
  "sha256": hashlib.sha256(txt.encode()).hexdigest(), "sha256_equal": hashlib.sha256(txt.encode()).hexdigest() == ref["sha256"],
  "ref_lines": len(reflines), "c_lines": len(lines), "mismatching_lines": len(mism), "first_mismatch": mism[:5],
}
print(json.dumps(res, indent=1))
