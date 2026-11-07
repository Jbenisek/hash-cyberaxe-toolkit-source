"""Builds gen.wasm from gen.c (clang -Os, wasm32, 2 KiB shadow stack, max 16 pages), runs it in the 1 MiB VM, compares with the Python reference, counts the
instructions of the compiled generator, and writes cport.json for build_all.py.   usage (Windows python): python -B make_cport.py"""

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

import sys, os, json, subprocess, glob
H = os.path.dirname(os.path.abspath(__file__))
V = _hca_public_path_text('__HCA_WORKSPACE__/research/tools/vm1mib')
subprocess.run([sys.executable, "-B", os.path.join(H, "build_gen.py"), "2048", "-Os"], check=True)
out = subprocess.run([sys.executable, "-B", os.path.join(H, "run_gen.py")], capture_output=True, text=True, check=True).stdout
res = json.loads(out)
OD = glob.glob(os.path.join(V, "toolchain", "wasi-sdk-*", "bin", "llvm-objdump.exe"))[0]
dis = subprocess.run([OD, "-d", os.path.join(H, "gen.wasm")], capture_output=True, text=True, check=True).stdout
import re
ninstr = sum(1 for l in dis.split("\n") if re.match(r"^\s*[0-9a-f]+:\s", l))
info = res["info"]
src = open(os.path.join(H, "gen.c"), encoding="utf-8").read()
scratch = info["sz_uses"] + info["sz_state"] + 2048 + 68
static_total = info["sz_code"] + info["sz_ctr"] + scratch
c = dict(src_bytes=len(src.encode()), instructions=info["ninst"], registers=info["nreg"], nodes=info["nodes"], calls=info["calls"],
         static_total=static_total, code_region=info["sz_code"], counters=info["sz_ctr"], uses=info["sz_uses"], state=info["sz_state"], scratch=scratch,
         fuel=res["fuel_used"], pages=res["memory_pages_max"], spare=1048576 - static_total, wasm_instructions=ninstr, wasm_bytes=os.path.getsize(os.path.join(H, "gen.wasm")),
         highest_nonzero_byte=res["highest_nonzero_byte"], sha256=res["sha256"],
         identical=bool(res["sha256_equal"] and res["instructions_equal"] and res["registers_equal"] and res["nodes_equal"] and res["calls_equal"] and res["q_equal"] and res["mismatching_lines"] == 0 and not res["trapped"]))
json.dump(c, open(os.path.join(H, "cport.json"), "w"), indent=1)
print(json.dumps(c, indent=1))
