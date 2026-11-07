"""Build all wasm modules with the user-level wasi-sdk clang (toolchain/). Memory: max 16 pages."""

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

import subprocess, os, sys, glob
H = _hca_public_path_text('__HCA_WORKSPACE__/research/tools/vm1mib')
CC = glob.glob(os.path.join(H, "toolchain", "wasi-sdk-*", "bin", "clang.exe"))[0]
GEN = os.path.join(H, "..", "..", "sha3r6_gap", "ls1", "gen.c")

def cc(src, out, exports, initial_pages=None, stack=32768, extra=(), max_pages=29):
    """initial_pages=None: the linker picks the minimum (static data + stack, rounded up to pages), so the
    final memory.size is the true page footprint; link fails if that exceeds 16 pages."""
    cmd = [CC, "--target=wasm32", "-O2", "-nostdlib", "-ffreestanding", "-fno-builtin",
           "-Wl,--no-entry", "-Wl,--stack-first", f"-Wl,-z,stack-size={stack}",
           *([f"-Wl,--initial-memory={initial_pages*65536}"] if initial_pages else []), f"-Wl,--max-memory={max_pages*65536}",
           *[f"-Wl,--export={e}" for e in exports], *extra, "-o", out, src]
    r = subprocess.run(cmd, capture_output=True, text=True)
    print(("OK  " if r.returncode == 0 else "FAIL") + " " + os.path.basename(out), r.stderr.strip()[:2000])
    return r.returncode == 0

if __name__ == "__main__":
    T = lambda p: os.path.join(H, p)
    cc(T("tests/mem.c"), T("tests/mem.wasm"), ["touch"], initial_pages=1, stack=16384)
    cc(T("tests/loop.c"), T("tests/loop.wasm"), ["addloop"], initial_pages=1, stack=16384)
    cc(T("tests/keccak.c"), T("tests/keccak.wasm"), ["sha3_256_nr", "in_ptr", "out_ptr"], initial_pages=1, stack=16384)
    # a deliberately bad module: max 17 pages (the harness must refuse it)
    subprocess.run([CC, "--target=wasm32", "-O2", "-nostdlib", "-Wl,--no-entry", "-Wl,--export=addloop",
                    "-Wl,--max-memory=" + str(17*65536), "-o", T("tests/bad17.wasm"), T("tests/loop.c")])
    subprocess.run([sys.executable, T("ls1port/make_port.py"), GEN, T("ls1port/gen_wasm.c")])
    W = ["-Wno-everything"]
    # DEFAULT LS1 VM build: MAXN=32768 (set in gen_wasm.c by make_port.py)
    cc(T("ls1port/gen_wasm.c"), T("ls1port/gen_wasm.wasm"), [], extra=W)
    # gen.c as written (MAXN 65535, 1,073,744 B static): expected to FAIL to link into 16 pages; kept as evidence
    cc(T("ls1port/gen_wasm.c"), T("ls1port/gen_asis.wasm"), [], extra=W + ["-DMAXN=65535"])
